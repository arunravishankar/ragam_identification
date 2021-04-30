import pandas as pd
import librosa
import requests
import urllib.request
import os
from datetime import datetime
    

cookie =  'G_ENABLED_IDPS=google; _ga=GA1.2.1416645183.1618886299; G_AUTHUSER_H=0; sangeethamshare_login=arunravishankar%40gmail.com; _gid=GA1.2.589416232.1619580559; PHPSESSID=gpkn86p2im4t9jqubp69r2dqp4; _gat=1; sessiontime=1619762113'


def get_features_from_mp3_(file, hop_length=500, n_chroma=50):
    """
    Get features
    """
    x, sr = librosa.load(file)
    chromagram = librosa.feature.chroma_stft(x, 
                                             sr=sr, 
                                             hop_length=hop_length, 
                                             n_chroma = n_chroma)
    spectral_centroid = librosa.feature.spectral_centroid(x, 
                                                          sr=sr, 
                                                          hop_length=hop_length)                  
    
    return(chromagram, spectral_centroid)

def download_file_(url, filename, cookie = cookie):
    """
    Downloads a file given the url
    args: url, filename, cookie
    """
    opener = urllib.request.build_opener()
    opener.addheaders = [('Cookie', cookie)]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url, filename)
    return

def delete_file_(filename):
    """
    Deletes the file from the disk
    args: filename
    """
    os.remove("getting_features.mp3")
    return

def download_get_features(df):
    """
    Downloads a file from the Sangeethapriya database,
    gets the features (chromagram and spectral centroid)
    """
    filename = 'getting_features.mp3'
    chromagrams = []
    spectral_centroids = []
    i=0
    for url in df['Download URLs']:
        
        now = datetime.now()
        download_file_(url, filename)
        chromagram, spectral_centroid = get_features_from_mp3_(filename)
        chromagrams.append(chromagram)
        spectral_centroids.append(spectral_centroid)
        delete_file_(filename)
        i+=1
        
        print(datetime.now() - now)
    df['Chromagram'] = chromagrams
    df['Spectral Centroids'] = spectral_centroids
    df.to_csv('features.csv')
    return


df = pd.read_csv('download_urls.csv')

download_get_features(df[:50])

# Have to handle errors in downloads