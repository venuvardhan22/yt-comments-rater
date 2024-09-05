import React, { useReducer } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';

const initialState = {
    url: '',
    status: '',
    result: '',
};

const reducer = (state, action) => {
    switch (action.type) {
        case 'SET_URL':
            return { ...state, url: action.payload };
        case 'SET_STATUS':
            return { ...state, status: action.payload };
        case 'SET_RESULT':
            return { ...state, result: action.payload, status: '' };
        default:
            return state;
    }
};

const App = () => {
    const [state, dispatch] = useReducer(reducer, initialState);

    const handleSubmit = async (event) => {
        event.preventDefault();
        console.log("Sending URL:", state.url);
        dispatch({ type: 'SET_STATUS', payload: 'Analyzing the video...' });
        try {
            const response = await axios.post('http://localhost:8080/get_score', { url: state.url });
            console.log("Received response:", response.data);
            if (response.data.error) {
                dispatch({ type: 'SET_RESULT', payload: <div className="alert alert-danger">{response.data.error}</div> });
            } else {
                dispatch({ type: 'SET_RESULT', payload: <div className="alert alert-success">The rating for this video is: {response.data.score}</div> });
            }
        } catch (error) {
            console.error("AJAX error:", error);
            dispatch({ type: 'SET_RESULT', payload: <div className="alert alert-danger">An error occurred while processing the request.</div> });
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
                        value={state.url}
                        onChange={(e) => dispatch({ type: 'SET_URL', payload: e.target.value })}
                        required
                    />
                </div>
                <button type="submit" className="btn btn-primary">Get Rating</button>
            </form>
            <div className="mt-4" id="result">
                {state.status && <div className="alert alert-info">{state.status}</div>}
                {state.result}
            </div>
        </div>
    );
};

export default App;
