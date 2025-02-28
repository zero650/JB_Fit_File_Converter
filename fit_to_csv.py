import csv
import os
import pytz
from fitparse import FitFile

allowed_fields = ['timestamp','position_lat','position_long', 'distance',
'enhanced_power_total','enhanced_heart_rate_count','hrv_algorithm']
header_keys = ['timestamp', 'position_lat', 'position_long', 'distance']

def convert_to_csv(file):
    file_data = {}
    
    for message in file.get_messages():
        if message.key == 'activity':
            activity_type = message.value
        elif message.key == 'heart_rate':
            heart_rate = message.value
        elif message.key == 'position_lat' or message.key == 'position_long':
            position = (message.value[0], message.value[1])
            file_data[position] = []
        
    # Add header keys if necessary
    for key in header_keys:
        if key not in file_data:
            file_data[key] = []
    
    csv_data = {}
    
    for position, values in file_data.items():
        csv_data[position] = {key: value for key, value in zip(header_keys, [0]*len(header_keys))}
        
        # Handle enhanced fields
        if message.key == 'enhanced_power_total':
            csv_data[position]['distance'] += message.value
        elif message.key == 'enhanced_heart_rate_count' and activity_type == 'running':
            csv_data[position]['hrv_algorithm'] = 1
    
    return csv_data

def write_csv_to_file(file_name, data):
    with open(file_name, 'w', newline='') as csvfile:
        fieldnames = header_keys
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write CSV header
        writer.writeheader()
        
        for position in data.keys():
            values = data[position]
            
            # Handle enhanced fields
            if 'distance' not in values:
                values['distance'] = 0
            
            if 'hrv_algorithm' not in values:
                values['hrv_algorithm'] = 0
            
            writer.writerow(values)

def convert_fit_to_csv(fit_file_name):
    csv_file_name = f"{fit_file_name}.csv"
    
    with open(fit_file_name, 'rb') as fit_file:
        file_data = FitFile(fit_file).process_messages()
        
    data = convert_to_csv(file_data)
    
    write_csv_to_file(csv_file_name, data)

convert_fit_to_csv('data.fit')