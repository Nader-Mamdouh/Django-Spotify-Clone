from urllib.parse import quote
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import requests
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)

    if result.status_code == 200:
        token = json_result["access_token"]
        return token
    else:
        raise Exception(f"Failed to get token: {json_result}")


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def search_for_artist_or_track(token, search_query):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)

    # Search for both artist and track
    query = f"?q={search_query}&type=artist,track&limit=10"
    query_url = url + query

    result = requests.get(query_url, headers=headers)

    if result.status_code == 200:
        data = result.json()
        artists = data["artists"]["items"]
        tracks = data["tracks"]["items"]

        # If there are artist matches, return all songs by that artist
        if len(artists) > 0:
            artist_id = artists[0]['id']
            return get_songs_by_artist(token, artist_id)

        # If no artist is found, return tracks with the same name
        elif len(tracks) > 0:
            return get_songs_by_name(token, search_query)

        else:
            return None
    else:
        return None


def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = get_auth_header(token)
    params = {"market": "US"}  # Adjust market as needed

    result = requests.get(url, headers=headers, params=params)

    if result.status_code == 200:
        return result.json()["tracks"]
    else:
        return None


def get_songs_by_name(token, track_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)

    query = f"?q={track_name}&type=track&limit=10"
    query_url = url + query

    result = requests.get(query_url, headers=headers)

    if result.status_code == 200:
        return result.json()["tracks"]["items"]
    else:
        return None


def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)

    # Correct the query by using a comma between types
    query = f"?q={artist_name}&type=artist,track&limit=10"
    query_url = url + query

    result = get(query_url, headers=headers)

    if result.status_code == 200:
        json_result = json.loads(result.content)["artists"]["items"]

        # Ensure there are results before accessing the first one
        if len(json_result) > 0:
            return json_result[0]
        else:
            return None
    else:
        # Handle the case where the request fails
        return None


def get_songs_by_artist(token, artist_id, country="US", limit=5):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = get_auth_header(token)
    params = {"market": country, "limit": limit}
    result = get(url, headers=headers, params=params)
    json_result = json.loads(result.content)["tracks"]
    return json_result


def get_albums_by_artist(token, artist_id, country="US"):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    headers = get_auth_header(token)
    params = {"market": country}
    result = get(url, headers=headers, params=params)
    result.encoding = 'utf-8'
    json_result = json.loads(result.content)['items']

    return json_result


def get_spotify_category_details(access_token, category_id):
    url = f"https://api.spotify.com/v1/browse/categories/{category_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve category details: {response.status_code}")
        print(response.text)  # Use response.text for non-JSON error responses
        return None


token = get_token()
artist_name = "Amr Diab"
artist_result = search_for_artist(token, artist_name)
artist_id = artist_result["id"]
songs = get_songs_by_artist(token, artist_id)
albums = get_albums_by_artist(token, artist_id)
print(artist_result)
