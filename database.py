"""
database.py

This module sets up the SQLAlchemy database connection, session management,
and defines the User model for the application. It loads environment variables
from a .env file for configuration and ensures proper resource management.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv()

# Retrieve the database URL from environment variables
DATABASE_URL = os.getenv("DB_URL")
if not DATABASE_URL:
    raise ValueError("DB_URL environment variable not set.")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative class definitions
Base = declarative_base()

class User(Base):
    """
    User model representing the 'user' table in the database.

    Attributes:
        id (int): Primary key.
        first_name (str): User's first name.
        last_name (str): User's last name.
        phone_number (str): User's phone number.
        default_language (str): User's default language.
        output_language (str): User's preferred output language.
        output_format (str): User's preferred output format.
    """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False, unique=True)
    default_language = Column(String, nullable=True)
    output_language = Column(String, nullable=True)
    output_format = Column(String, nullable=True)

# Create all tables in the database (if they don't exist)
Base.metadata.create_all(bind=engine)

def get_db():
    """
    Dependency generator that provides a database session.

    Yields:
        db (Session): SQLAlchemy database session.
    Ensures:
        The session is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()