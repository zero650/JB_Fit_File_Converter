import struct
import csv
import sys

def read_fit_file(filename):
    with open(filename, 'rb') as f:
        data = f.read()

    # Extract major version (2 bytes, big-endian)
    major_ver = struct.unpack('>H', data[0:2])[0]

    # Extract minor version (1 byte, big-endian)
    minor_ver = struct.unpack('>B', data[2:3])[0]

    # Extract revision count and size type (each 2 bytes, big-endian; total 4 bytes)
    rev_size_type = struct.unpack('>II', data[4:8])[0]  # First two bytes for revisions

    # Determine number of records (4 bytes, big-endian starting from position 8)
    num_records = struct.unpack('>I', data[8:12])[0]

    print(f"Major Version: {major_ver}")
    print(f"Minor Version: {minor_ver}")
    print(f"Revisions/Size Type: {rev_size_type}")
    print(f"Number of Records: {num_records}")

    return rev_size_type, major_ver, minor_ver, num_records

def main():
    filename = sys.argv[1]

    # Read the header
    _, _, _, num_records = read_fit_file(filename)

    activities = []  # Activity data extraction logic here

    headers = ['Major Version', 'Minor Version', 'Revisions/Size Type', 'Number of Records']
    for i in range(num_records):
        headers.append(f'Activity {i}')

    with open('output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(activities)

if __name__ == "__main__":
    main()