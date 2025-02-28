import os
import fitparse
from datetime import datetime, timezone
import sys
from sqlalchemy import create_engine, MetaData, Table, Integer, String, Float, DateTime, Column
from sqlalchemy.orm import sessionmaker

def main():
    params = {
        'host': "localhost",
        'database': "fitness",
        'user': "postgres",
        'password': "Norman01!"
    }
    
    # Create SQLAlchemy engine
    engine = create_engine(f'postgresql+psycopg2://{params["user"]}:{params["password"]}@{params["host"]}/{params["database"]}')
    
    try:
        # Connect to the PostgreSQL database using SQLAlchemy
        print("Connecting to PostgreSQL database...")
        conn = engine.connect()
        metadata = MetaData()
        
        # Define table schema
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
                     Column('activity_type', String)
                     )

        # Create table if it doesn't exist
        metadata.create_all(bind=engine)
        
        # Set up sessionmaker
        Session = sessionmaker(bind=engine)
        session = Session()

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
            for record in fitfile.get_messages('record'):
                if not hasattr(record, 'latitude') or not hasattr(record, 'longitude'):
                    continue  # Skip records without latitude/longitude
                
                # Create a new record object for insertion
                obj = {
                    'timestamp': record.timestamp,
                    'position_lat': record.latitude,
                    'position_long': record.longitude,
                    'distance': record.distance,
                    'enhanced_altitude': record.enhanced_altitude,
                    'altitude': record.altitude,
                    'enhanced_speed': record.enhanced_speed,
                    'speed': record.speed,
                    'heart_rate': record.heart_rate,
                    'temperature': record.temperature,
                    'cadence': record.cadence,
                    'fractional_cadence': record.fractional_cadence,
                    'vertical_oscillation': record.vertical_oscillation,
                    'stance_time_percent': record.stance_time_percent,
                    'stance_time': record.stance_time,
                    'activity_type': record.activity_type
                }
                
                # Insert record into the database
                try:
                    session.execute(table.insert().values(obj))
                    session.commit()
                except Exception as e:
                    print(f"Error inserting record: {e}")
                    session.rollback()

        except Exception as e:
            print(f"Error reading {file}: {e}")

    session.close()
    conn.close()

if __name__ == "__main__":
    main()
