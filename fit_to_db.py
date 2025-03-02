import os
from flask import Flask, request, render_template, redirect, url_for, flash
import fitparse
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Database setup
DATABASE_URL = "postgresql://postgres:Norman01!@localhost/fitness"  # Update with your credentials
engine = create_engine(DATABASE_URL, echo=True)  # Set echo=True to see SQL queries being executed
metadata = MetaData()

# Define the table schema
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

# Create the table if it doesn't exist
metadata.create_all(bind=engine)

# Create a sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

# Flask Setup
app = Flask(__name__)
app.secret_key = 'supersecretkey'

def process_fit_file(file_path):
    """Process the .fit file and add data to the database."""
    try:
        print(f"Processing {file_path}...")
        fitfile = fitparse.FitFile(file_path, data_processor=fitparse.StandardUnitsDataProcessor())
        
        for record in fitfile.get_messages('record'):
            # Extract latitude and longitude from the record fields
            lat = record.get_value('latitude')
            lon = record.get_value('longitude')

            # Print out the data for debugging
            print(f"Record Data: {record}")
            print(f"Latitude: {lat}, Longitude: {lon}")

            # Skip records without lat/lon
            if lat is None or lon is None:
                print(f"Skipping record due to missing lat/lon: {record}")
                continue  # Skip this record if lat/lon is missing

            # Extract other fields from the record
            timestamp = record.get_value('timestamp')
            distance = record.get_value('distance')
            enhanced_altitude = record.get_value('enhanced_altitude')
            altitude = record.get_value('altitude')
            enhanced_speed = record.get_value('enhanced_speed')
            speed = record.get_value('speed')
            heart_rate = record.get_value('heart_rate')
            temperature = record.get_value('temperature')
            cadence = record.get_value('cadence')
            fractional_cadence = record.get_value('fractional_cadence')
            vertical_oscillation = record.get_value('vertical_oscillation')
            stance_time_percent = record.get_value('stance_time_percent')
            stance_time = record.get_value('stance_time')
            activity_type = record.get_value('activity_type')

            # Prepare the data to be inserted into the database
            insert_data = {
                'timestamp': timestamp if timestamp else None,
                'position_lat': lat if lat else None,
                'position_long': lon if lon else None,
                'distance': distance if distance else None,
                'enhanced_altitude': enhanced_altitude if enhanced_altitude else None,
                'altitude': altitude if altitude else None,
                'enhanced_speed': enhanced_speed if enhanced_speed else None,
                'speed': speed if speed else None,
                'heart_rate': heart_rate if heart_rate else None,
                'temperature': temperature if temperature else None,
                'cadence': cadence if cadence else None,
                'fractional_cadence': fractional_cadence if fractional_cadence else None,
                'vertical_oscillation': vertical_oscillation if vertical_oscillation else None,
                'stance_time_percent': stance_time_percent if stance_time_percent else None,
                'stance_time': stance_time if stance_time else None,
                'activity_type': activity_type if activity_type else None
            }

            # Print out the data before inserting
            print(f"Data to insert: {insert_data}")

            # Insert the data into the database
            try:
                session.execute(table.insert().values(insert_data))
                session.commit()
                print(f"Inserted record: {insert_data}")  # Debug output
            except SQLAlchemyError as e:
                print(f"Error inserting data: {e}")
                session.rollback()  # In case of error, rollback the transaction

        print(f"Finished processing {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and file.filename.endswith('.fit'):
        # Save the uploaded file temporarily
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)
        
        # Process the uploaded .fit file
        process_fit_file(file_path)

        # Delete the temporary file after processing
        os.remove(file_path)

        flash('File successfully uploaded and processed!')
        return redirect(url_for('index'))

    else:
        flash('Invalid file type. Only .fit files are allowed.')
        return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
