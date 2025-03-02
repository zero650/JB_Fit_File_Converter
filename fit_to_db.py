from flask import Flask, render_template, request, redirect, url_for, flash
import os
import fitparse
from sqlalchemy import create_engine, MetaData, Table, Integer, String, Float, DateTime, Column
from sqlalchemy.orm import sessionmaker

# Flask app setup
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for flash messages

# PostgreSQL setup (replace with your actual credentials)
DATABASE_URL = "postgresql://postgres:Norman01!@localhost/fitness"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Table definition (use SQLAlchemy ORM)
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
              Column('activity_type', String)
)

# Make sure the table exists
metadata.create_all(engine)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    if file and file.filename.endswith('.fit'):
        filename = os.path.join('uploads', file.filename)
        file.save(filename)
        
        try:
            # Parse the .fit file
            fitfile = fitparse.FitFile(filename, data_processor=fitparse.StandardUnitsDataProcessor())

            # Iterate through each record in the .fit file
            for record in fitfile.get_messages('record'):
                # Extract relevant fields
                timestamp = record.get_value('timestamp')
                lat = record.get_value('latitude')
                lon = record.get_value('longitude')
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

                # Insert record into the database
                insert_data = {
                    'timestamp': timestamp,
                    'position_lat': lat,
                    'position_long': lon,
                    'distance': distance,
                    'enhanced_altitude': enhanced_altitude,
                    'altitude': altitude,
                    'enhanced_speed': enhanced_speed,
                    'speed': speed,
                    'heart_rate': heart_rate,
                    'temperature': temperature,
                    'cadence': cadence,
                    'fractional_cadence': fractional_cadence,
                    'vertical_oscillation': vertical_oscillation,
                    'stance_time_percent': stance_time_percent,
                    'stance_time': stance_time,
                    'activity_type': activity_type
                }

                # Insert the data into the table
                session.execute(table.insert().values(insert_data))
            
            # Commit the transaction
            session.commit()

            flash(f'File {file.filename} uploaded and processed successfully!')
            return redirect(url_for('index'))

        except Exception as e:
            flash(f'Error processing the file: {e}')
            session.rollback()

    flash('Invalid file type. Please upload a .fit file.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
