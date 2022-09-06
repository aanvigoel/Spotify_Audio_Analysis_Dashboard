import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pickle as pkl
import pandas as pd
from pymongo import MongoClient
import time


def read_mongo(db, collection, query={}, no_id=True):
    # Make a query to the specific DB and Collection
    cursor = db[collection].find(query)
    # Expand the cursor and construct the DataFrame
    df = pd.DataFrame(list(cursor))
    # Delete the _id
    if no_id:
        del df['_id']
    return df


def load_data(file='spotify_df.pkl'):
    try:
        data_df = pkl.load(open(file, "rb"))
    except OSError:
        # Create a mongo client
        client = MongoClient()
        db = client.SpotifyData
        data_df = read_mongo(db, 'track_features')
        pkl.dump(data_df, open("spotify_df.pkl", "wb"))
    return data_df


def add_features(row):
    with open("credentials.txt") as f:
        cred_ls = f.readlines()
        cid = cred_ls[0][:-1]
        secret = cred_ls[1]

    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    response = sp.track(row.id)
    # if response.status_code == 429:
    #    time.sleep(int(response.headers["Retry-After"]))
    #    response = sp.track(row.id)

    track_pop = response["popularity"]

    artists = row.artist_ids.strip('][').replace("'", "").split(', ')
    artist_pop = []
    genres = []

    artists = sp.artists(artists)["artists"]
    # if artists.status_code == 429:
    #    time.sleep(int(response.headers["Retry-After"]))
    #    artists = sp.artists(artists)["artists"]

    for i in range(len(artists)):
        artist_pop.append(artists[i]["popularity"])

        if artists[i]["genres"]:
            genres.append(artists[i]["genres"])
        else:
            genres.append("unknown")

    row["track_pop"] = track_pop
    row["artist_pop"] = artist_pop
    row["genres"] = genres

    return row
