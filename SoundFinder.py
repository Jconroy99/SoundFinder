from dis import Instruction
from types import TracebackType
import pandas as pd 
import sqlite3
from pathlib import Path
import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials 
from dotenv import load_dotenv
import os

load_dotenv()
#Environment variables: create .env file and store your id and secrets under these variable names
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

#Connection to spotify API via your own credentials
auth_manager = SpotifyClientCredentials(client_id = CLIENT_ID, client_secret = CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

#Creating and connecting to database and creating cursor object
Path('Spotify.db').touch()
conn = sqlite3.connect('Spotify.db')
c = conn.cursor()

#Creating dataframe from csv file and then uploading it to sql database as a table
charts_df = pd.read_csv('charts.csv')
charts_df.to_sql('spotify_table',conn, if_exists='replace')

#SQL queries to modify table based on region (will customize in the future to have region as input or something)
sql_query_delete = 'DELETE FROM spotify_table WHERE region!="United States"'
c.execute(sql_query_delete)
conn.commit()

#SQL query for every URL and storing it in list urls_slices and close connection
sql_select = 'Select url FROM spotify_table'

#This returns list of tuples e.g., [('url1',) (url2,)]
song_rows = c.execute(sql_select).fetchall()

#List comprehension to flatten rows into list of urls i.e., [url1, url2,...]
urls_list = [row[0] for row in song_rows]

#List comprehension to return a
#list of batches of 100 urls (or slices) that is passed to audio_features()
urls_list_len = len(urls_list)
urls_slices = [urls_list[i:i+100] for i in range(0,urls_list_len,100)]


#Iterate through each batch of 100 song urls and get audio features
urls_len = len(urls_slices)

#List of dictionaries of audio features 
track_features = [track_feature for urls_slice in urls_slices for track_feature in sp.audio_features(urls_slice)]

#Define global variables for inputted song's features for comparison (will eventually take as input from user)
song_link = 'https://open.spotify.com/track/02shCNmb6IvgB5jLqKjtkK?si=a35c6a01bc91447d'
song_input = sp.audio_features(song_link)

acousticness = song_input[0]['acousticness']
danceability = song_input[0]['danceability']
energy = song_input[0]['energy']
mode = song_input[0]['mode']
valence = song_input[0]['valence']
instrumetalness = song_input[0]['instrumentalness']
liveness = song_input[0]['liveness']
loudness = song_input[0]['loudness']
speechiness = song_input[0]['speechiness']
tempo = song_input[0]['tempo']

#Comparing acousticness loop:
acous_list = []
for track in track_features:
    if track['acousticness'] >= (acousticness - 0.1) and track['acousticness'] <= (acousticness + 0.1):
        acous_list.append(track)
print(len(acous_list))

#Comparing danceability:
dance_list = []
for track in acous_list:
    if track['danceability'] >= (danceability - 0.1) and track['danceability'] <= (danceability + 0.1):
        dance_list.append(track)
print(len(dance_list))

#Comparing energy:
energy_list = []
for track in dance_list:
    if track['energy'] >= (energy - 0.1) and track['energy'] <= (energy + 0.1):
        energy_list.append(track)
print(len(energy_list))

# #Comparing valence:
# valence_list = []
# for track in energy_list:
#     if track['valence'] >= (valence - 0.1) and track['valence'] <= (valence + 0.1):
#         valence_list.append(track)
# print(len(valence_list))

#Comparing instrumentalness:
instrumetalness_list = []
for track in energy_list:
    if track['instrumentalness'] >= (instrumetalness - 0.3) and track['instrumentalness'] <= (instrumetalness + 0.3):
        instrumetalness_list.append(track)
print(len(instrumetalness_list))

#Comparing speechiness:
speechiness_list = []
for track in instrumetalness_list:
    if track['speechiness'] >= (speechiness - 0.1) and track['speechiness'] <= (speechiness + 0.1):
        speechiness_list.append(track)
print(len(speechiness_list))

#Comparing tempo:
tempo_list = []
for track in speechiness_list:
    if track['tempo'] >= (tempo - 10) and track['tempo'] <= (tempo + 10):
        tempo_list.append(track)
print(len(tempo_list))
print(tempo_list)


