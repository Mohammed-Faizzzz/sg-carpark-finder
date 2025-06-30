import React, { useState } from 'react';
import './App.css';

function App() {
    const [postcode, setPostcode] = useState('');
    const [carparkResults, setCarparkResults] = useState([]); 
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [searchPerformed, setSearchPerformed] = useState(false); // To show "No results" only after a search

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setCarparkResults([]); 
        setSearchPerformed(true); // A search has been initiated

        try {
            const backendUrl = `http://127.0.0.1:5000/find-carpark?postcode=${postcode}&limit=10`; // Use the default limit or adjust

            const response = await fetch(backendUrl);
            const data = await response.json(); 

            if (response.ok) {
                setCarparkResults(data); 
                if (data.length === 0) {
                    setError("No suitable carparks found for this postcode. Please try a different one.");
                }
            } else {
                setError(data.detail || 'An unknown error occurred. Please check your input.'); 
            }
        } catch (err) {
            console.error("Fetch error:", err);
            setError('Could not connect to the server or an unexpected error occurred. Please ensure the backend is running.');
        } finally {
            setLoading(false);
        }
    };

    const getAvailabilityBadge = (status) => {
        let badgeClass = '';
        let badgeText = status;
        if (status === 'Real-time Available') {
            badgeClass = 'status-available';
            badgeText = 'Available';
        } else if (status === 'Real-time Full') {
            badgeClass = 'status-full';
            badgeText = 'Full';
        } else if (status === 'Static Data - Check on Site' || status === 'Initial Static') {
            badgeClass = 'status-static';
            badgeText = 'Availability Unknown'; // Or "Static Data"
        }
        return <span className={`status-badge ${badgeClass}`}>{badgeText}</span>;
    };

    return (
        <div className="container">
            <h1>Nearest Carpark Finder (SG)</h1>
            <form onSubmit={handleSubmit}>
                <label htmlFor="postcode">Enter Singapore Postcode:</label>
                <input
                    type="text"
                    id="postcode"
                    placeholder="e.g., 039803"
                    value={postcode}
                    onChange={(e) => setPostcode(e.target.value)}
                    required
                    maxLength="6"
                />
                <button type="submit" disabled={loading}>
                    {loading ? 'Searching...' : 'Find Carpark'}
                </button>
            </form>

            {error && <div className="error">{error}</div>}

            {loading && <p className="info-message">Loading carparks...</p>}

            {searchPerformed && !loading && carparkResults.length === 0 && !error && (
                <p className="info-message">No suitable carparks found for "{postcode}".</p>
            )}

            {carparkResults.length > 0 && (
                <div id="results">
                    <h2>Found Carpark Results</h2>
                    {carparkResults.map((carpark) => (
                        <div key={carpark.carpark_number} className="carpark-item">
                            <div className="carpark-item-header">
                                <h3 className="carpark-item-title">{carpark.name || carpark.carpark_number}</h3> 
                                {getAvailabilityBadge(carpark.availability_status)}
                            </div>
                            
                            <div className="carpark-item-details">
                                <p><strong>Code:</strong> {carpark.carpark_number}</p>
                                <p><strong>Address:</strong> {carpark.address}</p>
                                <p><strong>Type:</strong> {carpark.type}</p>
                                
                                {carpark.availability_status === 'Real-time Available' || carpark.availability_status === 'Real-time Full' ? (
                                    <p><strong>Lots:</strong> {carpark.available_lots} / {carpark.total_lots}</p>
                                ) : (
                                    <p><strong>Total Lots (Static):</strong> {carpark.total_lots || carpark.total_lots_static}</p>
                                )}
                                
                                <p><strong>Distance:</strong> {(carpark.distance / 1000).toFixed(2)} km</p>
                            </div>

                            <div className="carpark-item-actions">
                                <a 
                                    href={`https://developers.google.com/maps/documentation/javascript/kml9{carpark.lat},${carpark.lng}`} 
                                    target="_blank" 
                                    rel="noopener noreferrer" 
                                >
                                    View on Google Maps
                                </a>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default App;