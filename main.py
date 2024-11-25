import spotipy
import logging

from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOauthError
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logging.log",mode='a')
    ]
)

# mood selections to seed genres
MOOD_TO_GENRE = {
    'happy': ['pop', 'dance', 'happy'],
    'sad': ['acoustic', 'ambient'],
    'energetic': ['rock', 'dance', 'electronic', 'hip-hop'],
    'calm': ['classical', 'chill', 'ambient'],
}

class InvalidRequestError(Exception):
    pass

def initSpotifyClient():
    "initialize a Spotify api client"
    try:
        return spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    except SpotifyOauthError as e:
        logging.error(f"Error initializing Spotify client: {e}")
        raise

def getSpotifySongs(spotify : spotipy , seed_genres, audio_features, limit=10,):
    "Fetch song recommendations from Spotify using seed_genres and audio features"
    try:
        recommendations = spotify.recommendations(
            seed_genres = seed_genres,
            limit=limit, **audio_features
        )
    except Exception as e:
        logging.error(f"Error in getSpotifySongs: {e}")
        raise
    else:
        return [
            {
                'track_name': track['name'],
                'artist': track['artists'][0]['name'],
                'embed_url': f"https://open.spotify.com/embed/track/{track['id']}"
            }
            for track in recommendations['tracks']
        ]

def getAudioFeatures(req) -> dict:
    "return a dict contains the audio features from a json request."
    data = validate_request(req)
    data.pop('mood',None)
    audio_features = {key: value for key, value in data.items() if value is not None}
    if not audio_features:
        logging.warning("no audio features were given")
    else:
        logging.info(f"selected audio features : {audio_features}")
    return audio_features

def getSeedGenres(req) -> list:
    "return a list of seed genres based on mood selection from a json request"
    data = validate_request(req)
    mood_options = data.pop('mood',None)
    if not mood_options:
        logging.warning("no inputted mood selection were given. proceed to a default ['pop','rock'])")
    seed_genres = MOOD_TO_GENRE.get(mood_options,['pop','rock'])
    logging.info(f"selected seed genres : {seed_genres}")
    return seed_genres

def validate_request(req):
    "validate a request and return a data json"
    if not req.is_json:
        logging.error("Unsupported Media Type: Expected JSON data.")
        raise InvalidRequestError("Invalid Request: Expected JSON data.")
    return req.get_json()

# load dot environment
if not load_dotenv(dotenv_path='.env'):
    logging.error(".env variables does not exist\ncreate an enviroment variables named '.env' with 'CLIENT_ID' and 'CLIENT_SECRET' as variables")
    exit(1)

# initialize a flask app and spotify api client
app = Flask(__name__,template_folder='templates')
spotify = initSpotifyClient()

@app.route('/')
def main():
    logging.info("Accessed the main page.")
    return render_template("index.html")

@app.route('/recommend', methods=['POST'])
def recommend():
    logging.info("Received recommendation request.")
    try:
        seed_genres = getSeedGenres(request)
        audio_features = getAudioFeatures(request)
        recommended_songs = getSpotifySongs(spotify, seed_genres, audio_features)
        logging.info(f"successfully returns {len(recommended_songs)} songs")
        return jsonify({'songs': recommended_songs}), 200
    except InvalidRequestError as e:
        logging.error(f"Invalid request: {e}")
        return jsonify({'error': str(e)}), 415
    except Exception as e:
        logging.error(f"Error processing recommendation request: {e}")
        return jsonify({'error': 'An error occurred while processing the request.'}), 500   

if __name__ == "__main__":
    app.run(debug=True)
