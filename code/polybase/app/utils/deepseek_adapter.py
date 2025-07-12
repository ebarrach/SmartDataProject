# ============================================
# IMPORTS
# ============================================

import pandas as pd
from app.database import SessionLocal
from sqlalchemy import inspect


def reorder_columns(df: pd.DataFrame, table: str):
    """Réordonne les colonnes d’un DataFrame selon l’ordre de la table SQL.
    Parameters:
    -----------
    df : pd.DataFrame
        Données importées depuis Excel ou autre source.
    table : str
        Nom de la table SQL cible.

    Returns:
    --------
    pd.DataFrame : DataFrame réordonné selon l’ordre des colonnes SQL.

    Version:
    --------
    specification: Esteban Barracho (v.1 11/07/2025)
    implement: Esteban Barracho (v.1.1 12/07/2025)
    """
    assert isinstance(df, pd.DataFrame), "Entrée invalide : un DataFrame est attendu"
    assert isinstance(table, str) and table.strip(), "Nom de table invalide ou vide"

    db = SessionLocal()
    try:
        inspector = inspect(db.get_bind())
        sql_columns = [col["name"] for col in inspector.get_columns(table)]
        df_cols = df.columns.tolist()
        missing = [col for col in sql_columns if col not in df_cols]
        extra = [col for col in df_cols if col not in sql_columns]
        print(f"ℹ Colonnes manquantes: {missing}")
        print(f"ℹ Colonnes inutiles: {extra}")
        ordered = [col for col in sql_columns if col in df.columns]
        return df[ordered]
    finally:
        db.close()


def fix_types(df: pd.DataFrame, table: str):
    """Adapte les types de colonnes d’un DataFrame aux types SQL de la table.
    Parameters:
    -----------
    df : pd.DataFrame
        Données en mémoire à corriger.
    table : str
        Nom de la table SQL pour récupérer les types.

    Returns:
    --------
    pd.DataFrame : DataFrame avec colonnes typées selon la structure SQL.

    Version:
    --------
    specification: Esteban Barracho (v.1 11/07/2025)
    implement: Esteban Barracho (v.1.1 12/07/2025)
    """
    assert isinstance(df, pd.DataFrame), "Entrée invalide : un DataFrame est attendu"
    assert isinstance(table, str) and table.strip(), "Nom de table invalide ou vide"

    db = SessionLocal()
    try:
        inspector = inspect(db.get_bind())
        for col in inspector.get_columns(table):
            name = col["name"]
            sql_type = str(col["type"]).upper()
            if name not in df.columns:
                continue
            if "DATE" in sql_type:
                df[name] = pd.to_datetime(df[name], errors="coerce").dt.strftime("%Y-%m-%d")
            elif "INT" in sql_type:
                df[name] = pd.to_numeric(df[name], errors="coerce").astype("Int64")
            elif "DECIMAL" in sql_type or "FLOAT" in sql_type:
                df[name] = pd.to_numeric(df[name], errors="coerce")
            elif "BOOLEAN" in sql_type:
                df[name] = df[name].astype(bool)
        return df
    finally:
        db.close()


def adapt_excel(file_path: str, table: str):
    """Lit un fichier Excel, le nettoie et l’adapte à la structure d’une table SQL.
    Cette fonction applique plusieurs étapes :
    - Suppression des espaces dans les noms de colonnes.
    - Réordonnancement selon la structure SQL.
    - Conversion automatique des types.

    Parameters:
    -----------
    file_path : str
        Chemin vers le fichier Excel à adapter.
    table : str
        Nom de la table cible pour l’adaptation.

    Returns:
    --------
    list[dict] : Liste d’enregistrements prêts à insérer via l’API.

    Version:
    --------
    specification: Esteban Barracho (v.1 11/07/2025)
    implement: Esteban Barracho (v.1.1 12/07/2025)
    """
    assert isinstance(file_path, str) and file_path.endswith((".xlsx", ".xls")), "Chemin de fichier Excel invalide"
    assert isinstance(table, str) and table.strip(), "Nom de table invalide ou vide"

    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    df = reorder_columns(df, table)
    df = fix_types(df, table)
    return df.fillna("").to_dict(orient="records")


def prepare_adaptation():
    """Prépare l’environnement de correction DeepSeek au démarrage de l’API.
    Cette fonction peut être utilisée pour :
    - Initialiser des caches si besoin.
    - Vérifier la connectivité base/SQLAlchemy.
    - Afficher un message de disponibilité.

    Version:
    --------
    specification: Esteban Barracho (v.1 11/07/2025)
    implement: Esteban Barracho (v.1.1 12/07/2025)
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")  # Simple test de connexion
        print("🧠 DeepSeek prêt pour adapter les fichiers Excel.")
    except Exception as e:
        print(f"⚠ Erreur DeepSeek : {e}")
    finally:
        db.close()
