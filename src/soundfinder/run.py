import pandas as pd 
import sqlite3
from pathlib import Path
import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials 
from dotenv import load_dotenv
import os

def main():
    load_dotenv()
    '''Environment variables: create .env file and store your id and secrets under these variable names'''
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')

    spotify_client = SpotifyAuth(CLIENT_ID, CLIENT_SECRET)
    connection, cur = db_connection('Spotify.db') #db_name??

    logic_controller(spotify_client,connection,cur)
    connection.close()

def logic_controller(spotify_client,connection,cur):
        path_determiner = input('Have you ran this program already? type y/n (changing countries enter n)\n')
        '''Define variables for inputted song's features for comparison'''
        song_link = input("What song do you want the recommendations to be based on? (provide song link)\n")
        song_input = spotify_client.audio_features(f'{song_link}')

        if path_determiner == 'y':
            song_recommendations = recommendations(song_input,cur)
            print(song_recommendations)
            return(song_recommendations)
        elif path_determiner == 'n':
            csv_to_df('charts.csv',connection) #again name?? Need quotes?
            db_url_select_by_region(spotify_client,connection,cur)
            
            song_recommendations = recommendations(song_input,cur)
            print(song_recommendations)
            return song_recommendations
        else:
            return

def SpotifyAuth(CLIENT_ID, CLIENT_SECRET):
    '''Connection to spotify API via your own credentials'''
    auth_manager = SpotifyClientCredentials(client_id = CLIENT_ID, client_secret = CLIENT_SECRET)
    spotify_client = spotipy.Spotify(auth_manager=auth_manager)
    return spotify_client

def db_connection(db_name):
    '''Creating and connecting to database and creating cursor object'''
    Path(db_name).touch()
    connection = sqlite3.connect(db_name)
    cur = connection.cursor()
    return connection, cur

def csv_to_df(csv_file,connection):
    '''Creating dataframe from csv file and then uploading it to sql database as a table'''
    charts_df = pd.read_csv(csv_file)
    charts_df.to_sql('spotify_table',connection,if_exists='replace')

def db_url_select_by_region(spotify_client,connection,cur):
    region_selection = input('What country do you want to sort by? (eg. United States,United Kingdom)\n')
    query_select = f'Select url FROM spotify_table WHERE region ="{region_selection}"'

    '''This returns list of tuples e.g., [('url1',) (url2,)]'''
    song_rows = cur.execute(query_select).fetchall()

    '''List comprehension to flatten rows into list of urls i.e., [url1, url2,...]'''
    urls_list = [row[0] for row in song_rows]

    '''List comprehension to return a list of batches of 100 urls (or slices) '''
    urls_list_len = len(urls_list)
    urls_slices = [urls_list[i:i+100] for i in range(0,urls_list_len,100)]

    '''Iterate through each batch of 100 song urls and get audio features
        List of dictionaries of audio features''' 
    track_features = [track_feature for urls_slice in urls_slices for track_feature in spotify_client.audio_features(urls_slice)]
    '''Create table of Spotify features to avoid calling again'''
    create_track_features_table(track_features,connection,cur)

def create_track_features_table(track_features,connection,cur):
    cur.execute('''CREATE TABLE IF NOT EXISTS spotify_features_table (
        uri TEXT,
        acousticness REAL,
        danceability REAL,
        energy REAL,
        valence REAL,
        instrumentalness REAL,
        speechiness REAL,
        tempo REAL)''')
    cur.executemany("""
    INSERT OR REPLACE INTO 
        spotify_features_table
        (uri, acousticness, danceability, energy, valence, instrumentalness, speechiness, tempo)
    VALUES
        (:uri, :acousticness, :danceability, :energy, :valence, :instrumentalness, :speechiness, :tempo)
    """, track_features)
    connection.commit()

def recommendations(song_input,cur):
    acous_input = song_input[0]['acousticness']
    dance_input = song_input[0]['danceability']
    energy_input = song_input[0]['energy']
    val_input = song_input[0]['valence']
    instrumental_input = song_input[0]['instrumentalness']
    speech_input = song_input[0]['speechiness']
    tempo_input = song_input[0]['tempo']

    query_vars = (acous_input,dance_input,energy_input,val_input,instrumental_input,speech_input,tempo_input)
    sql_recommendations_query = '''SELECT uri FROM spotify_features_table WHERE
    acousticness >= :acous_input-0.1 AND acousticness <= :acous_input+0.1 AND
    danceability >= :dance_input-0.1 AND danceability <= :dance_input+0.1 AND
    energy >= :energy_input-0.1 AND energy <= :energy_input+0.1 AND
    valence >= :val_input-0.1 AND valence <= :val_input+0.1 AND
    instrumentalness >= :instrumental_input-0.3 AND instrumentalness <= :instrumental_input+0.3 AND
    speechiness >= :speech_input-0.1 AND speechiness <= :speech_input+0.1 AND
    tempo >= :tempo_input-10 AND tempo <= :tempo_input+10'''
    song_recs = cur.execute(sql_recommendations_query,query_vars).fetchall()
    song_recs_collapsed = set([song_rec[0] for song_rec in song_recs])
    return song_recs_collapsed