from flask import Flask, request, send_from_directory, jsonify
from googleapiclient.discovery import build
from transformers import pipeline
from flask_cors import CORS
import re
import os


app = Flask(__name__, static_folder='./build', static_url_path='/')

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
# Set up the YouTube API
api_key = 'AIzaSyCykf7XGBQWmr2ilcQlaxT-TXeDqSWPshI'  # Replace with your YouTube API key
youtube = build('youtube', 'v3', developerKey=api_key)

# Set up the sentiment analysis pipeline
sentiment_analyzer = pipeline('sentiment-analysis')

def get_comments(video_id):
    comments = []
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        maxResults=100
    )
    response = request.execute()

    while request is not None:
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)

        if 'nextPageToken' in response:
            request = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                pageToken=response['nextPageToken'],
                maxResults=100
            )
            response = request.execute()
        else:
            break

    return comments

def extract_video_id(url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube URL")

def calculate_video_score(positive, negative):
    total = positive + negative
    if total == 0:
        return 0
    p_pos = positive / total
    scaled_score = round(p_pos * 5, 2)
    return scaled_score

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')

@app.route('/logo192.png')
def logo():
    return send_from_directory(app.static_folder, 'logo192.png')

@app.route('/get_score', methods=['POST'])
def get_score():
    try:
        data = request.get_json()
        url = data['url']
        video_id = extract_video_id(url)
        comments = get_comments(video_id)

        positive = 0
        negative = 0

        sentiment_results = sentiment_analyzer(comments)

        for result in sentiment_results:
            if result['label'] == 'POSITIVE':
                positive += 1
            elif result['label'] == 'NEGATIVE':
                negative += 1

        score = calculate_video_score(positive, negative)
        return jsonify({'score': score})
    except ValueError as e:
        return jsonify({'error': str(e)})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'An error occurred while processing the request.'})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)




""""

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
          const response = await axios.post('http://localhost:8080/get_score', { url });
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

"""