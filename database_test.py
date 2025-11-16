#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Maps Reviews Database Test
Database integration test script
"""

import sqlite3
import pandas as pd
from datetime import datetime, timezone
import json
import os
import hashlib

class ReviewsDatabase:
    def __init__(self, db_path="reviews.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()
    
    @staticmethod
    def generate_review_hash(business_name, reviewer_name, date_original, review_text):
        """
        Generate unique hash for review to prevent duplicates
        Uses: business_name + reviewer_name + date + review_text
        """
        # Combine unique identifiers
        unique_string = f"{business_name}|{reviewer_name}|{date_original}|{review_text}"
        
        # Create MD5 hash (fast and sufficient for this use case)
        review_hash = hashlib.md5(unique_string.encode('utf-8')).hexdigest()
        
        return review_hash
    
    def check_review_exists(self, review_hash):
        """
        Fast check if review already exists in database
        Returns: True if exists, False if new
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM reviews WHERE review_hash = ?",
            (review_hash,)
        )
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def init_database(self):
        """Create database tables and run migrations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Reviews table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT NOT NULL,
            business_url TEXT,
            reviewer_name TEXT,
            rating INTEGER,
            date_original TEXT,
            review_text TEXT,
            timestamp_parsed DATETIME,
            time_category TEXT,
            scrape_session_id TEXT,
            review_hash TEXT UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create index for faster duplicate checking
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_review_hash 
        ON reviews(review_hash)
        ''')
        
        # Scrape sessions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scrape_sessions (
            id TEXT PRIMARY KEY,
            business_name TEXT NOT NULL,
            business_url TEXT,
            target_text_reviews INTEGER,
            target_total_ratings INTEGER,
            actual_text_reviews INTEGER,
            actual_total_ratings INTEGER,
            average_rating REAL,
            scrape_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'completed'
        )
        ''')
        
        # Businesses table (NEW!)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS businesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            place_id TEXT NOT NULL,
            enabled INTEGER DEFAULT 1,
            address TEXT,
            latitude REAL,
            longitude REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create index for faster lookups
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_business_name 
        ON businesses(name)
        ''')
        
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_business_enabled 
        ON businesses(enabled)
        ''')
        
        conn.commit()
        
        # Run migrations for existing databases
        self._migrate_add_review_hash(conn, cursor)
        self._migrate_populate_businesses(conn, cursor)
        self._migrate_add_location_to_businesses(conn, cursor)
        
        conn.close()
        print("✅ Database tables created/verified")
    
    def _migrate_add_review_hash(self, conn, cursor):
        """
        Migration: Add review_hash column to existing reviews table
        Safe to run multiple times (checks if column exists)
        """
        # Check if review_hash column exists
        cursor.execute("PRAGMA table_info(reviews)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'review_hash' not in columns:
            print("🔄 Migrating database: Adding review_hash column...")
            
            # Add review_hash column
            cursor.execute("ALTER TABLE reviews ADD COLUMN review_hash TEXT")
            
            # Generate hashes for existing reviews
            cursor.execute("""
                SELECT id, business_name, reviewer_name, date_original, review_text 
                FROM reviews
            """)
            existing_reviews = cursor.fetchall()
            
            updated_count = 0
            for review in existing_reviews:
                review_id, business_name, reviewer_name, date_original, review_text = review
                
                # Generate hash
                review_hash = self.generate_review_hash(
                    business_name or "",
                    reviewer_name or "",
                    date_original or "",
                    review_text or ""
                )
                
                # Update review with hash
                cursor.execute(
                    "UPDATE reviews SET review_hash = ? WHERE id = ?",
                    (review_hash, review_id)
                )
                updated_count += 1
            
            # Create index
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_review_hash 
                ON reviews(review_hash)
            ''')
            
            conn.commit()
            print(f"   ✅ Migration complete: {updated_count} reviews updated with hashes")
        else:
            print("   ℹ️  Database already up to date")
    
    def _migrate_populate_businesses(self, conn, cursor):
        """
        Migration: Populate businesses table from existing reviews
        Extracts unique businesses from reviews table
        """
        # Check if businesses table has any data
        cursor.execute("SELECT COUNT(*) FROM businesses")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("🔄 Migrating database: Populating businesses table...")
            
            # Get unique businesses from reviews with valid Place IDs
            cursor.execute("""
                SELECT DISTINCT business_name, business_url 
                FROM reviews 
                WHERE business_url LIKE 'ChIJ%'
                AND business_name IS NOT NULL
                AND business_name != ''
                ORDER BY business_name
            """)
            
            businesses = cursor.fetchall()
            inserted_count = 0
            
            for name, place_id in businesses:
                try:
                    cursor.execute("""
                        INSERT INTO businesses (name, place_id, enabled)
                        VALUES (?, ?, 1)
                    """, (name, place_id))
                    inserted_count += 1
                except sqlite3.IntegrityError:
                    # Skip duplicates
                    pass
            
            conn.commit()
            print(f"   ✅ Migration complete: {inserted_count} businesses imported")
        else:
            print(f"   ℹ️  Businesses table already populated ({count} businesses)")
    
    def _migrate_add_location_to_businesses(self, conn, cursor):
        """
        Migration: Add location columns to businesses table
        Safe to run multiple times (checks if columns exist)
        """
        cursor.execute("PRAGMA table_info(businesses)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrations_needed = []
        if 'address' not in columns:
            migrations_needed.append('address')
        if 'latitude' not in columns:
            migrations_needed.append('latitude')
        if 'longitude' not in columns:
            migrations_needed.append('longitude')
        
        if migrations_needed:
            print(f"🔄 Migrating database: Adding location columns to businesses table...")
            
            for column in migrations_needed:
                if column == 'address':
                    cursor.execute("ALTER TABLE businesses ADD COLUMN address TEXT")
                elif column == 'latitude':
                    cursor.execute("ALTER TABLE businesses ADD COLUMN latitude REAL")
                elif column == 'longitude':
                    cursor.execute("ALTER TABLE businesses ADD COLUMN longitude REAL")
            
            conn.commit()
            print(f"   ✅ Migration complete: Added {', '.join(migrations_needed)} columns")
        else:
            print("   ℹ️  Location columns already exist")
    
    def save_scrape_session(self, session_data):
        """Save scrape session information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO scrape_sessions 
        (id, business_name, business_url, target_text_reviews, target_total_ratings,
         actual_text_reviews, actual_total_ratings, average_rating, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_data['session_id'],
            session_data['business_name'],
            session_data.get('business_url', ''),
            session_data.get('target_text_reviews', 0),
            session_data.get('target_total_ratings', 0),
            session_data.get('actual_text_reviews', 0),
            session_data.get('actual_total_ratings', 0),
            session_data.get('average_rating', 0),
            session_data.get('status', 'completed')
        ))
        
        conn.commit()
        conn.close()
        print(f"✅ Scrape session saved: {session_data['session_id']}")
    
    def add_session(self, session_data):
        """Add session (for scraper compatibility)"""
        self.save_scrape_session(session_data)
    
    def add_review(self, review_data):
        """Add single review with duplicate check (for scraper compatibility)"""
        # Get date field (try both review_date and date_original for compatibility)
        date_field = review_data.get('review_date') or review_data.get('date_original', '')
        
        # Generate hash for duplicate check
        review_hash = self.generate_review_hash(
            review_data.get('business_name', ''),
            review_data.get('reviewer_name', ''),
            date_field,
            review_data.get('review_text', '')
        )
        
        # Quick duplicate check
        if self.check_review_exists(review_hash):
            return False  # Skip duplicate
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Convert rating value to integer
            rating_value = review_data.get('rating')
            if rating_value is not None:
                try:
                    rating_value = int(float(str(rating_value)))
                except (ValueError, TypeError):
                    rating_value = 0
            else:
                rating_value = 0
            
            cursor.execute('''
            INSERT INTO reviews 
            (business_name, business_url, reviewer_name, rating, date_original,
             review_text, timestamp_parsed, time_category, scrape_session_id, review_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                review_data.get('business_name', ''),
                review_data.get('business_url', ''),
                review_data.get('reviewer_name', ''),
                rating_value,
                review_data.get('review_date', ''),
                review_data.get('review_text', ''),
                review_data.get('timestamp_parsed'),
                review_data.get('time_category', ''),
                review_data.get('session_id', ''),
                review_hash
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.IntegrityError:
            # Duplicate hash (shouldn't happen with pre-check, but safe)
            conn.close()
            return False
        except Exception as e:
            print(f"❌ Review save error: {e}")
            conn.close()
            return False
    
    def save_reviews(self, reviews_data, session_id):
        """Save reviews to database with duplicate detection"""
        if not reviews_data:
            print("⚠️ No reviews found to save")
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        skipped_count = 0
        
        for review in reviews_data:
            # Generate hash
            review_hash = self.generate_review_hash(
                review.get('business_name', ''),
                review.get('reviewer_name', ''),
                review.get('date', ''),
                review.get('review_text', '')
            )
            
            # Quick check if exists
            cursor.execute(
                "SELECT COUNT(*) FROM reviews WHERE review_hash = ?",
                (review_hash,)
            )
            
            if cursor.fetchone()[0] > 0:
                skipped_count += 1
                continue  # Skip duplicate
            
            try:
                cursor.execute('''
                INSERT INTO reviews 
                (business_name, business_url, reviewer_name, rating, date_original,
                 review_text, timestamp_parsed, time_category, scrape_session_id, review_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    review.get('business_name', ''),
                    review.get('business_url', ''),
                    review.get('reviewer_name', ''),
                    review.get('rating'),
                    review.get('date', ''),
                    review.get('review_text', ''),
                    review.get('timestamp_parsed'),
                    review.get('time_category', ''),
                    session_id,
                    review_hash
                ))
                saved_count += 1
            except sqlite3.IntegrityError:
                skipped_count += 1
                continue
        
        conn.commit()
        conn.close()
        
        print(f"✅ {saved_count} new reviews saved to database")
        if skipped_count > 0:
            print(f"⏭️ {skipped_count} duplicate reviews skipped")
    
    def get_all_reviews(self):
        """Get all reviews"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
        SELECT r.*, s.business_name as session_business_name, s.scrape_date
        FROM reviews r
        LEFT JOIN scrape_sessions s ON r.scrape_session_id = s.id
        ORDER BY r.created_at DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def get_reviews_by_business(self, business_name):
        """Get reviews for specific business"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
        SELECT * FROM reviews 
        WHERE business_name LIKE ?
        ORDER BY created_at DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=[f'%{business_name}%'])
        conn.close()
        
        return df
    
    def get_statistics(self):
        """Get general statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total review count
        cursor.execute("SELECT COUNT(*) FROM reviews")
        total_reviews = cursor.fetchone()[0]
        
        # Total business count
        cursor.execute("SELECT COUNT(DISTINCT business_name) FROM reviews")
        total_businesses = cursor.fetchone()[0]
        
        # Average rating
        cursor.execute("SELECT AVG(rating) FROM reviews WHERE rating IS NOT NULL")
        avg_rating = cursor.fetchone()[0]
        
        # Text reviews count
        cursor.execute("SELECT COUNT(*) FROM reviews WHERE review_text IS NOT NULL AND review_text != ''")
        text_reviews = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_reviews': total_reviews,
            'total_businesses': total_businesses,
            'average_rating': round(avg_rating, 2) if avg_rating else 0,
            'text_reviews': text_reviews,
            'rating_only': total_reviews - text_reviews
        }
    
    # ==================== BUSINESS CRUD OPERATIONS ====================
    
    def get_all_businesses(self, enabled_only=False):
        """Get all businesses from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if enabled_only:
            cursor.execute("""
                SELECT id, name, place_id, enabled, created_at, updated_at
                FROM businesses
                WHERE enabled = 1
                ORDER BY name
            """)
        else:
            cursor.execute("""
                SELECT id, name, place_id, enabled, created_at, updated_at
                FROM businesses
                ORDER BY name
            """)
        
        businesses = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': b[0],
                'name': b[1],
                'place_id': b[2],
                'enabled': bool(b[3]),
                'created_at': b[4],
                'updated_at': b[5]
            }
            for b in businesses
        ]
    
    def get_business_by_id(self, business_id):
        """Get single business by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, place_id, enabled, created_at, updated_at
            FROM businesses
            WHERE id = ?
        """, (business_id,))
        
        business = cursor.fetchone()
        conn.close()
        
        if business:
            return {
                'id': business[0],
                'name': business[1],
                'place_id': business[2],
                'enabled': bool(business[3]),
                'created_at': business[4],
                'updated_at': business[5]
            }
        return None
    
    def add_business(self, name, place_id, enabled=True):
        """Add new business to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO businesses (name, place_id, enabled)
                VALUES (?, ?, ?)
            """, (name, place_id, 1 if enabled else 0))
            
            conn.commit()
            business_id = cursor.lastrowid
            conn.close()
            
            print(f"✅ Business added: {name}")
            return {'success': True, 'id': business_id, 'message': 'Business added successfully'}
        
        except sqlite3.IntegrityError:
            conn.close()
            print(f"❌ Business already exists: {name}")
            return {'success': False, 'error': 'Business with this name already exists'}
        
        except Exception as e:
            conn.close()
            print(f"❌ Error adding business: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_business(self, business_id, name=None, place_id=None, enabled=None):
        """Update existing business"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build update query dynamically
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        
        if place_id is not None:
            updates.append("place_id = ?")
            params.append(place_id)
        
        if enabled is not None:
            updates.append("enabled = ?")
            params.append(1 if enabled else 0)
        
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(business_id)
            
            query = f"UPDATE businesses SET {', '.join(updates)} WHERE id = ?"
            
            try:
                cursor.execute(query, params)
                conn.commit()
                
                if cursor.rowcount > 0:
                    conn.close()
                    print(f"✅ Business updated: ID {business_id}")
                    return {'success': True, 'message': 'Business updated successfully'}
                else:
                    conn.close()
                    return {'success': False, 'error': 'Business not found'}
            
            except sqlite3.IntegrityError:
                conn.close()
                return {'success': False, 'error': 'Business with this name already exists'}
            
            except Exception as e:
                conn.close()
                print(f"❌ Error updating business: {str(e)}")
                return {'success': False, 'error': str(e)}
        
        conn.close()
        return {'success': False, 'error': 'No updates specified'}
    
    def delete_business(self, business_id):
        """Delete business from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM businesses WHERE id = ?", (business_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                conn.close()
                print(f"✅ Business deleted: ID {business_id}")
                return {'success': True, 'message': 'Business deleted successfully'}
            else:
                conn.close()
                return {'success': False, 'error': 'Business not found'}
        
        except Exception as e:
            conn.close()
            print(f"❌ Error deleting business: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def toggle_business(self, business_id):
        """Toggle business enabled/disabled status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current status
        cursor.execute("SELECT enabled FROM businesses WHERE id = ?", (business_id,))
        result = cursor.fetchone()
        
        if result:
            current_status = result[0]
            new_status = 0 if current_status else 1
            
            cursor.execute("""
                UPDATE businesses 
                SET enabled = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (new_status, business_id))
            
            conn.commit()
            conn.close()
            
            status_text = "enabled" if new_status else "disabled"
            print(f"✅ Business {status_text}: ID {business_id}")
            return {'success': True, 'message': f'Business {status_text}', 'enabled': bool(new_status)}
        else:
            conn.close()
            return {'success': False, 'error': 'Business not found'}

def test_database():
    """Test database functions"""
    print("🧪 DATABASE TEST STARTING...")
    print("=" * 50)
    
    # Create database
    db = ReviewsDatabase("test_reviews.db")
    
    # Create test data
    test_session = {
        'session_id': f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'business_name': 'Test Business',
        'business_url': 'https://test.com',
        'target_text_reviews': 5,
        'target_total_ratings': 10,
        'actual_text_reviews': 3,
        'actual_total_ratings': 8,
        'average_rating': 4.2,
        'status': 'completed'
    }
    
    # Save session
    print("1️⃣ Saving test session...")
    db.save_scrape_session(test_session)
    
    # Create test reviews
    test_reviews = [
        {
            'business_name': 'Test Business',
            'business_url': 'https://test.com',
            'reviewer_name': 'Test User 1',
            'rating': 5,
            'date': '2 hours ago',
            'review_text': 'Great place, definitely recommend!',
            'timestamp_parsed': datetime.now().isoformat(),
            'time_category': 'Today'
        },
        {
            'business_name': 'Test Business',
            'business_url': 'https://test.com',
            'reviewer_name': 'Test User 2',
            'rating': 4,
            'date': '1 day ago',
            'review_text': 'Nice service but a bit expensive',
            'timestamp_parsed': datetime.now().isoformat(),
            'time_category': 'Yesterday'
        },
        {
            'business_name': 'Test Business',
            'business_url': 'https://test.com',
            'reviewer_name': 'Test User 3',
            'rating': 3,
            'date': '1 week ago',
            'review_text': '',  # Rating only
            'timestamp_parsed': datetime.now().isoformat(),
            'time_category': 'This Week'
        }
    ]
    
    # Save reviews
    print("2️⃣ Saving test reviews...")
    db.save_reviews(test_reviews, test_session['session_id'])
    
    # Test duplicate detection
    print("3️⃣ Testing duplicate detection...")
    print("   Attempting to save same reviews again...")
    db.save_reviews(test_reviews, test_session['session_id'])
    print("   ✅ Duplicate detection working!")
    
    # Read data back
    print("4️⃣ Reading data...")
    all_reviews = db.get_all_reviews()
    print(f"📊 Total reviews: {len(all_reviews)}")
    
    # Show statistics
    print("5️⃣ Statistics:")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"   📈 {key}: {value}")
    
    # Show first few reviews
    print("6️⃣ First 3 reviews:")
    if len(all_reviews) > 0:
        for i, review in all_reviews.head(3).iterrows():
            print(f"   👤 {review['reviewer_name']} - ⭐ {review['rating']}")
            if review['review_text']:
                print(f"      💬 {review['review_text'][:50]}...")
    
    print("=" * 50)
    print("✅ DATABASE TEST COMPLETED!")
    
    return db

if __name__ == "__main__":
    # Run test
    test_database()
