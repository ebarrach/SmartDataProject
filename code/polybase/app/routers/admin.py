# ============================================
# IMPORTS
# ============================================

import string
import random
import bcrypt
import Levenshtein
from fastapi import APIRouter, Depends, Request, HTTPException, status, Query
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from app.auth import get_current_user

# ============================================
# ROUTER INITIALIZATION
# ============================================

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")

# ============================================
# GESTION DES PRÉFIXES D'IDENTIFIANTS
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
    """Génère un identifiant métier unique (ex: CL001, PRJ002)."""
    num = ''.join(random.choices(string.digits, k=length))
    return f"{prefix}{num}"


# ============================================
# ACCÈS ADMIN
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
# PAGE HTML ADMIN
# ============================================
@router.get("", response_class=JSONResponse)
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
# LISTE DES TABLES
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
# STRUCTURE DE TABLE
# ============================================
@router.get("/table/{table}/structure")
def get_table_structure(table: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Retrieves the structure of a specific table, including types, nullability, and examples.
    Parameters:
    -----------
    table (str): Name of the table to inspect.
    db (Session): Database session.
    user: Authenticated admin user.

    Returns:
    --------
    list[dict]: Column metadata including example values.

    Version:
    --------
    specification: Esteban Barracho (v.1 26/06/2025)
    implement: Esteban Barracho (v.1.2 09/07/2025)
    """
    check_admin(user)
    inspector = inspect(db.get_bind())
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
        })
    return cols


# ============================================
# DONNÉES DE TABLE
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
    implement: Esteban Barracho (v.1 26/06/2025)
    """

    check_admin(user)
    result = db.execute(text(f"SELECT * FROM `{table}`"))
    data = [dict(row) for row in result.mappings()]
    return data


# ============================================
# INSERTION SÉCURISÉE
# ============================================
@router.post("/table/{table}")
def insert_row(table: str, row: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Inserts a new row securely into the specified table with optional ID generation.
    Parameters:
    -----------
    table (str): Table name to insert into.
    row (dict): Dictionary of values to insert.
    db (Session): Active database session.
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
    insert_row = {}

    # GÉNÈRE L'ID SI NÉCESSAIRE (clé primaire métier)
    id_field = None
    prefix = table_prefixes.get(table)
    for cname, cinfo in columns.items():
        if cname.startswith('id_') and cinfo.get("primary_key", False):
            id_field = cname
            break
    if id_field and prefix:
        # Vérifie unicité et regénère si existe déjà (boucle protection)
        for _ in range(10):
            new_id = generate_id(prefix)
            exists = db.execute(text(f"SELECT 1 FROM `{table}` WHERE `{id_field}` = :id"), {"id": new_id}).first()
            if not exists:
                insert_row[id_field] = new_id
                break
        else:
            raise HTTPException(500, detail="Impossible de générer un nouvel identifiant unique.")

    # INJECTION DES AUTRES CHAMPS (hors ID et password)
    for k, v in row.items():
        if k == id_field:
            continue  # Ne jamais prendre l'id fourni par le client !
        if k not in columns:
            raise HTTPException(400, detail=f"Colonne interdite: {k}")
        c = columns[k]
        if not c["nullable"] and (v is None or v == ""):
            raise HTTPException(400, detail=f"Champ obligatoire manquant: {k}")
        typ = str(c["type"]).upper()
        if ("INT" in typ or "DECIMAL" in typ) and v not in (None, "") and not str(v).replace(".", "", 1).isdigit():
            raise HTTPException(400, detail=f"Le champ {k} doit être numérique.")
        if c.get("length") and v and len(str(v)) > c["length"]:
            raise HTTPException(400, detail=f"Le champ {k} dépasse la longueur max {c['length']}.")
        # Hashage automatique pour le mot de passe
        if k == "password" and v:
            hashed = bcrypt.hashpw(v.encode("utf-8"), bcrypt.gensalt()).decode()
            insert_row[k] = hashed
        else:
            insert_row[k] = v if v not in ("", None) else None

    # CONSTRUCTION ET EXECUTION SQL
    keys = ", ".join([f"`{k}`" for k in insert_row.keys()])
    vals = ", ".join([f":{k}" for k in insert_row.keys()])
    sql = text(f"INSERT INTO `{table}` ({keys}) VALUES ({vals})")
    try:
        db.execute(sql, insert_row)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(400, detail=f"Erreur lors de l’insertion : {e}")
    # Retourne l'identifiant généré (pour liaison côté client)
    return {"status": "ok", "id": insert_row.get(id_field, None)}

# ============================================
# RECHERCHE GLOBALE LEVENSHTEIN SUR TOUTES LES TABLES
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
# MISE À JOUR D'UNE ENTRÉE (PUT)
# ============================================
@router.put("/table/{table}/{id}")
@router.put("/table/{table}/{id}")
def update_row(table: str, id: str, row: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Updates a record in a table based on its primary key.
    Parameters:
    -----------
    table (str): Table name to update.
    id (str): Identifier of the row to update.
    row (dict): Fields and values to modify.
    db (Session): Active database session.
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
    sql = text(f"UPDATE `{table}` SET {', '.join(updates)} WHERE `{id_field}` = :id")
    try:
        db.execute(sql, values)
        db.commit()
        return {"status": "ok"}
    except Exception as e:
        db.rollback()
        raise HTTPException(400, detail=f"Erreur lors de la mise à jour : {e}")


# ============================================
# SUPPRESSION D'UNE ENTRÉE (DELETE)
# ============================================
@router.delete("/table/{table}/{id}")
def delete_row(table: str, id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Deletes a row from a specified table based on primary key.
    Parameters:
    -----------
    table (str): Table name.
    id (str): Identifier of the row to delete.
    db (Session): Active database session.
    user: Authenticated admin user.

    Returns:
    --------
    dict: Confirmation message of successful deletion.

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
    id_field = pk['constrained_columns'][0] if pk['constrained_columns'] else None

    if not id_field:
        raise HTTPException(400, detail="Impossible de déterminer la clé primaire.")

    print(f"🧹 Suppression dans {table} sur {id_field} = {id}")  # DEBUG

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

