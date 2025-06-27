from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import math
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


    # 1. Get Postcode Coordinates

    # 2. Get Carpark Availability Data from Data.gov.sg
    
    # 3. Calculate Nearest Available Carpark
    
    # 4. Return Nearest Carpark Details