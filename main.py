import sqlite3
import requests
import json
from typing import Dict, List, Optional
import time
import os
import argparse

class MTGDatabase:
    def __init__(self, db_path: str = "mtg_database.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Connect to SQLite database and create tables"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Read and execute the schema
        with open('mtgSchema.sql', 'r') as f:
            schema = f.read()
            self.cursor.executescript(schema)
        
        self.conn.commit()
        print("Database connected and schema created")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def get_or_insert_artist(self, artist_name: str) -> int:
        """Get existing artist ID or insert new artist and return ArtistID"""
        # First try to get existing artist
        self.cursor.execute(
            "SELECT ArtistID FROM Artist WHERE ArtistName = ?",
            (artist_name,)
        )
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
        
        # If not found, insert new artist
        self.cursor.execute(
            "INSERT INTO Artist (ArtistName) VALUES (?)",
            (artist_name,)
        )
        return self.cursor.lastrowid
    
    def get_or_insert_rarity(self, rarity_name: str) -> int:
        """Get existing rarity ID or insert new rarity and return RarityID"""
        # First try to get existing rarity
        self.cursor.execute(
            "SELECT RarityID FROM Rarity WHERE RarityName = ?",
            (rarity_name,)
        )
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
        
        # If not found, insert new rarity
        self.cursor.execute(
            "INSERT INTO Rarity (RarityName) VALUES (?)",
            (rarity_name,)
        )
        return self.cursor.lastrowid
    
    def get_or_insert_set(self, set_name: str, set_code: str, release_date: str) -> int:
        """Get existing set ID or insert new set and return SetID"""
        # First try to get existing set
        self.cursor.execute(
            "SELECT SetID FROM CardSet WHERE SetCode = ?",
            (set_code,)
        )
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
        
        # If not found, insert new set
        self.cursor.execute(
            "INSERT INTO CardSet (SetName, SetCode, ReleaseDate) VALUES (?, ?, ?)",
            (set_name, set_code, release_date)
        )
        return self.cursor.lastrowid
    
    def get_or_insert_color(self, color: str) -> int:
        """Get existing color ID or insert new color and return ColorID"""
        # First try to get existing color
        self.cursor.execute(
            "SELECT ColorID FROM Color WHERE Color = ?",
            (color,)
        )
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
        
        # If not found, insert new color
        self.cursor.execute(
            "INSERT INTO Color (Color) VALUES (?)",
            (color,)
        )
        return self.cursor.lastrowid
    
    def get_or_insert_card_type(self, type_name: str) -> int:
        """Get existing card type ID or insert new type and return CardTypeID"""
        # First try to get existing type
        self.cursor.execute(
            "SELECT CardTypeID FROM CardType WHERE TypeName = ?",
            (type_name,)
        )
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
        
        # If not found, insert new type
        self.cursor.execute(
            "INSERT INTO CardType (TypeName) VALUES (?)",
            (type_name,)
        )
        return self.cursor.lastrowid
    
    def get_or_insert_subtype(self, subtype_name: str) -> int:
        """Get existing subtype ID or insert new subtype and return SubTypeID"""
        # First try to get existing subtype
        self.cursor.execute(
            "SELECT SubTypeID FROM SubType WHERE SubTypeName = ?",
            (subtype_name,)
        )
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
        
        # If not found, insert new subtype
        self.cursor.execute(
            "INSERT INTO SubType (SubTypeName) VALUES (?)",
            (subtype_name,)
        )
        return self.cursor.lastrowid
    
    def get_or_insert_supertype(self, supertype_name: str) -> int:
        """Get existing supertype ID or insert new supertype and return SuperTypeID"""
        # First try to get existing supertype
        self.cursor.execute(
            "SELECT SuperTypeID FROM SuperType WHERE SuperTypeName = ?",
            (supertype_name,)
        )
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
        
        # If not found, insert new supertype
        self.cursor.execute(
            "INSERT INTO SuperType (SuperTypeName) VALUES (?)",
            (supertype_name,)
        )
        return self.cursor.lastrowid

    def parse_type_line(self, type_line: str) -> tuple:
        """Parse type line into supertypes, types, and subtypes"""
        if not type_line:
            return [], [], []
        
        # Split by '—' to separate types from subtypes
        parts = type_line.split('—')
        type_part = parts[0].strip()
        subtype_part = parts[1].strip() if len(parts) > 1 else ""
        
        # Define known supertypes (expanded list)
        known_supertypes = {
            'Legendary', 'Basic', 'Snow', 'World', 'Elite', 'Ongoing',
            'Tribal', 'Host', 'Dungeon', 'Background', 'Class'
        }
        
        # Parse the type part
        words = type_part.split()
        supertypes = []
        types = []
        
        for word in words:
            if word in known_supertypes:
                supertypes.append(word)
            else:
                types.append(word)
        
        # Parse subtypes and remove duplicates
        subtypes = list(dict.fromkeys(subtype_part.split())) if subtype_part else []
        
        return supertypes, types, subtypes

    def insert_card(self, card_data: Dict) -> int:
        """Insert card and return CardID"""
        # Debug: Print type line for problematic cards
        if card_data['name'] in ['Alloy Golem', 'Henge Guardian', 'Hollow Warrior', 'Phyrexian Colossus']:
            print(f"DEBUG INSERT: {card_data['name']}")
            print(f"  Raw type_line: '{card_data.get('type_line', 'MISSING')}'")
        
        # Get foreign key IDs using get_or_insert methods
        artist_id = self.get_or_insert_artist(card_data.get('artist', 'Unknown'))
        rarity_id = self.get_or_insert_rarity(card_data.get('rarity', 'Unknown'))
        set_id = self.get_or_insert_set(
            card_data['set_name'],
            card_data['set'],
            card_data.get('released_at', '1900-01-01')
        )
        
        # Parse type line for supertype
        supertypes, types, subtypes = self.parse_type_line(card_data.get('type_line', ''))
        primary_supertype = supertypes[0] if supertypes else None
        
        # Debug: Print parsed results for problematic cards
        if card_data['name'] in ['Alloy Golem', 'Henge Guardian', 'Hollow Warrior', 'Phyrexian Colossus']:
            print(f"  Parsed supertypes: {supertypes}")
            print(f"  Parsed types: {types}")
            print(f"  Parsed subtypes: {subtypes}")
            print()
        
        # Insert card
        self.cursor.execute("""
            INSERT INTO Card (
                CardName, ManaCost, ConvertedManaCost, Abilities, 
                FlavorText, Power, Toughness, ImageURL, Layout, SuperType,
                ArtistID, RarityID, SetID
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            card_data['name'],
            card_data.get('mana_cost'),
            card_data.get('cmc'),
            card_data.get('oracle_text', ''),
            card_data.get('flavor_text', ''),
            card_data.get('power'),
            card_data.get('toughness'),
            card_data.get('image_uris', {}).get('normal', ''),
            card_data.get('layout', 'normal'),
            primary_supertype,
            artist_id,
            rarity_id,
            set_id
        ))
        
        card_id = self.cursor.lastrowid
        
        # Insert colors
        for color in card_data.get('colors', []):
            color_id = self.get_or_insert_color(color)
            self.cursor.execute(
                "INSERT OR IGNORE INTO Card_Color (CardID, ColorID) VALUES (?, ?)",
                (card_id, color_id)
            )
        
        # Insert card types (remove duplicates)
        unique_types = list(dict.fromkeys(types))
        for card_type in unique_types:
            type_id = self.get_or_insert_card_type(card_type)
            self.cursor.execute(
                "INSERT OR IGNORE INTO Card_CardType (CardID, CardTypeID) VALUES (?, ?)",
                (card_id, type_id)
            )
        
        # Insert subtypes (remove duplicates)
        unique_subtypes = list(dict.fromkeys(subtypes))
        for subtype in unique_subtypes:
            subtype_id = self.get_or_insert_subtype(subtype)
            self.cursor.execute(
                "INSERT OR IGNORE INTO Card_SubType (CardID, SubTypeID) VALUES (?, ?)",
                (card_id, subtype_id)
            )
        
        return card_id

class ScryfallAPI:
    def __init__(self):
        self.base_url = "https://api.scryfall.com"
    
    def get_urzas_block_sets(self) -> List[str]:
        """Get all set codes for Urza's block"""
        # Urza's block consists of: Urza's Saga, Urza's Legacy, Urza's Destiny
        return ['usg', 'ulg', 'uds']
    
    def get_masques_block_sets(self) -> List[str]:
        """Get all set codes for Masques block"""
        # Masques block consists of: Mercadian Masques, Nemesis, Prophecy
        return ['mmq', 'nem', 'pcy']
    
    def get_invasion_block_sets(self) -> List[str]:
        """Get all set codes for Invasion block"""
        # Invasion block consists of: Invasion, Planeshift, Apocalypse
        return ['inv', 'pls', 'apc']
    
    def get_all_target_sets(self) -> List[str]:
        """Get all target set codes"""
        return ['usg', 'ulg', 'uds', 'mmq', 'nem', 'pcy', 'inv', 'pls', 'apc']
    
    def get_cards_from_set(self, set_code: str) -> List[Dict]:
        """Get all cards from a specific set"""
        cards = []
        page = 1
        
        print(f"Fetching cards from {set_code}...")
        
        while True:
            url = f"{self.base_url}/cards/search"
            params = {
                'q': f'set:{set_code}',
                'page': page
            }
            
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if 'data' not in data:
                    print(f"No data found for {set_code}")
                    break
                
                print(f"Page {page}: Found {len(data['data'])} cards")
                cards.extend(data['data'])
                
                # Check if there are more pages
                if not data.get('has_more', False):
                    break
                
                page += 1
                
                # Be respectful to the API
                time.sleep(0.1)
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching cards from set {set_code}: {e}")
                break
        
        print(f"Total cards fetched from {set_code}: {len(cards)}")
        
        # Explicitly fetch ALL basic land printings for this set
        basic_lands = ['Plains', 'Island', 'Swamp', 'Mountain', 'Forest']
        
        for land_name in basic_lands:
            try:
                # Use a different approach to get all printings
                land_url = f"{self.base_url}/cards/search"
                land_params = {
                    'q': f'name:"{land_name}" set:{set_code}',
                    'unique': 'prints'  # This should get all printings
                }
                
                land_response = requests.get(land_url, params=land_params)
                land_response.raise_for_status()
                land_data = land_response.json()
                
                if 'data' in land_data and land_data['data']:
                    # Remove any existing basic lands of this type from the set
                    cards = [card for card in cards if not (card['name'] == land_name and card['set'] == set_code)]
                    
                    # Add all printings of this basic land
                    for land_card in land_data['data']:
                        if land_card['name'] == land_name and land_card['set'] == set_code:
                            cards.append(land_card)
                            print(f"Added {land_name} by {land_card.get('artist', 'Unknown')} from {set_code}")
                
                time.sleep(0.1)  # Be respectful to the API
                
            except Exception as e:
                print(f"Error fetching {land_name} from {set_code}: {e}")
                # Continue with other lands even if one fails
                continue
        
        # Count basic lands
        basic_land_count = sum(1 for card in cards if card['name'] in ['Plains', 'Island', 'Swamp', 'Mountain', 'Forest'])
        print(f"Found {basic_land_count} basic land printings in {set_code}")
        
        for card in cards:
            if card['name'] in ['Alloy Golem', 'Henge Guardian']:
                print(f"DEBUG: {card['name']}")
                print(f"  type_line: '{card.get('type_line', 'MISSING')}'")
                print(f"  types: {card.get('type_line', '').split('—')[0].strip() if '—' in card.get('type_line', '') else card.get('type_line', '')}")
                print(f"  subtypes: {card.get('type_line', '').split('—')[1].strip() if '—' in card.get('type_line', '') else 'NONE'}")
                print()
        
        return cards

def print_database_statistics(db):
    """Print comprehensive database statistics"""
    # Basic counts
    db.cursor.execute("SELECT COUNT(*) FROM Card")
    card_count = db.cursor.fetchone()[0]
    
    db.cursor.execute("SELECT COUNT(*) FROM Artist")
    artist_count = db.cursor.fetchone()[0]
    
    db.cursor.execute("SELECT COUNT(*) FROM CardSet")
    set_count = db.cursor.fetchone()[0]
    
    db.cursor.execute("SELECT COUNT(*) FROM Color")
    color_count = db.cursor.fetchone()[0]
    
    db.cursor.execute("SELECT COUNT(*) FROM CardType")
    type_count = db.cursor.fetchone()[0]
    
    db.cursor.execute("SELECT COUNT(*) FROM SubType")
    subtype_count = db.cursor.fetchone()[0]
    
    print(f"\nDatabase Statistics:")
    print(f"Cards: {card_count}")
    print(f"Artists: {artist_count}")
    print(f"Sets: {set_count}")
    print(f"Colors: {color_count}")
    print(f"Card Types: {type_count}")
    print(f"Subtypes: {subtype_count}")
    
    # Verify unique artists
    db.cursor.execute("SELECT COUNT(DISTINCT ArtistName) FROM Artist")
    unique_artists = db.cursor.fetchone()[0]
    print(f"Unique Artists: {unique_artists}")
    
    # Show top artists by card count
    db.cursor.execute("""
        SELECT a.ArtistName, COUNT(c.CardID) as card_count
        FROM Artist a
        JOIN Card c ON a.ArtistID = c.ArtistID
        GROUP BY a.ArtistID, a.ArtistName
        ORDER BY card_count DESC
        LIMIT 5
    """)
    
    print(f"\nTop 5 Artists by Card Count:")
    for artist_name, count in db.cursor.fetchall():
        print(f"  {artist_name}: {count} cards")
    
    # Show cards per set
    db.cursor.execute("""
        SELECT cs.SetName, COUNT(c.CardID) as card_count
        FROM CardSet cs
        JOIN Card c ON cs.SetID = c.SetID
        GROUP BY cs.SetID, cs.SetName
        ORDER BY card_count DESC
    """)
    
    print(f"\nCards per Set:")
    for set_name, count in db.cursor.fetchall():
        print(f"  {set_name}: {count} cards")

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='MTG Database Population Tool')
    parser.add_argument('--clean', action='store_true', 
                       help='Clean existing database before populating')
    parser.add_argument('--sets', choices=['urzas', 'masques', 'invasion', 'all'], 
                       default='urzas', help='Which sets to populate')
    
    args = parser.parse_args()
    
    if args.clean:
        print("Starting MTG Database Clean and Population...")
        # Remove existing database file if it exists
        if os.path.exists("mtg_database.db"):
            os.remove("mtg_database.db")
            print("Removed existing database file")
    else:
        print("Starting MTG Database Population (incremental)...")
    
    # Initialize database
    db = MTGDatabase()
    db.connect()
    
    # Initialize API
    api = ScryfallAPI()
    
    # Determine which sets to fetch
    if args.sets == 'urzas':
        target_sets = api.get_urzas_block_sets()
        print(f"Fetching cards from Urza's block sets: {target_sets}")
    elif args.sets == 'masques':
        target_sets = api.get_masques_block_sets()
        print(f"Fetching cards from Masques block sets: {target_sets}")
    elif args.sets == 'invasion':
        target_sets = api.get_invasion_block_sets()
        print(f"Fetching cards from Invasion block sets: {target_sets}")
    else:  # all
        target_sets = api.get_all_target_sets()
        print(f"Fetching cards from all target sets: {target_sets}")
    
    total_cards = 0
    
    for set_code in target_sets:
        print(f"\nFetching cards from set: {set_code}")
        cards = api.get_cards_from_set(set_code)
        print(f"Found {len(cards)} cards in {set_code}")
        
        for card in cards:
            try:
                card_id = db.insert_card(card)
                total_cards += 1
                if total_cards % 10 == 0:
                    print(f"Processed {total_cards} cards...")
                    db.conn.commit()  # Periodic commits
            except Exception as e:
                print(f"Error inserting card {card.get('name', 'Unknown')}: {e}")
        
        db.conn.commit()  # Commit after each set
    
    print(f"\nDatabase population complete! Total cards inserted: {total_cards}")
    
    # Print comprehensive statistics
    print_database_statistics(db)
    
    db.close()

if __name__ == "__main__":
    main()
