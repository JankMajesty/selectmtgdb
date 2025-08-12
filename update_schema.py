import sqlite3

def update_schema():
    """Add Layout and SuperType columns to existing database"""
    print("Updating database schema...")
    
    # Connect to existing database
    conn = sqlite3.connect('mtg_database.db')
    cursor = conn.cursor()
    
    try:
        # Check if Layout column already exists
        cursor.execute("PRAGMA table_info(Card)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'Layout' not in columns:
            print("Adding Layout column to Card table...")
            cursor.execute("ALTER TABLE Card ADD COLUMN Layout TEXT")
            conn.commit()
            print("Layout column added successfully!")
        else:
            print("Layout column already exists.")
        
        # Add SuperType column if it doesn't exist
        if 'SuperType' not in columns:
            print("Adding SuperType column to Card table...")
            cursor.execute("ALTER TABLE Card ADD COLUMN SuperType TEXT")
            conn.commit()
            print("SuperType column added successfully!")
        else:
            print("SuperType column already exists.")
        
        # Update existing split cards to have layout='split'
        print("Updating existing split cards...")
        cursor.execute("""
            UPDATE Card 
            SET Layout = 'split' 
            WHERE CardName LIKE '%//%'
        """)
        
        updated_count = cursor.rowcount
        print(f"Updated {updated_count} split cards with layout='split'")
        
        # Set layout='normal' for all other cards
        cursor.execute("""
            UPDATE Card 
            SET Layout = 'normal' 
            WHERE Layout IS NULL
        """)
        
        normal_count = cursor.rowcount
        print(f"Set {normal_count} cards to layout='normal'")
        
        # Basic SuperType detection for existing cards
        print("Adding basic SuperType detection for existing cards...")
        
        # Legendary cards (basic detection)
        cursor.execute("""
            UPDATE Card 
            SET SuperType = 'Legendary' 
            WHERE CardName LIKE '%Legendary%' AND SuperType IS NULL
        """)
        legendary_count = cursor.rowcount
        print(f"Set {legendary_count} cards to SuperType='Legendary'")
        
        # Basic lands
        cursor.execute("""
            UPDATE Card 
            SET SuperType = 'Basic' 
            WHERE CardName IN ('Plains', 'Island', 'Swamp', 'Mountain', 'Forest') 
            AND SuperType IS NULL
        """)
        basic_count = cursor.rowcount
        print(f"Set {basic_count} cards to SuperType='Basic'")
        
        conn.commit()
        print("Schema update completed successfully!")
        
        # Print summary
        cursor.execute("SELECT COUNT(*) FROM Card WHERE SuperType IS NOT NULL")
        supertype_count = cursor.fetchone()[0]
        cursor.execute("SELECT SuperType, COUNT(*) FROM Card WHERE SuperType IS NOT NULL GROUP BY SuperType")
        supertype_stats = cursor.fetchall()
        
        print(f"\nSummary:")
        print(f"- Cards with SuperType: {supertype_count}")
        for supertype, count in supertype_stats:
            print(f"  {supertype}: {count} cards")
        
    except Exception as e:
        print(f"Error updating schema: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_schema()
