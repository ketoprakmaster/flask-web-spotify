# Spotify Song Recommendation App

This project is a Flask web application that provides song recommendations based on user-selected moods and audio preferences. It uses the Spotify API to fetch recommendations tailored to the user's input.

## Features

- Select a mood and customize audio features using sliders and options.
- Receive curated song recommendations.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.7+
- Spotify Developer Account (to obtain `CLIENT_ID` and `CLIENT_SECRET`)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/spotify-recommendation-app.git
cd spotify-recommendation-app
```

### 2. Install Dependencies

```
pip install -r requirements.txt
```
### 3. Configure Environment Variables
Create a .env file in the project root and add your Spotify credentials:

```
SPOTIPY_CLIENT_ID = <your_spotify_client_id>
SPOTIPY_CLIENT_SECRET = <your_spotify_client_secret>
```
### 4. Run the App
start the flask server
```
python main.py
```