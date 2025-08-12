#!/usr/bin/env python3
"""
Initialize database for production deployment.
This creates an empty database with the schema but no data.
"""
import sqlite3
import os

def init_database():
    """Initialize database with schema only"""
    db_path = "mtg_database.db"
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    # Create new database with schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read and execute the schema
    with open('mtgSchema.sql', 'r') as f:
        schema = f.read()
        cursor.executescript(schema)
    
    conn.commit()
    conn.close()
    print(f"Database initialized: {db_path}")
    print("Note: Database contains schema only, no card data.")

if __name__ == "__main__":
    init_database()
