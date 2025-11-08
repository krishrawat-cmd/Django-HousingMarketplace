import os
import sys
import csv
import sqlite3
import pyodbc
from django.core.wsgi import get_wsgi_application

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_project.settings')
application = get_wsgi_application()

# Import Django models
from members.models import User, Listing, Booking, Review, Message, Payment, Favorite, ListingImage

def connect_to_sql_server(server, database, username=None, password=None):
    """Connect to SQL Server database"""
    # For SQL Server Authentication
    if username and password:
        conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    # For Windows Authentication
    else:
        conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as e:
        print(f"Error connecting to SQL Server: {e}")
        sys.exit(1)

def migrate_users(sql_conn, django_db):
    """Migrate users from SQL Server to Django"""
    cursor = sql_conn.cursor()
    cursor.execute("SELECT id, name, email, password_hash, phone_number, profile_picture, bio, created_at, updated_at FROM [dbo].[Users]")
    
    users = cursor.fetchall()
    for user in users:
        User.objects.create(
            id=user[0],
            name=user[1],
            email=user[2],
            password_hash=user[3],
            phone_number=user[4],
            profile_picture=user[5],
            bio=user[6],
            created_at=user[7],
            updated_at=user[8]
        )
    print(f"Migrated {len(users)} users")

def migrate_listings(sql_conn, django_db):
    """Migrate listings from SQL Server to Django"""
    cursor = sql_conn.cursor()
    cursor.execute("SELECT id, user_id, title, description, price_per_night, address, city, state, country, zip_code, latitude, longitude, bedrooms, bathrooms, max_guests, has_kitchen, has_wifi, has_tv, has_heating, has_air_conditioning, created_at, updated_at FROM [dbo].[Listings]")
    
    listings = cursor.fetchall()
    for listing in listings:
        try:
            user = User.objects.get(id=listing[1])
            Listing.objects.create(
                id=listing[0],
                user=user,
                title=listing[2],
                description=listing[3],
                price_per_night=listing[4],
                address=listing[5],
                city=listing[6],
                state=listing[7],
                country=listing[8],
                zip_code=listing[9],
                latitude=listing[10],
                longitude=listing[11],
                bedrooms=listing[12],
                bathrooms=listing[13],
                max_guests=listing[14],
                has_kitchen=listing[15],
                has_wifi=listing[16],
                has_tv=listing[17],
                has_heating=listing[18],
                has_air_conditioning=listing[19],
                created_at=listing[20],
                updated_at=listing[21]
            )
        except User.DoesNotExist:
            print(f"User with ID {listing[1]} does not exist. Skipping listing {listing[0]}")
    
    print(f"Migrated {len(listings)} listings")

def migrate_bookings(sql_conn, django_db):
    """Migrate bookings from SQL Server to Django"""
    cursor = sql_conn.cursor()
    cursor.execute("SELECT id, user_id, listing_id, check_in_date, check_out_date, total_price, status, created_at, updated_at FROM [dbo].[Bookings]")
    
    bookings = cursor.fetchall()
    for booking in bookings:
        try:
            user = User.objects.get(id=booking[1])
            listing = Listing.objects.get(id=booking[2])
            
            Booking.objects.create(
                id=booking[0],
                user=user,
                listing=listing,
                check_in_date=booking[3],
                check_out_date=booking[4],
                total_price=booking[5],
                status=booking[6],
                created_at=booking[7],
                updated_at=booking[8]
            )
        except (User.DoesNotExist, Listing.DoesNotExist) as e:
            print(f"Error migrating booking {booking[0]}: {e}")
    
    print(f"Migrated {len(bookings)} bookings")

def migrate_reviews(sql_conn, django_db):
    """Migrate reviews from SQL Server to Django"""
    cursor = sql_conn.cursor()
    cursor.execute("SELECT id, user_id, listing_id, rating, comment, created_at, updated_at FROM [dbo].[Reviews]")
    
    reviews = cursor.fetchall()
    for review in reviews:
        try:
            user = User.objects.get(id=review[1])
            listing = Listing.objects.get(id=review[2])
            
            Review.objects.create(
                id=review[0],
                user=user,
                listing=listing,
                rating=review[3],
                comment=review[4],
                created_at=review[5],
                updated_at=review[6]
            )
        except (User.DoesNotExist, Listing.DoesNotExist) as e:
            print(f"Error migrating review {review[0]}: {e}")
    
    print(f"Migrated {len(reviews)} reviews")

def migrate_favorites(sql_conn, django_db):
    """Migrate favorites from SQL Server to Django"""
    cursor = sql_conn.cursor()
    cursor.execute("SELECT id, user_id, listing_id, created_at FROM [dbo].[Favorites]")
    
    favorites = cursor.fetchall()
    for favorite in favorites:
        try:
            user = User.objects.get(id=favorite[1])
            listing = Listing.objects.get(id=favorite[2])
            
            Favorite.objects.create(
                id=favorite[0],
                user=user,
                listing=listing,
                created_at=favorite[3]
            )
        except (User.DoesNotExist, Listing.DoesNotExist) as e:
            print(f"Error migrating favorite {favorite[0]}: {e}")
    
    print(f"Migrated {len(favorites)} favorites")

def main():
    # Get SQL Server connection details
    server = input("Enter SQL Server name (e.g., localhost\SQLEXPRESS): ")
    database = input("Enter database name (e.g., hoouse_db): ")
    auth_type = input("Use SQL Server Authentication? (y/n): ").lower()
    
    if auth_type == 'y':
        username = input("Enter SQL Server username: ")
        password = input("Enter SQL Server password: ")
        sql_conn = connect_to_sql_server(server, database, username, password)
    else:
        sql_conn = connect_to_sql_server(server, database)
    
    # Migrate data
    print("Starting data migration...")
    migrate_users(sql_conn, None)
    migrate_listings(sql_conn, None)
    migrate_bookings(sql_conn, None)
    migrate_reviews(sql_conn, None)
    migrate_favorites(sql_conn, None)
    
    print("Migration completed successfully!")

if __name__ == "__main__":
    main()