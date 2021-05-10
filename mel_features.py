import pandas as pd
from sklearn.model_selection import train_test_split
from datetime import datetime
import numpy as np
import os
import librosa
import warnings
warnings.filterwarnings("ignore")

from sklearn import preprocessing
def extract_feature(file_name, i):
    X, sample_rate = librosa.load(file_name, offset = 20*i, duration = 10)
    stft = np.abs(librosa.stft(X))
    mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T,axis=0)
    chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T,axis=0)
    mel = np.mean(librosa.feature.melspectrogram(X, sr=sample_rate).T,axis=0)
    contrast = np.mean(librosa.feature.spectral_contrast(S=stft,
    	sr=sample_rate).T,axis=0)
    tonnetz = np.mean(librosa.feature.tonnetz(y=librosa.effects.harmonic(X),
    	sr=sample_rate).T,axis=0)
    return mfccs,chroma,mel,contrast,tonnetz

def parse_audio_files(indices, ragams, le):
    begin_time = datetime.now()
    features, labels = np.empty((0,193)), np.empty(0) # 193 => total features
    workdir = os.path.join(os.getcwd(), 'songs')
    #le = preprocessing.LabelEncoder()
    #le.fit(ragams)
    j = 0
    begin_time = datetime.now()
    for index, ragam in zip(indices, ragams):
        if j%50==0:
            print(j, datetime.now().strftime("%H:%M:%S"))
        j+=1
        filename = os.path.join(workdir, 'song_{}.mp3'.format(index)) 
        try:
            for i in range(50):
                mfccs, chroma, mel, contrast, tonnetz = extract_feature(filename, i)
                ext_features = np.hstack([mfccs, chroma, mel, contrast, tonnetz])
                features = np.vstack([features, ext_features])
                ragam_e = le.transform([ragam])[0]
                labels = np.append(labels, ragam_e)
        except:
            continue
    print(datetime.now()-begin_time)
    return np.array(features, dtype=np.float32), np.array(labels, dtype = np.int8)


df = pd.read_csv('sample_50_rand_df.csv')
X_train_file, X_test_file, y_train_file, y_test_file = train_test_split(df.index, 
                                                    df['Ragam'], 
                                                    test_size = 0.1, 
                                                    random_state = 0,
                                                    stratify = df['Ragam'])
indices = list(X_train_file)
ragams = list(y_train_file)
#print(indices[0], ragams[0], df.loc[indices[0]]['Ragam'])

le = preprocessing.LabelEncoder()
le.fit(ragams)


features = parse_audio_files(indices[:500], ragams[:500], le)
np.savetxt('features_01.csv', features[0], delimiter = ',')
np.savetxt('labels_01.csv', features[1], delimiter = ',')