from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import math
import logging
import json
import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

ONEMAP_USERNAME = os.getenv('ONEMAP_USERNAME')
ONEMAP_PASSWORD = os.getenv('ONEMAP_PASSWORD')
onemap_access_token = os.getenv('ACCESS_TOKEN')
onemap_token_expiry = 0

# import method from prep_data.py to get carpark data
# from prep_data import load_carpark_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

carpark_data = None  # Global variable to store carpark data

# if carpark_data is None:
#     # Load carpark data from CSV file
#     carpark_data = load_carpark_data('HDBCarparkInformation.csv')
#     if not carpark_data:
#         logger.error("Failed to load carpark data. Ensure the CSV file is correctly formatted and exists.")
#         raise HTTPException(status_code=500, detail="Carpark data not available")

app = FastAPI(
    title="Singapore Carpark Finder API",
    description="API to find the nearest available public carpark by postcode in Singapore.",
    version="1.0.0",
)

# Configure CORS
# For development, allow all origins. In production, restrict this to frontend's domain.
origins = [
    "http://localhost",
    "http://localhost:3000",  # Create React App default port
    # Add deployed frontend URL here post-deployment of React app:
    # "https://frontend-app.netlify.app",
    # "https://Mohammed-Faizzzz.github.io" # If hosted on GitHub Pages (adjust path for repo name)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_onemap_token():
    global onemap_access_token, onemap_token_expiry
    import time

    # Check if token is still valid
    if onemap_access_token and onemap_token_expiry > time.time() + 300: # Refresh if less than 5 min to expiry
        logger.info("Using existing OneMap access token.")
        return onemap_access_token

    logger.info("Requesting new OneMap access token...")
    try:
        token_url = "https://www.onemap.gov.sg/api/auth/post/getToken" # Confirm this URL with OneMap docs
        response = requests.post(token_url, json={
            "email": ONEMAP_USERNAME,
            "password": ONEMAP_PASSWORD
        })
        response.raise_for_status()
        token_data = response.json()
        print("\nToken Response Data:", token_data)  # Debugging: Print the token response
        
        onemap_access_token = token_data.get('access_token')
        onemap_token_expiry = token_data.get('expiry_timestamp') # This is a Unix timestamp in milliseconds, need to convert
        
        if onemap_access_token and onemap_token_expiry:
            # Convert milliseconds to seconds for Python's time.time()
            onemap_token_expiry = int(onemap_token_expiry) / 1000.0
            logger.info(f"Successfully obtained OneMap access token. Expires at: {time.ctime(onemap_token_expiry)}")
            return onemap_access_token
        else:
            raise ValueError("Access token or expiry missing from OneMap response.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get OneMap access token: {e}")
        raise HTTPException(status_code=500, detail="Failed to authenticate with OneMap API.")
    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Error parsing OneMap token response: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse OneMap token response.")


@app.get("/find-carpark")
async def find_carpark(postcode: str = Query(..., min_length=6, max_length=6, regex="^[0-9]{6}$")):
    logger.info(f"Received request for postcode: {postcode}")

    user_lat, user_lng = None, None

    # Get OneMap access token
    token = await get_onemap_token()
    headers = {"Authorization": f"Bearer {token}"} # Use the obtained token in the header

    # 1. Get Postcode Coordinates from OneMap API
    try:
        onemap_url = f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={postcode}&returnGeom=Y&getAddrDetails=Y&pageNum=1"
        onemap_response = requests.get(onemap_url, headers=headers)
        onemap_response.raise_for_status()
        onemap_data = onemap_response.json()

        if onemap_data and onemap_data.get('results'):
            first_result = onemap_data['results'][0]
            user_lat = float(first_result.get('LATITUDE'))
            user_lng = float(first_result.get('LONGITUDE'))
            if user_lat is None or user_lng is None:
                 raise ValueError("Latitude or Longitude missing from OneMap response.")
            logger.info(f"OneMap: Postcode {postcode} geocoded to {user_lat}, {user_lng}")
        else:
            logger.warning(f"OneMap: No results found for postcode {postcode}")
            raise HTTPException(status_code=404, detail="Postcode not found or invalid.")
    except requests.exceptions.RequestException as e:
        logger.error(f"OneMap API request failed: {e}")
        raise HTTPException(status_code=500, detail="Error connecting to OneMap API.")
    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Error processing OneMap data for {postcode}: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred processing postcode data.")

    # 2. Get Carpark Availability Data from Data.gov.sg
    carparks = []
    try:
        carpark_api_url = "https://api.data.gov.sg/v1/transport/carpark-availability"
        carpark_response = requests.get(carpark_api_url)
        carpark_response.raise_for_status()
        carpark_data = carpark_response.json()
        # output to a json file for debugging
        print(len(carpark_data['items']))
        with open('carpark_data.json', 'w') as f:
            json.dump(carpark_data, f, indent=4)
        # print(carpark_data)  # Debugging: Print the carpark data to check its structure
    
    except Exception as e:
        logger.error(f"Error fetching carpark data: {e}")
        raise HTTPException(status_code=500, detail="Error fetching carpark data")
    finally:
        return None
    
    # 3. Calculate Nearest Available Carpark
    
    # 4. Return Nearest Carpark Details