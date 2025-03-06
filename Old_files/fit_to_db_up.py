from flask import Flask, request, render_template, redirect, url_for
import os
import fitparse
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Integer, String, Float, DateTime, Column
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

# Set the directory where uploaded files will be stored
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'fit'}

# SQLAlchemy connection parameters
params = {
    'host': "localhost",
    'database': "fitness",
    'user': "postgres",
    'password': "password!"
}

# Create SQLAlchemy engine
engine = create_engine(f'postgresql+psycopg2://{params["user"]}:{params["password"]}@{params["host"]}/{params["database"]}')
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

metadata.create_all(bind=engine)

# Create session
Session = sessionmaker(bind=engine)
session = Session()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    
    if file and allowed_file(file.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        # Process the .fit file and insert into the database
        process_fit_file(filename)
        
        return 'File successfully uploaded and processed'
    else:
        return 'Invalid file type. Only .fit files are allowed.'

def process_fit_file(file_path):
    try:
        # Parse .fit file
        fitfile = fitparse.FitFile(file_path, data_processor=fitparse.StandardUnitsDataProcessor())
        
        for record in fitfile.get_messages('record'):
            if not hasattr(record, 'latitude') or not hasattr(record, 'longitude'):
                continue  # Skip records without latitude/longitude
            
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
        print(f"Error processing .fit file: {e}")

if __name__ == "__main__":
    app.run(debug=True)
