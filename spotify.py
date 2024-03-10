import os
import requests
import configparser

config = configparser.ConfigParser()
config.read('spotify_credentials.properties')

client_id = config['spotify_credentials']['client.id']
client_secret = config['spotify_credentials']['client.secret']
token_url = 'https://accounts.spotify.com/api/token'
search_url = 'https://api.spotify.com/v1/search'
image_folder = 'artist-images'

def get_artist_details(artist_name):
    artist_details = {
        'name': '',
        'genre': [],
        'image_url': ''
    }

    auth_response = requests.post(token_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })

    access_token = auth_response.json()['access_token']

    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }

    params = {
        'q': artist_name,
        'type': 'artist',
        'market': 'RO',
        'limit': 1
    }

    response = requests.get(search_url, headers=headers, params=params)
    data = response.json()

    if 'artists' in data and 'items' in data['artists'] and len(data['artists']['items']) > 0:
        artist = data['artists']['items'][0]
        genres = artist.get('genres', [])
        image_url = artist.get('images')[0]['url'] if 'images' in artist and len(artist['images']) > 0 else None

        if image_url:
            image_filename = os.path.join(image_folder, f"{artist_name}.jpg")
            with open(image_filename, 'wb') as f:
                f.write(requests.get(image_url).content)

            artist_details = {
                'name': artist_name,
                'genre': genres,
                'image_url': image_filename
            }

    return artist_details

