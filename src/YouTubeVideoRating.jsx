import React, { useState } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';

const App = () => {
    const [url, setUrl] = useState('');
    const [result, setResult] = useState('');

    const handleSubmit = async (event) => {
        event.preventDefault();
        console.log("Sending URL:", url);
        try {
            const response = await axios.post('/get_score', { url });
            console.log("Received response:", response.data);
            if (response.data.error) {
                setResult(<div className="alert alert-danger">{response.data.error}</div>);
            } else {
                setResult(<div className="alert alert-success">The rating for this video is: {response.data.score}</div>);
            }
        } catch (error) {
            console.error("AJAX error:", error);
            setResult(<div className="alert alert-danger">An error occurred while processing the request.</div>);
        }
    };

    return (
        <div className="container">
            <h1 className="mt-5">YouTube Video Sentiment Rating</h1>
            <form id="videoForm" className="mt-4" onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="url">Enter YouTube Video URL:</label>
                    <input
                        type="text"
                        className="form-control"
                        id="url"
                        name="url"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        required
                    />
                </div>
                <button type="submit" className="btn btn-primary">Get Rating</button>
            </form>
            <div className="mt-4" id="result">{result}</div>
        </div>
    );
};

export default App;
