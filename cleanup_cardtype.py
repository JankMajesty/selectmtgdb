#!/usr/bin/env python3
"""
Script to remove the "//" card type from the CardType table.
This will remove the card type but preserve the cards that were associated with it.
"""

import sqlite3
import sys

def cleanup_double_slash_cardtype(db_path: str = "mtg_database.db"):
    """Remove the '//' card type from CardType table while preserving associated cards."""
    
    print("Starting cleanup of '//' card type...")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # First, let's see what we're working with
        cursor.execute("SELECT CardTypeID FROM CardType WHERE TypeName = '//'")
        result = cursor.fetchone()
        
        if not result:
            print("No '//' card type found in the database.")
            return
        
        cardtype_id = result[0]
        print(f"Found '//' card type with ID: {cardtype_id}")
        
        # Check how many cards are associated with this type
        cursor.execute("SELECT COUNT(*) FROM Card_CardType WHERE CardTypeID = ?", (cardtype_id,))
        card_count = cursor.fetchone()[0]
        print(f"Found {card_count} cards associated with '//' card type")
        
        if card_count > 0:
            # Show which cards will be affected
            cursor.execute("""
                SELECT c.CardName, c.CardID 
                FROM Card c 
                JOIN Card_CardType cct ON c.CardID = cct.CardID 
                WHERE cct.CardTypeID = ?
                ORDER BY c.CardName
            """, (cardtype_id,))
            
            affected_cards = cursor.fetchall()
            print(f"\nCards that will lose the '//' type association:")
            for card_name, card_id in affected_cards:
                print(f"  - {card_name} (ID: {card_id})")
        
        # Confirm before proceeding
        response = input(f"\nProceed with removing '//' card type? This will remove {card_count} card-type associations. (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            return
        
        # Step 1: Remove all associations between cards and the "//" card type
        cursor.execute("DELETE FROM Card_CardType WHERE CardTypeID = ?", (cardtype_id,))
        deleted_associations = cursor.rowcount
        print(f"Removed {deleted_associations} card-type associations")
        
        # Step 2: Remove the "//" card type from CardType table
        cursor.execute("DELETE FROM CardType WHERE CardTypeID = ?", (cardtype_id,))
        deleted_types = cursor.rowcount
        print(f"Removed {deleted_types} card type record")
        
        # Commit the changes
        conn.commit()
        print("✅ Cleanup completed successfully!")
        
        # Verify the cleanup
        cursor.execute("SELECT COUNT(*) FROM CardType WHERE TypeName = '//'")
        remaining_types = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Card_CardType WHERE CardTypeID = ?", (cardtype_id,))
        remaining_associations = cursor.fetchone()[0]
        
        print(f"\nVerification:")
        print(f"  - '//' card types remaining: {remaining_types}")
        print(f"  - Associations with old CardTypeID {cardtype_id}: {remaining_associations}")
        
        if remaining_types == 0 and remaining_associations == 0:
            print("✅ Cleanup verified - all '//' card type data removed")
        else:
            print("⚠️  Warning: Some data may not have been cleaned up properly")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        conn.rollback()
        sys.exit(1)
        
    finally:
        conn.close()

def show_cardtype_stats(db_path: str = "mtg_database.db"):
    """Show current card type statistics."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\nCurrent CardType table contents:")
        cursor.execute("""
            SELECT ct.CardTypeID, ct.TypeName, COUNT(cct.CardID) as card_count
            FROM CardType ct
            LEFT JOIN Card_CardType cct ON ct.CardTypeID = cct.CardTypeID
            GROUP BY ct.CardTypeID, ct.TypeName
            ORDER BY ct.TypeName
        """)
        
        results = cursor.fetchall()
        print(f"{'ID':<4} {'Type Name':<20} {'Card Count':<10}")
        print("-" * 35)
        for cardtype_id, type_name, card_count in results:
            print(f"{cardtype_id:<4} {type_name:<20} {card_count:<10}")
            
    finally:
        conn.close()

if __name__ == "__main__":
    print("MTG Database CardType Cleanup Tool")
    print("=" * 40)
    
    # Show current stats
    show_cardtype_stats()
    
    # Perform cleanup
    cleanup_double_slash_cardtype()
    
    # Show final stats
    print("\nFinal state:")
    show_cardtype_stats()
