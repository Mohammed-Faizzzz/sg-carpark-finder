# convert HDBCarpakInformation.csv into a hashmap with the key as the carpark number,
# and address, x_coord, y_coord as a tuple in the value.

import csv

def load_carpark_data(file_path):
    carpark_data = {}
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                carpark_number = row['carpark_number']
                address = row['address']
                x_coord = float(row['x_coord'])
                y_coord = float(row['y_coord'])
                carpark_data[carpark_number] = {
                    'address': address,
                    'coordinates': (x_coord, y_coord)
                }
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
    return carpark_data

