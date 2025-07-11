# ============================================
# IMPORTS
# ============================================

import pandas as pd
from app.database import SessionLocal
from sqlalchemy import inspect


def reorder_columns(df: pd.DataFrame, table: str):
    """Réordonne les colonnes d’un DataFrame selon l’ordre SQL de la table."""
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
    """Corrige les types simples pour correspondre à ceux de la table SQL."""
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
    """
    Lit un fichier Excel, le corrige automatiquement et renvoie un JSON prêt à injecter.

    - Corrige les noms de colonnes.
    - Trie les colonnes dans l'ordre attendu.
    - Corrige les types selon la base.

    Parameters:
        file_path (str): Chemin du fichier Excel.
        table (str): Nom de la table cible.

    Returns:
        list[dict]: Données adaptées prêtes à être envoyées au backend.
    """
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    df = reorder_columns(df, table)
    df = fix_types(df, table)
    return df.fillna("").to_dict(orient="records")


def prepare_adaptation():
    """
    Prépare l’environnement de correction DeepSeek au démarrage de l’API.

    Cette fonction peut être utilisée pour :
    - Initialiser des caches si besoin.
    - Vérifier la connectivité base/SQLAlchemy.
    - Afficher un message de disponibilité.

    Version:
    --------
    specification: Esteban Barracho (v.2 11/07/2025)
    implement: Esteban Barracho (v.2 11/07/2025)
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")  # Simple test de connexion
        print("🧠 DeepSeek prêt pour adapter les fichiers Excel.")
    except Exception as e:
        print(f"⚠ Erreur DeepSeek : {e}")
    finally:
        db.close()
