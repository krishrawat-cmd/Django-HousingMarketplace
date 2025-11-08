# SQL Server to Django Migration Guide

## Overview

This guide provides instructions for migrating data from a SQL Server database to your Django application. The migration process involves:

1. Setting up the Django models (completed)
2. Creating migration files (completed)
3. Applying migrations (completed)
4. Transferring data from SQL Server to Django

## Prerequisites

Before running the migration script, ensure you have the following installed:

```
pip install pyodbc
```

You'll also need the SQL Server ODBC driver installed on your system.

## Migration Process

### 1. Models Setup (Completed)

The Django models have been created in `members/models.py` based on the SQL Server database schema. These models include:

- User
- Listing
- Booking
- Review
- Message
- Payment
- Favorite
- ListingImage

### 2. Migration Files (Completed)

Migration files have been created using:

```
python manage.py makemigrations members
```

### 3. Apply Migrations (Completed)

Migrations have been applied using:

```
python manage.py migrate
```

### 4. Data Migration

To transfer data from SQL Server to Django:

1. Run the migration script:

```
python migrate_data.py
```

2. Follow the prompts to provide SQL Server connection details:
   - Server name (e.g., localhost\SQLEXPRESS)
   - Database name (e.g., hoouse_db)
   - Authentication type (SQL Server or Windows)
   - Username and password (if using SQL Server Authentication)

3. The script will migrate data for the following tables:
   - Users
   - Listings
   - Bookings
   - Reviews
   - Favorites

## Troubleshooting

### Common Issues

1. **Connection Errors**:
   - Verify SQL Server is running
   - Check server name and credentials
   - Ensure firewall allows connections

2. **Missing Dependencies**:
   - Install required packages: `pip install pyodbc`
   - Install SQL Server ODBC drivers

3. **Data Type Mismatches**:
   - If you encounter data type errors, you may need to modify the migration script to handle specific data conversions

### Manual Data Import

If the automatic migration fails, you can export data from SQL Server as CSV files and import them manually:

1. Export tables from SQL Server to CSV
2. Use Django's ORM or the `sqlite3` module to import the data

## Next Steps

After migration:

1. Verify data integrity by checking record counts and sample records
2. Update Django's authentication system if you plan to use Django's built-in User model
3. Run tests to ensure your application works with the migrated data

## Notes

- The migration script preserves original IDs from SQL Server
- Foreign key relationships are maintained
- The script handles basic error cases (e.g., missing related records)