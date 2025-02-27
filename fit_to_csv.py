import struct
import csv

def read_fit_file(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    # Header fields: Activity type, start time, end time (example VLIs)
    header_length = 24
    if len(data) >= header_length:
        header = struct.unpack('<I*I*', data[:header_length])
        activity_type = header[0]
        start_time = header[1].decode('latin-1')
        end_time = header[2].decode('latin-1')
    else:
        return None, None, None, []
    
    # Read records
    record_count = struct.unpack('<I', data[header_length:header_length+4])[0]
    count = 0
    records = []
    while count < record_count:
        # Each record starts with a 2-byte integer (number of attributes)
        num_attributes = struct.unpack('<H', data[header_length + 4 * count:header_length + 4 * count + 2])[0]
        if num_attributes >= 13:
            break
        # Extract heart rate and calories burned
        heart_rate = int(data[header_length + 4 * count + 5]) if (num_attributes > 6) else None
        calories_burned = data[header_length + 4 * count + 7: header_length + 4 * count + 11].decode('latin-1') if (num_attributes > 7) else None
        
        records.append((heart_rate, calories_burned))
        count += 1
    
    return activity_type, start_time, end_time, records

def main():
    import sys
    filename = sys.argv[1]
    
    activity_type, start_time, end_time, records = read_fit_file(filename)
    
    if not records:
        print("No records found in the .fit file.")
        return
    
    heart_rate = []
    calories_burned = []
    
    for record in records:
        heart_rate.append(record[0])
        calories_burned.append(record[1])
    
    header = ['Heart Rate', 'Calories Burned']
    with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        
        for i in range(len(heart_rate)):
            writer.writerow([heart_rate[i], calories_burned[i]])

if __name__ == "__main__":
    main()