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

#SQL query for every URL and storing it in list urls and close connection
sql_select = 'Select url FROM spotify_table'
urls = c.execute(sql_select).fetchall()
conn.close()

#Iterate through each song url and get audio features
urls_len = len(urls)
track_features = []
for i in range(100):
    #Returns list of dictionaries of a song's features/qualities
    track_features.append(sp.audio_features(urls[i]))
    print(track_features[i])

#Define global variables for inputted song's features for comparison
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

print(track_features[2][0]['acousticness'])
print(acousticness)

#Comparing acousticness loop:
acous_list = []
for i in range(100):
    if track_features[i][0]['acousticness'] >= (acousticness - 0.1) and track_features[i][0]['acousticness'] <= (acousticness + 0.1):
        acous_list.append(track_features[i])
        print('success')
    else:
        print(track_features[i])

acous_len = len(acous_list)
print(acous_len)
# dance_list = []
# for i in range(acous_len):
#     if acous_list[i]['danceability'] >= (danceability - 0.1) and acous_list[i]['danceability'] <= (danceability + 0.1):
#         dance_list.append(acous_list[i])
#     else:
#         print(acous_list[i]) 

# dance_len = len(dance_list)
# print(dance_len)

