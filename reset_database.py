"""
Script to reset the database by dropping all tables and recreating them.
This is useful during development when the schema is still evolving.
"""
import sys
from sqlalchemy import text

from app.db.base import Base
from app.core.config import get_settings
from sqlalchemy import create_engine

def reset_database():
    # Create engine with echo for logging SQL commands
    db_url = get_settings().database_url
    engine = create_engine(db_url, echo=True)
    
    print("Dropping all tables...")
    # Use raw SQL to drop all tables in the correct order (handling foreign keys)
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        
        # Get all table names
        result = conn.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        
        # Drop each table
        for table in tables:
            print(f"Dropping table: {table}")
            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
            
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    
    print("Creating all tables from models...")
    # Create all tables based on models
    Base.metadata.create_all(bind=engine)
    
    print("Database reset complete!")

if __name__ == "__main__":
    # Ask for confirmation to prevent accidental data loss
    if len(sys.argv) > 1 and sys.argv[1].lower() == "--confirm":
        reset_database()
    else:
        print("WARNING: This will delete all data in the database!")
        print("To confirm, run: python reset_database.py --confirm")
