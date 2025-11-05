"""
🔧 Fix Ghost Business Names
Consolidates old "İstanbul Sabiha Gokcen Havalimani" reviews into "Sabiha Gokcen Airport"
"""

import sqlite3
from database_test import ReviewsDatabase

def fix_ghost_business():
    """Fix ghost business name in reviews table"""
    
    print("🔍 Checking for ghost business names...")
    
    db = ReviewsDatabase("reviews.db")
    df = db.get_all_reviews()
    
    # Get unique business names
    unique_businesses = df['business_name'].unique()
    print(f"\n📊 Current unique business names in reviews:")
    for idx, name in enumerate(unique_businesses, 1):
        count = len(df[df['business_name'] == name])
        print(f"  {idx}. {name} ({count} reviews)")
    
    # Check for ghost business
    ghost_name = "İstanbul Sabiha Gokcen Havalimani"
    correct_name = "Sabiha Gokcen Airport"
    
    if ghost_name in unique_businesses:
        ghost_count = len(df[df['business_name'] == ghost_name])
        print(f"\n⚠️  Found ghost business: '{ghost_name}' with {ghost_count} reviews")
        print(f"✅ Will rename to: '{correct_name}'")
        
        # Confirm
        response = input("\n🤔 Proceed with renaming? (y/n): ").strip().lower()
        
        if response == 'y':
            # Update using direct SQL
            conn = sqlite3.connect("reviews.db")
            cursor = conn.cursor()
            
            try:
                # Update business_name
                cursor.execute("""
                    UPDATE reviews 
                    SET business_name = ? 
                    WHERE business_name = ?
                """, (correct_name, ghost_name))
                
                updated_count = cursor.rowcount
                conn.commit()
                
                print(f"\n✅ Successfully updated {updated_count} reviews")
                print(f"   '{ghost_name}' → '{correct_name}'")
                
                # Verify
                cursor.execute("SELECT DISTINCT business_name FROM reviews")
                new_businesses = cursor.fetchall()
                
                print(f"\n📊 New unique business names:")
                for idx, (name,) in enumerate(new_businesses, 1):
                    cursor.execute("SELECT COUNT(*) FROM reviews WHERE business_name = ?", (name,))
                    count = cursor.fetchone()[0]
                    print(f"  {idx}. {name} ({count} reviews)")
                
                print("\n🎉 Ghost business fixed successfully!")
                
            except Exception as e:
                conn.rollback()
                print(f"\n❌ Error: {str(e)}")
            
            finally:
                conn.close()
        else:
            print("\n⏭️  Skipped")
    else:
        print(f"\n✅ No ghost business found. All good!")
        print(f"   (Looking for: '{ghost_name}')")

if __name__ == "__main__":
    fix_ghost_business()
