import base64
import requests
import spotipy
import os
import logging

from flask import Flask, jsonify, render_template, request
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logging.log",mode='w')
    ]
)

env_bool = load_dotenv(dotenv_path='env')

token = str()
expiration = datetime.now()
app = Flask(__name__,template_folder='templates')



def get_token_expiration_time(expires_in_seconds: int) -> datetime:
    """
    Convert the expires_in value to the real datetime when the token will expire.
    
    :param expires_in_seconds: Number of seconds until the token expires (e.g., 3600 for 1 hour)
    :return: A datetime object representing the exact expiration time
    """
    # Get the current time
    current_time = datetime.now()
    
    # Add the expires_in seconds to the current time
    expiration_time = current_time + timedelta(seconds=expires_in_seconds)
    
    return expiration_time



# Replace print statements in manage_token
def manage_token() -> str:
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    global token
    global expiration

    if expiration >= datetime.now() and token:
        logging.info(f"Using existing token. Token expiration: {expiration}")
        return token

    token, expiration = create_token(client_id, client_secret)
    logging.info(f"Creating new token at: {datetime.now()}. Token expiration date: {expiration}")
    
    return token



def create_auth_header(client_id: str, client_secret: str) -> str:
    """Create a Base64 encoded authorization header."""
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
    return f"Basic {auth_base64}"



def create_token(client_id: str, client_secret: str) -> tuple[str, datetime]:
    """Return a token (str) and expiration date (datetime) from Spotify API."""
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": create_auth_header(client_id, client_secret),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    logging.debug("Requesting new token from Spotify API.")

    # Make the POST request to get the token
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the response to get the token
        json_result = response.json()
        access_token = json_result.get("access_token")
        expires_in = get_token_expiration_time(json_result.get("expires_in") - 100)
        
        logging.info("Token successfully created.")
        return access_token, expires_in

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get token: {e}")
        raise Exception(f"Failed to get token: {e}")



def get_spotify_songs(mood_option,audio_features: dict = {}, limit=10) -> list:
    if not audio_features:
        raise ValueError("no attributes were given")

    logging.debug(f"Fetching songs with audio features: {audio_features}")
    sp = spotipy.Spotify(auth=manage_token())
    
    mood_to_genre = {
        'happy': ['pop','dance','happy'],
        'sad': ['acoustic', 'ambient'],
        'energetic': ['rock', 'dance','electronic','hip-hop'],
        'calm': ['classical', 'chill','ambient'],
    }

    seed_genres = mood_to_genre.get(mood_option,['pop','rock'])
    logging.info(f"seed genres selected : {seed_genres}")
    
    try:
        recommendations = sp.recommendations(
            seed_genres=seed_genres,
            limit=limit, **audio_features
    )
    except Exception as e:
        logging.error(f"Error fetching recommendations: {e}")
        raise

    tracks = [
        {
            'track_name': track['name'],
            'artist': track['artists'][0]['name'],
            'embed_url': f"https://open.spotify.com/embed/track/{track['id']}"
        }
        for track in recommendations['tracks']
    ]

    logging.info(f"Retrieved {len(tracks)} tracks.")
    return tracks    



@app.route('/')
def main():
    logging.info("Accessed the main page.")
    return render_template("index.html")



@app.route('/recommend', methods=['POST'])
def recommend():
    logging.info("Received recommendation request.")
    
    try:
        data = request.get_json()

        # Extract mood from the request data
        mood_select = data.pop('mood', None)
        
        # If mood is required, raise an error if it's missing
        if not mood_select:
            raise ValueError("Mood selection is missing from the request.")

        # Filter out only the audio features that have valid values
        audio_features = {key: value for key, value in data.items() if value is not None}

        logging.debug(f"Received mood options: {mood_select}")
        logging.debug(f"Received audio features: {audio_features}")

        # Fetch song recommendations from Spotify using mood and audio features
        recommended_songs = get_spotify_songs(mood_option=mood_select, audio_features=audio_features)

        logging.info(f"Successfully retrieved {len(recommended_songs)} song recommendations.")
        return jsonify({'songs': recommended_songs})

    except ValueError as ve:
        logging.error(f"ValueError: {ve}")
        return jsonify({'error': str(ve)}), 400  # Bad request
    except Exception as e:
        logging.error(f"Error processing recommendation request: {e}")
        return jsonify({'error': 'An error occurred while processing the request.'}), 500



if __name__ == "__main__":
    if not env_bool:
        raise BaseException(".env variables does not exist\ncreate an enviroment variables named '.env' with 'CLIENT_ID' and 'CLIENT_SECRET' as variables")
    else:
        app.run(debug=True)