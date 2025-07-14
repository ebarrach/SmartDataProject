# ============================================
# IMPORTS
# ============================================

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ============================================
# PROVIDING THE SESSION TO THE APPLICATION
# ============================================

def get_db():
    """Dependency injection for a SQLAlchemy session.
    Version:
    --------
    specification: Esteban Barracho (v.1 22/06/2025)
    implement: Esteban Barracho (v.1 22/06/2025)
    """
    db = SessionLocal()
    assert db is not None, "Session DB invalide"
    try:
        yield db
    finally:
        db.close()

# ============================================
# LOADING ENVIRONMENT VARIABLES
# ============================================

load_dotenv()
"""This instruction loads environment variables from a `.env` file located at the root of the project.
Version:
--------
specification: Esteban Barracho (v.1 19/06/2025)
implement: Esteban Barracho (v.1 19/06/2025)
"""

# ============================================
# CONFIGURATION OF LOGIN CREDENTIALS
# ============================================

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

assert all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]), "⚠️ Variables d'environnement SQL manquantes"

# ============================================
# CONNECTION TO THE DATABASE
# ============================================

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
"""This string defines the full SQLAlchemy-compatible database URL.
Version:
--------
specification: Esteban Barracho (v.1 19/06/2025)
implement: Esteban Barracho (v.1 19/06/2025)
"""

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
"""This object creates the SQLAlchemy engine based on the URL configuration.
Version:
--------
specification: Esteban Barracho (v.1 19/06/2025)
implement: Esteban Barracho (v.2 22/06/2025)
"""

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
"""This object provides a factory for creating new SQLAlchemy session instances.
Version:
--------
specification: Esteban Barracho (v.1 19/06/2025)
implement: Esteban Barracho (v.1 19/06/2025)
"""

Base = declarative_base()
"""This base class is used to define ORM models.
Version:
--------
specification: Esteban Barracho (v.1 19/06/2025)
implement: Esteban Barracho (v.1 19/06/2025)
"""
