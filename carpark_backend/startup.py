# Runs during application startup
# Import HDB carpark data and URA carpark data and store both in a dictionary
# Call realtime carpark availability API to get the latest carpark availability data

import csv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import math
import logging
import json
import os
from bs4 import BeautifulSoup
import logger

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

def load_HDB_carpark_data(file_path):
    carpark_data = {}
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                carpark_number = row['car_park_no']
                address = row['address']
                x_coord = float(row['x_coord'])
                y_coord = float(row['y_coord'])
                carpark_data[carpark_number] = {
                    'address': address,
                    'coordinates': (x_coord, y_coord),
                    'type': 'HDB',
                }
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
    return carpark_data

prep_data_file = './HDBCarparkInformation.csv'
carpark_data = load_HDB_carpark_data(prep_data_file)
print(f"Loaded {len(carpark_data)} carparks from {prep_data_file}")
print(list(carpark_data.keys())[:10])
print(list(carpark_data.values())[:10])

def parse_ura_feature(feature, carpark_data):
    """
    Parses a single URA GeoJSON feature to extract carpark details.
    Returns a dictionary of extracted properties and coordinates.
    """
    props = feature.get('properties', {})
    geometry = feature.get('geometry', {})

    carpark_info = {}

    # 1. Parse HTML Description using BeautifulSoup
    description_html = props.get('Description', '')
    if description_html:
        soup = BeautifulSoup(description_html, 'html.parser')
        for row in soup.find_all('tr'):
            cols = row.find_all(['th', 'td'])
            if len(cols) == 2:
                key = cols[0].get_text(strip=True)
                value = cols[1].get_text(strip=True)
                carpark_info[key] = value
    
    carpark_number = carpark_info.get('PP_CODE')
    if not carpark_number:
        # print(f"URA feature missing PP_CODE in description, skipping: {props.get('Name')}")
        return None

    # 2. Extract Coordinates (from Polygon geometry)
    # GeoJSON coordinates are [longitude, latitude, altitude] for a Point or first point of a Polygon
    lat, lng = None, None
    if geometry and geometry.get('type') == 'Polygon':
        coords = geometry.get('coordinates')
        if coords and len(coords) > 0 and len(coords[0]) > 0:
            # Use the first point of the outer ring as the carpark's representative point
            lng = coords[0][0][0]
            lat = coords[0][0][1]
        else:
            print(f"URA carpark {carpark_number} has empty or malformed coordinates, skipping.")
            return None
    elif geometry and geometry.get('type') == 'Point': # In case some URA data is Point
        coords = geometry.get('coordinates')
        if coords and len(coords) >= 2:
            lng = coords[0]
            lat = coords[1]
    
    if lat is None or lng is None:
        print(f"URA carpark {carpark_number} has no valid latitude/longitude, skipping.")
        return None
    
    if carpark_number in carpark_data:
        carpark_data[carpark_number]['total_lots_static'] += 1
    else:
        carpark_data[carpark_number] = {
            'address': carpark_info.get('PARKING_PL', 'N/A'),
            'coordinates': (lat, lng),
            'type': 'URA',
            'total_lots_static': 1
        }

def load_URA_carpark_data(file_path):
    ura_carparks = {}
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            geojson_data = json.load(file)
            
            if geojson_data.get('type') == 'FeatureCollection':
                for feature in geojson_data.get('features', []):
                    parse_ura_feature(feature, ura_carparks)
            else:
                print(f"Provided file {file_path} is not a valid GeoJSON FeatureCollection.")

    except FileNotFoundError:
        print(f"Error: The URA GeoJSON file {file_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} is not a valid JSON file.")
    except Exception as e:
        print(f"An error occurred while reading the URA GeoJSON file: {e}")
    return ura_carparks

prep_data_file_ura = './URAParkingLotGEOJSON.geojson'
ura_carpark_data = load_URA_carpark_data(prep_data_file_ura)
print(f"Loaded {len(ura_carpark_data)} URA carparks from {prep_data_file_ura}")
print(list(ura_carpark_data.keys())[:10])
print(list(ura_carpark_data.values())[:10])
