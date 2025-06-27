# Singapore Public Carpark Finder

## Find Your Nearest Affordable Public Parking Spot in Singapore! 🇸🇬

This application helps you quickly locate the nearest available public carpark in Singapore by simply entering a postcode. Whether you're headed to Bugis for coffee or ECP, simply enter your destination's postal code to find the nearest public parking. Say goodbye to expensive private parking and save time circling for a spot!

---

## Features

* **Postcode-based Search:** Easily find carparks by typing in your destination's postcode.
* **Nearest Available Carpark:** Identifies the closest public carpark with available lots.
* **Real-time Availability:** Uses current data to show the number of available parking lots.
* **Google Maps Integration:** Provides a direct link to the selected carpark's location on Google Maps for easy navigation.
* **Responsive Web Interface:** Built with React for a modern and interactive user experience.
* **Robust Backend:** Powered by Python FastAPI for efficient data processing and API orchestration.

---

## Technologies Used

* **Frontend:**
    * React.js (JavaScript library for building user interfaces)
    * Vite (Fast build tool for React) or Create React App
    * HTML5, CSS3
* **Backend:**
    * Python 3.x
    * FastAPI (Modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints)
    * Uvicorn (ASGI server for FastAPI)
    * `requests` (Python HTTP library for making API calls)
    * `math` (Python's built-in math module for distance calculation)
    * `fastapi.middleware.cors` (For handling Cross-Origin Resource Sharing)

---

## Data Sources

This application relies on publicly available data from the Singapore Government:

* **Data.gov.sg Carpark Availability API:** Provides real-time information on the availability of public carparks across Singapore, maintained by agencies like HDB and URA.

---
