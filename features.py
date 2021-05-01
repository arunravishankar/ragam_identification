import pandas as pd
import librosa
import requests
import urllib.request
import os
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")
    

cookie = 'G_ENABLED_IDPS=google; _ga=GA1.2.1416645183.1618886299; G_AUTHUSER_H=0; sangeethamshare_login=arunravishankar%40gmail.com; _gid=GA1.2.589416232.1619580559; PHPSESSID=0tdns5cv55be6rghl519hed2bv; _gat=1; sessiontime=1619932903'

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
    file_size = os.path.getsize(filename)/1048576
    #print("File Size is :", file_size, "MB")
    return(file_size)

def delete_file_(filename):
    """
    Deletes the file from the disk
    args: filename
    """
    os.remove(filename)
    return

def download_get_features(df, filename, savefile):
    """
    Downloads a file from the Sangeethapriya database,
    gets the features (chromagram and spectral centroid)
    """
    chromagrams = []
    spectral_centroids = []
    i=0
    size = 0
    for url in df['Download URLs']:
        if i%10==0:
            print(i, "Current Time =", datetime.now().strftime("%H:%M:%S"))
        
        now = datetime.now()
        try:
            size += download_file_(url, filename)
            chromagram, spectral_centroid = get_features_from_mp3_(filename)
            chromagrams.append(chromagram)
            spectral_centroids.append(spectral_centroid)
            delete_file_(filename)
        except:
            chromagrams.append('None')
            spectral_centroids.append('None')
        i+=1
        
        #print(datetime.now() - now)
    df['Chromagram'] = chromagrams
    df['Spectral Centroids'] = spectral_centroids
    df.to_csv(savefile)
    return(size)

begin_time = datetime.now()
df = pd.read_csv('sample_50_rand_df.csv')

size = download_get_features(df[:2], 'get_features_1.mp3', 'features_1.csv')
print("Total time to process the files is :", datetime.now() - begin_time)
print("Total data processed is :", size, "MB")
# Have to handle errors in downloads