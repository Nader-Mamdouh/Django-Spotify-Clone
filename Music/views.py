from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
import requests
import json
import os
from urllib.parse import quote
from dotenv import load_dotenv
import base64
from requests import post, get
from bs4 import BeautifulSoup as bs
import re
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


def get_token():
    auth_string = str(client_id) + ":" + str(client_secret)
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


def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    return json_result[0]


def get_songs_by_artist(token, artist_id, country="US", limit=9):
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


def top_artists():
    json_path = os.path.join(os.path.dirname(__file__), 'top-artist.json')
    artist_tuples = []
    with open(json_path) as f:
        data = json.load(f)
    token = get_token()
    for artist in data['top_artists']:
        artist_name = artist['name']
        artist_result = search_for_artist(token, artist_name)
        artist_id = artist_result["id"]
        artist_tuples.append((artist['name'], artist['image_url'], artist_id))
    return artist_tuples


def top_songs():
    token = get_token()
    artists_info = top_artists()
    artistnames = []
    track_details = []
    for name in artists_info:
        artistnames.append(name)
    for name in artistnames:
        artist_result = search_for_artist(token, name)
        artist_id = artist_result["id"]
        songs = get_songs_by_artist(token, artist_id)

        for track in songs:
            track_id = track['id']
            track_name = track['name']
            artist_name = track['artists'][0]['name'] if track['artists'] else None
            cover_url = track['album']['images'][0]['url'] if track['album']['images'] else None
            track_details.append({
                'id': track_id,
                'name': track_name,
                'artist': artist_name,
                'cover_url': cover_url
            })
    return track_details


@login_required(login_url='login')
def index(request):
    artists_info = top_artists()
    top_track_list = top_songs()
    first_six_tracks = top_track_list[:6]
    second_six_tracks = top_track_list[6:12]
    third_six_tracks = top_track_list[12:18]

    browse = {
        'artists_info': artists_info,
        'first_six_tracks': first_six_tracks,
        'second_six_tracks': second_six_tracks,
        'third_six_tracks': third_six_tracks,
    }
    return render(request, 'index.html', browse)


def search(request):
    if request.method == "POST":
        search_query = request.POST['search_query']
        token = get_token()
        url = "https://spotify-scraper.p.rapidapi.com/v1/search"

        querystring = {"term": search_query, "type": "track"}

        headers = {
            "x-rapidapi-key": "45600af87fmshab57eeb80b3cea1p1afb91jsnc5babd5089a6",
            "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        track_list = []

        if response.status_code == 200:
            data = response.json()

            search_results_count = data["tracks"]["totalCount"]
            tracks = data["tracks"]["items"]

            for index, track in enumerate(tracks):
                if index == 30:
                    break
                track_name = track["name"]
                artist_name = track["artists"][0]["name"]
                artist_result = search_for_artist(token, artist_name)
                artist_id = artist_result["id"]
                duration = track["durationText"]
                trackid = track["id"]

                if get_image(token, trackid):
                    track_image = get_image(token, trackid)
                else:
                    track_image = "https://imgv3.fotor.com/images/blog-richtext-image/music-of-the-spheres-album-cover.jpg"

                track_list.append({
                    'track_name': track_name,
                    'artist_name': artist_name,
                    'artist_id': artist_id,
                    'duration': duration,
                    'trackid': trackid,
                    'track_image': track_image,
                })
        context = {
            'search_results_count': search_results_count,
            'track_list': track_list[:30],
        }

        return render(request, 'search.html', context)
    else:
        return render(request, 'search.html')


def ms_to_mm_ss(duration_ms):
    minutes = duration_ms // 60000  # 1 minute = 60000 milliseconds
    # Remainder of milliseconds converted to seconds
    seconds = (duration_ms % 60000) // 1000
    return f"{minutes}:{seconds:02d}"


def profile(request, pk):
    artist_id = pk
    url = "https://spotify-scraper.p.rapidapi.com/v1/artist/overview"

    querystring = {"artistId": artist_id}

    headers = {
        "x-rapidapi-key": "45600af87fmshab57eeb80b3cea1p1afb91jsnc5babd5089a6",
        "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = response.json()

        name = data["name"]
        monthly_listeners = data["stats"]["monthlyListeners"]
        header_url = data["visuals"]["header"][0]["url"]

        top_tracks = []
        token = get_token()
        songs = get_songs_by_artist(token, artist_id)
        for track in songs:
            track_id = str(track["id"])
            track_name = str(track["name"])
            track_image = track['album']['images'][0]['url'] if track['album'][
                'images'] else "https://imgv3.fotor.com/images/blog-richtext-image/music-of-the-spheres-album-cover.jpg"
            duration_ms = track.get("duration_ms", 0)
            duration_mm_ss = ms_to_mm_ss(duration_ms)
            track_info = {
                "id": track_id,
                "name": track_name,
                "durationText": duration_mm_ss,
                "playCount": track.get("popularity", 0),
                "track_image": track_image
            }
            top_tracks.append(track_info)
        artist_data = {
            "name": name,
            "monthlyListeners": monthly_listeners,
            "headerUrl": header_url,
            "topTracks": top_tracks,
        }

    else:
        artist_data = {}

    return render(request, 'profile.html', artist_data)


def get_audio_details(query):
    url = "https://spotify-scraper.p.rapidapi.com/v1/track/download"

    querystring = {"track": query}

    headers = {
        "x-rapidapi-key": "45600af87fmshab57eeb80b3cea1p1afb91jsnc5babd5089a6",
        "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    audio_details = []
    if response.status_code == 200:
        response_data = response.json()

        if 'youtubeVideo' in response_data and 'audio' in response_data['youtubeVideo']:
            audio_list = response_data['youtubeVideo']['audio']
            if audio_list:
                first_audio_url = audio_list[0]['url']
                duration_text = audio_list[0]['durationText']

                audio_details.append(first_audio_url)
                audio_details.append(duration_text)
            else:
                print("No audio data availble")
        else:
            print("No 'youtubeVideo' or 'audio' key found")
    else:
        print("Failed to fetch data")

    return audio_details


def get_image(token, trackid, country="US"):
    # Use f-string to insert trackid
    url = f'https://api.spotify.com/v1/tracks/{trackid}'
    headers = get_auth_header(token)
    params = {"market": country}
    result = get(url, headers=headers, params=params)
    result.encoding = 'utf-8'
    data = result.json()
    return data['album']['images'][0]['url']


def music(request, pk):
    track_id = pk
    token = get_token()
    url = "https://spotify-scraper.p.rapidapi.com/v1/track/metadata"

    querystring = {"trackId": track_id}

    headers = {
        "x-rapidapi-key": "45600af87fmshab57eeb80b3cea1p1afb91jsnc5babd5089a6",
        "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = response.json()
        track_name = data.get("name")
        artists_list = data.get("artists", [])
        first_artist_name = artists_list[0].get(
            "name") if artists_list else "No artist found"
        artist_result = search_for_artist(token, first_artist_name)
        artist_id = artist_result["id"]
        audio_details_query = track_name + first_artist_name
        audio_details = get_audio_details(audio_details_query)
        audio_url = audio_details[0]
        duration_text = audio_details[1]
        track_image = get_image(token, track_id)
        context = {
            'track_name': track_name,
            'artist_name': first_artist_name,
            'artist_id': artist_id,
            'audio_url': audio_url,
            'duration_text': duration_text,
            'track_image': track_image,
        }
    return render(request, 'music.html', context)


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('login')
    else:
        return render(request, 'login.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email already Exist")
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username already Exist")
                return redirect('signup')
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password1)
                user.save()
                user_login = auth.authenticate(
                    username=username, password=password1)
                auth.login(request, user_login)
                return redirect('/')
        else:
            messages.info(request, "Password Miss Match")
            return redirect('signup')
    else:
        return render(request, 'signup.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')
