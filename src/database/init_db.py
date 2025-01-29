# src/database/init_db.py
import os
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from src.database.models import Base
                                                                                                                                        
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./items.db")
                                                                                                                                        
def initialize_database():
    engine = create_engine(DATABASE_URL.replace("+aiosqlite", ""))
                                                                                                                                        
    if not database_exists(engine.url):
        create_database(engine.url)
                                                                                                                                        
    Base.metadata.create_all(bind=engine)
                                                                                                                                        
    # Add test groups if needed
    # ...
                                                                                                                                        
if __name__ == "__main__":
    initialize_database()