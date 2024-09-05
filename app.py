from flask import Flask, request, render_template, jsonify
from googleapiclient.discovery import build
from transformers import pipeline
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for your Flask app

# Set up the YouTube API
api_key = 'AIzaSyCykf7XGBQWmr2ilcQlaxT-TXeDqSWPshI'  # Replace with your actual YouTube API key
youtube = build('youtube', 'v3', developerKey=api_key)

# Set up the sentiment analysis pipeline
sentiment_analyzer = pipeline('sentiment-analysis', truncation=True)

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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_score', methods=['POST'])
def get_score():
    try:
        url = request.json.get('url')
        video_id = extract_video_id(url)
        comments = get_comments(video_id)

        if not comments:
            return jsonify({'error': 'No comments found for the given video.'})

        positive = 0
        negative = 0

        # Ensure comments are processed in manageable chunks
        chunk_size = 500  # Adjust as needed
        for i in range(0, len(comments), chunk_size):
            chunk = comments[i:i + chunk_size]
            sentiment_results = sentiment_analyzer(chunk)

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
        # Log the exception for debugging purposes
        import traceback
        error_message = str(e) + '\n' + traceback.format_exc()
        return jsonify({'error': error_message})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
