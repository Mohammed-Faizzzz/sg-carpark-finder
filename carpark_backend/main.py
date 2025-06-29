from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import math
import logging
import json
# import method from prep_data.py to get carpark data
from prep_data import load_carpark_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

carpark_data = None  # Global variable to store carpark data

if carpark_data is None:
    # Load carpark data from CSV file
    carpark_data = load_carpark_data('HDBCarparkInformation.csv')
    if not carpark_data:
        logger.error("Failed to load carpark data. Ensure the CSV file is correctly formatted and exists.")
        raise HTTPException(status_code=500, detail="Carpark data not available")

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

    
@app.get("/find-carpark")
async def find_nearest_carpark(postcode: str = Query(..., min_length=6, max_length=6, regex="^[0-9]{6}$")):
    
    # 1. Get Postcode Coordinates using OpenMap API (elasticsearch)
    logger.info(f"Received request for postcode: {postcode}")
    url = "https://www.onemap.gov.sg/api/common/elastic/search?searchVal={postcode}&returnGeom=Y&getAddrDetails=Y&pageNum=1"
      
    headers = {"Authorization": "Bearer **********************"}
            
    response = requests.get(url, headers=headers)

    # 2. Get Carpark Availability Data from Data.gov.sg
    carparks = []
    try:
        carpark_api_url = "https://api.data.gov.sg/v1/transport/carpark-availability"
        carpark_response = requests.get(carpark_api_url)
        carpark_response.raise_for_status() # Raise an exception for HTTP errors
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