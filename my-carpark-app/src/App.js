import React, { useState } from 'react';

function App() {
    const [postcode, setPostcode] = useState('');
    const [carparkResult, setCarparkResult] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setCarparkResult(null);

        try {
            // Make a request to Python backend
            const response = await fetch(`http://localhost:5000/find-carpark?postcode=${postcode}`); // Adjust URL for backend
            const data = await response.json();

            if (response.ok) {
                setCarparkResult(data);
            } else {
                setError(data.error || 'An unknown error occurred.');
            }
        } catch (err) {
            console.error("Fetch error:", err);
            setError('Could not connect to the server or an unexpected error occurred.');
        } finally {
            setLoading(false);
        }
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
                    minLength="6"
                    maxLength="6"
                />
                <button type="submit" disabled={loading}>
                    {loading ? 'Searching...' : 'Find Carpark'}
                </button>
            </form>

            {error && <div className="error">{error}</div>}

            {carparkResult && (
                <div className="carpark-item">
                    <strong>Nearest Carpark:</strong> {carparkResult.carpark_number}<br/>
                    Available Lots: {carparkResult.lots_available} / {carparkResult.total_lots}<br/>
                    Distance: {(carparkResult.distance / 1000).toFixed(2)} km<br/>
                    <a href={`https://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png6${carparkResult.lat},${carparkResult.lng}`} target="_blank" rel="noopener noreferrer">
                        View on Google Maps
                    </a>
                </div>
            )}
        </div>
    );
}

export default App;