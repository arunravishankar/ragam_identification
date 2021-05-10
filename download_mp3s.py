import pandas as pd
import numpy as np
import librosa
import requests
import urllib.request
import os
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")
import sys
import csv
    

cookie = 'G_ENABLED_IDPS=google; _ga=GA1.2.1416645183.1618886299; G_AUTHUSER_H=0; sangeethamshare_login=arunravishankar%40gmail.com; _gid=GA1.2.1341742613.1620334341; PHPSESSID=vpotsmibsk45tes2poqa9np19r; _gat=1; sessiontime=1620521720'

def get_features_from_mp3_(file, hop_length=1000, n_chroma=50):
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
    max_index = [np.argmax([chromagram[i][j] for i in range(0,n_chroma-1)]) for j in range(chromagram.shape[1])]
    
    return(max_index, spectral_centroid)

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



def download_files(df, workdir):
    """
    Downloads a file from the Sangeethapriya database,
    gets the features (chromagram and spectral centroid)
    """
    size = 0
    
    for index, row in df.iterrows():
        filename = os.path.join(workdir, 'song_' + str(index) + '.mp3')

        url = row['Download URLs']        

        if index%10==0:
            print(index, "Current Time =", datetime.now().strftime("%H:%M:%S"))
        
        now = datetime.now()
        try:
            size += download_file_(url, filename)
        except:
            continue
            
    return(size)

def main():
    cwd = os.getcwd()
    songs_dir = os.path.join(cwd, 'songs')
    begin_time = datetime.now()
    df = pd.read_csv('sample_50_rand_df.csv')
    size = download_files(df[0:500], songs_dir)
    print("Total time to process the files is :", datetime.now() - begin_time)
    print("Total data processed is :", size, "MB")
    # Have to handle errors in downloads
    return
if __name__ =='__main__':
    main()

