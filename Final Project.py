#!/usr/bin/env python
# coding: utf-8

# In[3]:


get_ipython().system('pip install spotipy')


# In[4]:


get_ipython().system('pip install ticketpy')


# In[6]:


import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import ipywidgets as widgets
from ipywidgets import interact_manual
import pandas as pd
import requests


client_id = ''
client_secret = ''

client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def top_songs(artist_name):
    result = sp.search(artist_name, limit=1, type='artist')
    artist = result['artists']['items'][0]
    top_tracks = sp.artist_top_tracks(artist['id'])
    print(f"Top tracks for {artist['name']}:")
    for track in top_tracks['tracks']:
        print(f"{track['name']} - {track['external_urls']['spotify']}")

def about(artist_name):
    result = sp.search(artist_name, limit=1, type='artist')
    artist = result['artists']['items'][0]
    print(f"About {artist['name']}:")
    print(f"Genres: {', '.join(artist['genres'])}")
    print(f"Followers: {artist['followers']['total']}")
    print(f"Popularity: {artist['popularity']}")

def albums(artist_name):
    result = sp.search(artist_name, limit=1, type='artist')
    artist = result['artists']['items'][0]
    albums = sp.artist_albums(artist['id'], album_type='album')
    print(f"Albums for {artist['name']}:")
    for album in albums['items']:
        print(f"{album['name']} - {album['external_urls']['spotify']}")

def top_50():
    playlist_link = 'spotify:playlist:37i9dQZEVXbLRQDuF5jeBp' 
    results = sp.playlist_items(playlist_link)
    print("Top 50 USA playlist:")
    for track in results['items']:
        song_name = track['track']['name']
        artist_name = track['track']['artists'][0]['name']
        song_url = track['track']['external_urls']['spotify']
        print(f"{song_name} - {artist_name}: {song_url}")
        
def find_shows(artist_name):
    result = sp.search(artist_name, limit=1, type='artist')
    artist = result['artists']['items'][0]
    artist_id = artist['id']
    
    url = f"https://app.ticketmaster.com/discovery/v2/events.json?apikey=T3NabBkdxPtjuJcCn28oR5Ecb6ywMtkr&size=5&sort=date,asc&marketId=200&attractionId={artist_id}"
    
    response = requests.get(url)
    data = response.json()
    
    if 'errors' in data:
        print(f"Could not find any upcoming shows for {artist_name}.")
    elif data['page']['totalElements'] == 0:
        print(f"No upcoming shows found for {artist_name}.")
    else:
        events = data['_embedded']['events']
        print(f"Upcoming shows for {artist_name}:")
        for event in events:
            name = event['name']
            date = event['dates']['start']['localDate']
            time = event['dates']['start']['localTime']
            venue = event['_embedded']['venues'][0]['name']
            print(f"{name} at {venue} on {date} at {time}")
           
category_list = ['About', 'Top songs', 'Albums', 'Top 50 USA', 'Find shows']
artist_name_widget = widgets.Text(value='',placeholder='Enter artist name',description='Artist:',disabled=False)

@interact_manual(category=category_list, artist_name=artist_name_widget)
def get_artist_data(category, artist_name=''):
    pd.options.display.max_colwidth = 1000
    if category == 'Top 50 USA':
        top_50()
    else:
        if artist_name:
            if category == 'Top songs':
                result = sp.search(artist_name, limit=1, type='artist')
                artist = result['artists']['items'][0]
                top_tracks = sp.artist_top_tracks(artist['id'])
                top_songs = []
                for track in top_tracks['tracks']:
                    top_songs.append({'song_name': track['name'], 'song_url': track['external_urls']['spotify']})
                df = pd.DataFrame(top_songs)
                print(f"Top songs for {artist['name']}:")
                display(df)
            elif category == 'About':
                result = sp.search(artist_name, limit=1, type='artist')
                artist = result['artists']['items'][0]
                df = pd.DataFrame({'artist_name': [artist['name']], 'genres': [', '.join(artist['genres'])], 
                                   'followers': [artist['followers']['total']], 'popularity': [artist['popularity']]})
                print(f"About {artist['name']}:")
                display(df)
            elif category == 'Albums':
                result = sp.search(artist_name, limit=1, type='artist')
                artist = result['artists']['items'][0]
                albums = sp.artist_albums(artist['id'], album_type='album')
                album_list = []
                for album in albums['items']:
                    album_list.append({'album_name': album['name'], 'album_url': album['external_urls']['spotify']})
                df = pd.DataFrame(album_list)
                print(f"Albums for {artist['name']}:")
                display(df)
            elif category == 'Find shows':
                if artist_name:
                    try:
                        tm_url = 'https://app.ticketmaster.com/discovery/v2/events.json'
                        result = sp.search(artist_name, limit=1, type='artist')
                        artist = result['artists']['items'][0]
                        params = {'keyword': artist['name'], 'apikey': ''}
                        response = requests.get(tm_url, params=params)
                        events = response.json()['_embedded']['events']
                        event_list = []
                        for event in events:
                            event_list.append({'event_name': event['name'], 'venue_name': event['_embedded']['venues'][0]['name'],
                                                   'event_date': event['dates']['start']['localDate'], 
                                                   'event_time': event['dates']['start']['localTime'], 
                                                   'event_url': event['url']})
                        df = pd.DataFrame(event_list)
                        print(f"Upcoming shows for {artist['name']}:")
                        display(df)
                    except KeyError:
                        print(f"Could not find information for artist '{artist_name}'.")
                else:
                    print('Please enter an artist name.')

