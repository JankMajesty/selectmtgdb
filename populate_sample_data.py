#!/usr/bin/env python3
"""
Populate database with a small sample of MTG cards for demonstration.
This is a lightweight version that doesn't require the full Scryfall API calls.
"""

import sqlite3
import os

def populate_sample_data(db_path: str = "mtg_database.db"):
    """Add some sample MTG cards to demonstrate the database functionality"""
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if we already have data
        cursor.execute("SELECT COUNT(*) FROM Card")
        card_count = cursor.fetchone()[0]
        
        if card_count > 0:
            print(f"Database already contains {card_count} cards. Skipping sample data population.")
            return True
        
        print("Populating database with sample MTG cards...")
        
        # Insert sample artists
        artists = [
            "Mark Tedin", "Kev Walker", "Pete Venters", "rk post", "Matt Cavotta"
        ]
        
        for artist in artists:
            cursor.execute("INSERT OR IGNORE INTO Artist (ArtistName) VALUES (?)", (artist,))
        
        # Insert sample rarities
        rarities = ["Common", "Uncommon", "Rare", "Mythic Rare"]
        for rarity in rarities:
            cursor.execute("INSERT OR IGNORE INTO Rarity (RarityName) VALUES (?)", (rarity,))
        
        # Insert sample sets
        sets_data = [
            ("Urza's Saga", "USG", "1998-10-12"),
            ("Urza's Legacy", "ULG", "1999-02-15"),
            ("Urza's Destiny", "UDS", "1999-06-07")
        ]
        
        for set_name, set_code, release_date in sets_data:
            cursor.execute("INSERT OR IGNORE INTO CardSet (SetName, SetCode, ReleaseDate) VALUES (?, ?, ?)", 
                         (set_name, set_code, release_date))
        
        # Insert sample colors
        colors = ["W", "U", "B", "R", "G"]
        for color in colors:
            cursor.execute("INSERT OR IGNORE INTO Color (Color) VALUES (?)", (color,))
        
        # Insert sample card types
        card_types = ["Creature", "Instant", "Sorcery", "Enchantment", "Artifact", "Land"]
        for card_type in card_types:
            cursor.execute("INSERT OR IGNORE INTO CardType (TypeName) VALUES (?)", (card_type,))
        
        # Insert sample subtypes
        subtypes = ["Human", "Wizard", "Goblin", "Artifact", "Aura", "Equipment"]
        for subtype in subtypes:
            cursor.execute("INSERT OR IGNORE INTO SubType (SubTypeName) VALUES (?)", (subtype,))
        
        # Insert sample cards
        sample_cards = [
            {
                "name": "Lightning Bolt",
                "mana_cost": "{R}",
                "cmc": 1.0,
                "abilities": "Lightning Bolt deals 3 damage to any target.",
                "artist": "rk post",
                "rarity": "Common",
                "set_code": "USG",
                "types": ["Instant"],
                "colors": ["R"]
            },
            {
                "name": "Serra Angel",
                "mana_cost": "{3}{W}{W}",
                "cmc": 5.0,
                "abilities": "Flying, vigilance",
                "power": "4",
                "toughness": "4",
                "artist": "Mark Tedin",
                "rarity": "Rare",
                "set_code": "USG",
                "types": ["Creature"],
                "subtypes": ["Angel"],
                "colors": ["W"]
            },
            {
                "name": "Counterspell",
                "mana_cost": "{U}{U}",
                "cmc": 2.0,
                "abilities": "Counter target spell.",
                "artist": "Kev Walker",
                "rarity": "Common",
                "set_code": "ULG",
                "types": ["Instant"],
                "colors": ["U"]
            },
            {
                "name": "Sol Ring",
                "mana_cost": "{1}",
                "cmc": 1.0,
                "abilities": "{T}: Add {C}{C}.",
                "artist": "Pete Venters",
                "rarity": "Uncommon",
                "set_code": "UDS",
                "types": ["Artifact"],
                "colors": []
            },
            {
                "name": "Forest",
                "mana_cost": "",
                "cmc": 0.0,
                "abilities": "{T}: Add {G}.",
                "artist": "Matt Cavotta",
                "rarity": "Common",
                "set_code": "USG",
                "types": ["Land"],
                "subtypes": ["Forest"],
                "colors": []
            }
        ]
        
        for card in sample_cards:
            # Get foreign key IDs
            cursor.execute("SELECT ArtistID FROM Artist WHERE ArtistName = ?", (card["artist"],))
            artist_id = cursor.fetchone()[0]
            
            cursor.execute("SELECT RarityID FROM Rarity WHERE RarityName = ?", (card["rarity"],))
            rarity_id = cursor.fetchone()[0]
            
            cursor.execute("SELECT SetID FROM CardSet WHERE SetCode = ?", (card["set_code"],))
            set_id = cursor.fetchone()[0]
            
            # Insert card
            cursor.execute("""
                INSERT INTO Card (CardName, ManaCost, ConvertedManaCost, Abilities, 
                                Power, Toughness, ArtistID, RarityID, SetID)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                card["name"], card["mana_cost"], card["cmc"], card["abilities"],
                card.get("power"), card.get("toughness"), artist_id, rarity_id, set_id
            ))
            
            card_id = cursor.lastrowid
            
            # Insert card-color relationships
            for color in card.get("colors", []):
                cursor.execute("SELECT ColorID FROM Color WHERE Color = ?", (color,))
                color_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO Card_Color (CardID, ColorID) VALUES (?, ?)", 
                             (card_id, color_id))
            
            # Insert card-type relationships
            for card_type in card.get("types", []):
                cursor.execute("SELECT CardTypeID FROM CardType WHERE TypeName = ?", (card_type,))
                type_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO Card_CardType (CardID, CardTypeID) VALUES (?, ?)", 
                             (card_id, type_id))
            
            # Insert card-subtype relationships
            for subtype in card.get("subtypes", []):
                cursor.execute("SELECT SubTypeID FROM SubType WHERE SubTypeName = ?", (subtype,))
                subtype_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO Card_SubType (CardID, SubTypeID) VALUES (?, ?)", 
                             (card_id, subtype_id))
        
        conn.commit()
        
        # Print statistics
        cursor.execute("SELECT COUNT(*) FROM Card")
        card_count = cursor.fetchone()[0]
        print(f"Successfully populated database with {card_count} sample cards")
        
        return True
        
    except Exception as e:
        print(f"Error populating sample data: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    populate_sample_data()
