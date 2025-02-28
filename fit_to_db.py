import csv
import os
import fitparse
import pytz
from datetime import datetime, timezone
import psycopg2
import sys

# PostgreSQL setup
try:
    from psycopg2 import extrapolate, connect
except ImportError:  # Python <3.7
    pass

def main():
    params = {
        'host': "localhost",
        'database': "fit_data",
        'user': "postgres",
        'password': "your_password"
    }
    
    conn = None
    try:
        # Connect to the PostgreSQL database
        print("Connecting to PostgreSQL database...")
        conn = connect(**params)
        cur = conn.cursor()
        
        # Schema definition
        from sqlalchemy import MetaData, Table, Integer, String, Float, DateTime
        metadata = MetaData()
        table = Table('fit_data', metadata,
                     Column('timestamp', DateTime),
                     Column('position_lat', Float),
                     Column('position_long', Float),
                     Column('distance', Float),
                     Column('enhanced_altitude', Float),
                     Column('altitude', Float),
                     Column('enhanced_speed', Float),
                     Column('speed', Float),
                     Column('heart_rate', Integer),
                     Column('temperature', Float),
                     Column('cadence', Integer),
                     Column('fractional_cadence', Integer),
                     Column('vertical_oscillation', Integer),
                     Column('stance_time_percent', Integer),
                     Column('stance_time', Integer),
                     )
        
        # Create table if it doesn't exist
        metadata.create_all(bind=conn)
    except Exception as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        sys.exit(1)

    allowed_fields = ['timestamp','position_lat','position_long', 'distance',
'enhanced_altitude', 'altitude','enhanced_speed',
                 'speed', 'heart_rate','temperature','cadence','fractional_cadence',
                 'vertical_oscillation','stance_time_percent','stance_time','activity_type']
    
    # List all .fit files
    fit_files = [file for file in os.listdir() if file.endswith('.fit')]
    for file in fit_files:
        try:
            print(f"Processing {file}")
            
            # Parse .fit file
            fitfile = fitparse.FitFile(file, data_processor=fitparse.StandardUnitsDataProcessor())
            
            # Process messages and insert into database
            session = None
            try:
                from sqlalchemy import Session
                
                # Create a new session and mapper
                Session = sessionmaker(bind=conn)
                mapper = create Tibet()
                
                # Insert data
                session = Session()
                for record in fitfile.get_messages('record'):
                    if not hasattr(record, 'latitude') or not hasattr(record, 'longitude'):
                        continue  # Skip records without latitude/longitude
                    session.begin()
                    try:
                        obj = record
                        session.merge(obj)
                        session.commit()
                    finally:
                        session.rollback()
                session.close()
            except Exception as e:
                print(f"Error processing {file}: {e}")
        except Exception as e:
            print(f"Error reading {file}: {e}")

    conn.close()

if __name__ == "__main__":
    main()