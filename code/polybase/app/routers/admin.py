# ============================================
# IMPORTS
# ============================================

import random
import string
import os
import pandas as pd
from fastapi.responses import FileResponse
from app.utils.openrouter_adapter import adapt_excel_to_table

import Levenshtein
import bcrypt
from fastapi import APIRouter, Depends, Request, HTTPException, status, Query
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db

# ============================================
# ROUTER INITIALIZATION
# ============================================

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ============================================
# MANAGEMENT OF IDENTIFIER PREFIXES
# ============================================
table_prefixes = {
    "Client": "CL",
    "Personnel": "P",
    "Projet": "PRJ",
    "Facture": "F",
    "Tache": "T",
    "Phase": "PH",
    "PlanificationCollaborateur": "PL",
    "PrestationCollaborateur": "PC",
    "Cout": "C",
    "ImportLog": "IMP",
    "Offre": "OFF",
    "HonoraireReparti": "HR",
    "ResponsableProjet": "P",
    "Collaborateur": "P",
    "Gerer": None,
    "ProjectionFacturation": "PF"
}

def generate_id(prefix, length=3):
    """Generates a unique business identifier from a prefix and a random number.
    Parameters:
    -----------
    prefix: str
        Prefix of the identifier (e.g. “CL”, “PRJ”, “T”).
    length: int, optional
        Length of the randomly generated numeric part (default: 3).
    Returns:
    --------
    str
        Concatenated identifier of type `prefix` + `random digits`, e.g.: “CL001”.
    Version:
    --------
    specification: Esteban Barracho (v.1 26/06/2025)
    implement: Esteban Barracho (v.1 26/06/2025)
    """
    num = ''.join(random.choices(string.digits, k=length))
    return f"{prefix}{num}"

# ============================================
# ADMIN ACCESS
# ============================================
def check_admin(user):
    """Verifies whether the authenticated user has administrative privileges.
    Parameters:
    -----------
    user: The current authenticated user object.
    Raises:
    -------
    HTTPException: If the user is not an administrator.
    Version:
    --------
    specification: Esteban Barracho (v.1 26/06/2025)
    implement: Esteban Barracho (v.1 26/06/2025)
    """
    if not getattr(user, "fonction", None) or user.fonction.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé à l'administrateur."
        )

# ============================================
# ADMIN HTML PAGE
# ============================================
@router.get("", response_class=JSONResponse)
async def admin_page(request: Request, user=Depends(get_current_user)):
    """Renders the admin page for users with administrative privileges.
    Parameters:
    -----------
    request (Request): FastAPI request instance.
    user: Authenticated user from session.
    Returns:
    --------
    TemplateResponse: Rendered admin.html template.
    Version:
    --------
    specification: Esteban Barracho (v.1 26/06/2025)
    implement: Esteban Barracho (v.1 26/06/2025)
    """
    check_admin(user)
    return templates.TemplateResponse("admin.html", {"request": request, "user": user})

# ============================================
# LIST OF TABLES
# ============================================
@router.get("/tables")
def get_tables(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Returns a list of all non-view tables in the database schema.
    Parameters:
    -----------
    db (Session): Database session.
    user: Authenticated admin user.
    Returns:
    --------
    list[str]: Names of all tables excluding views.
    Version:
    --------
    specification: Esteban Barracho (v.1 26/06/2025)
    implement: Esteban Barracho (v.1 26/06/2025)
    """
    check_admin(user)
    inspector = inspect(db.get_bind())
    tables = [t for t in inspector.get_table_names() if not t.startswith('Vue')]
    return tables

# ============================================
# TABLE STRUCTURE
# ============================================
@router.get("/table/{table}/structure")
def get_table_structure(table: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Retrieves the structure of a specific table, including types, nullability, and examples,
    and detects foreign key relationships for dynamic dropdowns.
    Parameters:
    -----------
    table (str): Name of the table to inspect.
    Db (Session): Database session.
    user: Authenticated admin user.
    Returns:
    --------
    list[dict]: Column metadata including foreign key target if applicable.
    Version:
    --------
    specification: Esteban Barracho (v.1.3 11/07/2025)
    implement: Esteban Barracho (v.1.3 11/07/2025)
    """
    check_admin(user)
    inspector = inspect(db.get_bind())
    fk_map = {}
    for fk in inspector.get_foreign_keys(table):
        if fk.get("constrained_columns") and fk.get("referred_table"):
            for col in fk["constrained_columns"]:
                fk_map[col] = fk["referred_table"]
    cols = []
    for c in inspector.get_columns(table):
        ex = "Exemple : "
        tpe = str(c["type"]).upper()
        if "VARCHAR" in tpe:
            ex += "abc123"
        elif "DATE" in tpe:
            ex += "2025-12-31"
        elif "DECIMAL" in tpe or "INT" in tpe:
            ex += "123"
        elif "ENUM" in tpe:
            ex += "Valeur possible : " + ",".join(map(str, c["type"].enums))
        elif "BOOLEAN" in tpe:
            ex += "0 ou 1"
        else:
            ex += tpe
        cols.append({
            "name": c["name"],
            "type": str(c["type"]),
            "nullable": c["nullable"],
            "maxLength": c.get("length", None),
            "precision": c.get("precision", None),
            "example": ex,
            "foreign_table": fk_map.get(c["name"])  # clé étrangère si détectée
        })
    return cols

# ============================================
# TABLE DATA
# ============================================
@router.get("/table/{table}")
def get_table_data(table: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Retrieves all records from the specified table (max 200 rows by design).
    Parameters:
    -----------
    table (str): Table name.
    db (Session): Active SQLAlchemy session.
    user: Authenticated admin user.
    Returns:
    --------
    list[dict]: List of records from the table.
    Version:
    --------
    specification: Esteban Barracho (v.1 26/06/2025)
    implement: Esteban Barracho (v.2 11/07/2025)
    """
    check_admin(user)
    if table == "Personnel":
        result = db.execute(text("SELECT * FROM Personnel WHERE fonction != 'admin'"))
    else:
        result = db.execute(text(f"SELECT * FROM `{table}`"))
    data = [dict(row) for row in result.mappings()]
    for row in data:
        if table == "Personnel" and "password" in row:
            row["password"] = "********"
    return data

# ============================================
# SAFE INSERTION
# ============================================
@router.post("/table/{table}")
def insert_row(table: str, row: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Inserts a new row securely into the specified table with optional ID generation.
    Parameters:
    -----------
    table (str): Table name to insert into.
    Row (dict): Dictionary of values to insert.
    Db (Session): Active database session.
    user: Authenticated admin user.
    Returns:
    --------
    dict: Confirmation message and generated ID if applicable.
    Version:
    --------
    specification: Esteban Barracho (v.1 26/06/2025)
    implement: Esteban Barracho (v.1 27/06/2025)
    """
    check_admin(user)
    inspector = inspect(db.get_bind())
    if table not in inspector.get_table_names():
        raise HTTPException(404, detail="Table inconnue")
    columns = {c["name"]: c for c in inspector.get_columns(table)}
    assert isinstance(columns, dict) and len(columns) > 0, f"Structure de la table `{table}` vide ou invalide"
    insert_row = {}
    # Forcer la détection de l'ID principal même si inspect échoue
    id_field = next((name for name, col in columns.items() if name.startswith("id_") and col.get("primary_key")), None)
    if not id_field:
        for fallback in ["id_" + table.lower(), f"id_{table}"]:
            if fallback in columns:
                id_field = fallback
                break
    prefix = table_prefixes.get(table)
    assert prefix is None or isinstance(prefix, str), f"Préfixe mal défini pour la table {table}"
    if id_field and prefix:
        # Vérifie unicité et regénère si existe déjà (boucle protection)
        for _ in range(10):
            new_id = generate_id(prefix)
            assert new_id.startswith(prefix), f"ID généré ne commence pas par le préfixe {prefix}"
            exists = db.execute(text(f"SELECT 1 FROM `{table}` WHERE `{id_field}` = :id"), {"id": new_id}).first()
            if not exists:
                insert_row[id_field] = new_id
                break
        else:
            raise HTTPException(500, detail="Impossible de générer un identifiant unique.")

    # INJECTION DES AUTRES CHAMPS (hors ID et password)
    for k, v in row.items():
        if k == id_field:
            continue  # Ne jamais prendre l'id fourni par le client (génération auto)
        if k not in columns:
            raise HTTPException(400, detail=f"Colonne inconnue: {k}")
        c = columns[k]
        if not c["nullable"] and (v is None or v == ""):
            raise HTTPException(400, detail=f"Champ requis manquant: {k}")
        typ = str(c["type"]).upper()
        if "INT" in typ or "DECIMAL" in typ:
            if v not in (None, "") and not str(v).replace(".", "", 1).isdigit():
                raise HTTPException(400, detail=f"Le champ {k} doit être numérique.")
        if c.get("length") and v and len(str(v)) > c["length"]:
            raise HTTPException(400, detail=f"Le champ {k} dépasse la longueur maximale ({c['length']})")
        # Hashage automatique pour le mot de passe
        if k == "password" and v:
            insert_row[k] = bcrypt.hashpw(v.encode(), bcrypt.gensalt()).decode()
        else:
            insert_row[k] = v if v not in ("", None) else None
    # CONSTRUCTION ET EXECUTION SQL
    keys = ", ".join([f"`{k}`" for k in insert_row])
    vals = ", ".join([f":{k}" for k in insert_row])
    sql = text(f"INSERT INTO `{table}` ({keys}) VALUES ({vals})")
    try:
        db.execute(sql, insert_row)
        db.commit()
        assert db.execute(text(f"SELECT 1 FROM `{table}` WHERE `{id_field}` = :id"),
                          {"id": insert_row.get(id_field)}).first(), "Échec de l'insertion, l’ID n’existe pas en base"
    except Exception as e:
        db.rollback()
        raise HTTPException(400, detail=f"Erreur lors de l’insertion : {e}")
    # Retourne l'identifiant généré (pour liaison côté client)
    return {"status": "ok", "id": insert_row.get(id_field)}

# ============================================
# GLOBAL LEVENSHTEIN SEARCH ON ALL TABLES
# ============================================
@router.get("/search_global")
def search_global(query: str = Query(..., min_length=1),db: Session = Depends(get_db),user=Depends(get_current_user)):
    """Performs a fuzzy Levenshtein search across all business tables.
    Parameters:
    -----------
    query (str): Search string (minimum 1 character).
    db (Session): Active database session.
    user: Authenticated admin user.
    Returns:
    --------
    list[dict]: Matching values with distance scores and metadata.
    Version:
    --------
    specification: Esteban Barracho (v.1 26/06/2025)
    implement: Esteban Barracho (v.1 27/06/2025)
    """
    check_admin(user)
    inspector = inspect(db.get_bind())
    results = []
    tables = [t for t in inspector.get_table_names() if not t.startswith('Vue')]
    for table in tables:
        # Prends max 200 lignes/table
        rows = db.execute(text(f"SELECT * FROM `{table}` LIMIT 200")).mappings().all()
        columns = [col["name"] for col in inspector.get_columns(table)]
        id_field = next((c for c in columns if c.startswith("id_")), None)
        for row in rows:
            for col in columns:
                value = row.get(col)
                if value is None:
                    continue
                score = Levenshtein.distance(query.lower(), str(value).lower())
                if score < 4:  # seuil : à ajuster selon tolérance
                    results.append({
                        "table": table,
                        "id": row.get(id_field),
                        "col": col,
                        "value": value,
                        "score": score,
                        "row": dict(row)
                    })
    results.sort(key=lambda r: (r["score"], r["table"], r["col"]))
    return results

# ============================================
# UPDATE OF AN ENTRY (PUT)
# ============================================
@router.put("/table/{table}/{id}")
def update_row(table: str, id: str, row: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Updates a record in a table based on its primary key.
    Parameters:
    -----------
    table (str): Table name to update.
    Id (str): Identifier of the row to update.
    Row (dict): Fields and values to modify.
    Db (Session): Active database session.
    user: Authenticated admin user.
    Returns:
    --------
    dict: Confirmation of update operation.
    Version:
    --------
    specification: Esteban Barracho (v.1 26/06/2025)
    implement: Esteban Barracho (v.1 27/06/2025)
    """
    check_admin(user)
    inspector = inspect(db.get_bind())
    if table not in inspector.get_table_names():
        raise HTTPException(404, detail="Table inconnue")
    pk = inspector.get_pk_constraint(table)
    assert "constrained_columns" in pk, f"Clé primaire introuvable pour la table `{table}`"
    id_field = pk['constrained_columns'][0] if pk['constrained_columns'] else None
    if not id_field:
        raise HTTPException(400, detail="Impossible de déterminer la clé primaire.")
    columns = {c["name"]: c for c in inspector.get_columns(table)}
    updates = []
    values = {}
    for k, v in row.items():
        if k == id_field:
            continue
        if k in columns:
            updates.append(f"`{k}` = :{k}")
            values[k] = v
    values["id"] = id
    assert updates, f"Aucune colonne valide fournie pour la mise à jour de `{table}`"
    sql = text(f"UPDATE `{table}` SET {', '.join(updates)} WHERE `{id_field}` = :id")
    try:
        db.execute(sql, values)
        db.commit()
        return {"status": "ok"}
    except Exception as e:
        db.rollback()
        raise HTTPException(400, detail=f"Erreur lors de la mise à jour : {e}")

# ============================================
# DELETING AN ENTRY (DELETE)
# ============================================
@router.delete("/table/{table}/{id}")
def delete_row(table: str, id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Deletes a row from a specified table based on primary key.
    Parameters:
    -----------
    table (str): Table name.
    Id (str): Identifier of the row to delete.
    Db (Session): Active database session.
    user: Authenticated admin user.
    Returns:
    --------
    dict: Confirmation message of successful deletion.
    Version:
    --------
    specification: Esteban Barracho (v.1 26/06/2025)
    implement: Esteban Barracho (v.2 11/07/2025)
    """
    check_admin(user)
    inspector = inspect(db.get_bind())
    if table not in inspector.get_table_names():
        raise HTTPException(404, detail="Table inconnue")
    pk = inspector.get_pk_constraint(table)
    id_field = pk['constrained_columns'][0] if pk['constrained_columns'] else None
    if not id_field:
        raise HTTPException(400, detail="Impossible de déterminer la clé primaire.")
    if table == "Personnel":
        fonction = db.execute(text("SELECT fonction FROM Personnel WHERE id_personnel = :id"), {"id": id}).scalar()
        if fonction == "admin":
            raise HTTPException(403, detail="Impossible de supprimer un administrateur via l’interface.")
    sql = text(f"DELETE FROM `{table}` WHERE `{id_field}` = :id")
    try:
        result = db.execute(sql, {"id": id})
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(404, detail="Aucune ligne supprimée")
        return {"status": "ok"}
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur DELETE {table}({id}): {e}")
        raise HTTPException(400, detail=f"Erreur lors de la suppression : {e}")

def detect_foreign_keys(table: str, db: Session):
    """Detects foreign key relationships for a given SQL table.
    This function inspects the provided table and identifies columns
    that are constrained as foreign keys, returning a mapping of
    local column names to their referenced (foreign) table names.
    Parameters:
    -----------
    table : str
        Name of the table to inspect for foreign key relationships.
    db : Session
        Active SQLAlchemy session used for schema inspection.
    Returns:
    --------
    dict
        Dictionary mapping constrained column names to the referenced table names.
        Example: {"id_client": "Client"}
    Version:
    --------
    specification: Esteban Barracho (v.1 26/06/2025)
    implement: Esteban Barracho (v.1.1 11/07/2025)
    """
    inspector = inspect(db.get_bind())
    fks = inspector.get_foreign_keys(table)
    assert isinstance(fks, list), "Les clés étrangères doivent être une liste"
    fk_map = {}

    for fk in fks:
        if fk.get("constrained_columns") and fk.get("referred_table"):
            for col in fk["constrained_columns"]:
                fk_map[col] = fk["referred_table"]
    return fk_map

# =============================================
# IMPORTATION & EXPORTATION D’UNE TABLE (EXCEL)
# =============================================
@router.get("/export/{table}")
def export_table(table: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """This route allows an administrator to export the contents
    of a specific table to an Excel file (.xlsx).
    Parameters:
    -----------
    table: str
        Name of the table to be exported.
    db: Session
        Injected SQLAlchemy session.
    user: User
        Currently logged-in user (verified as an administrator).
    Return:
    -------
    FileResponse
        Excel file containing the exported data.
    Version:
    --------
    specification: Esteban Barracho (v.1 12/07/2025)
    implement: Esteban Barracho (v.1 12/07/2025)
    """
    check_admin(user)
    result = db.execute(text(f"SELECT * FROM `{table}`")).mappings().all()
    df = pd.DataFrame(result)
    file_path = os.path.join(UPLOAD_DIR, f"{table}.xlsx")
    df.to_excel(file_path, index=False)
    return FileResponse(file_path, filename=f"{table}.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@router.post("/import/{table}")
async def import_table(table: str, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """This route allows an administrator to import an Excel file and adapt it to the structure of a given SQL table.
    Parameters:
    -----------
    table: str
        Name of the target table for import.
    request: Request
        HTTP request containing the Excel file.
    db: Session
        Injected SQLAlchemy session.
    user: User
        Logged-in user (must be an administrator).
    Return:
    -------
    dict
        Dictionary containing the status of the operation,
        the number of entries inserted, and an AI suggestion.
    Version:
    --------
    specification: Esteban Barracho (v.1 12/07/2025)
    implement: Esteban Barracho (v.1 12/07/2025)
    """
    check_admin(user)
    form = await request.form()
    file = form["file"]
    contents = await file.read()
    path = os.path.join(UPLOAD_DIR, f"import_{table}.xlsx")
    with open(path, "wb") as f:
        f.write(contents)
    inserted, suggestion = adapt_excel_to_table(table=table, file_path=path, db=db)
    return {"status": "ok", "inserted": inserted, "suggestion": suggestion}

