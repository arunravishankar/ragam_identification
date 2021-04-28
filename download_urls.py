import pandas as pd
import requests
from bs4 import BeautifulSoup
import re


def df_uploaders_album_ids(df):
    """
    Parses the Uploaders and Album IDs from the Concert IDs
    args: df - dataframe containing Concert ID, Track, Kriti, Ragam,
    Composer and Artist
    return : df - dataframe appended by uploaders and album_ids  
    """
    df['Uploader'] = df['Concert ID'].str.split('-').str[0].str.strip()
    df['Album ID'] = df['Concert ID'].str.split('-').str[1].str.strip().str.lower()
    return df



def get_album_href(response):
    """
    Gets the album urls for a file 
    by using the Concert ID and 
    Track number from the dataframe and scraping 
    Sangeethapriya.
    args: response - response from a futures request
    return: album_href
    """
    soup = BeautifulSoup(response.text)
    div_main = soup.find('div', {'id':'main'})
    if div_main is None:                # Error handling
        album_href = 'None'
    else: 
        if div_main.a is None:          #Error handling
            album_href = 'None'
        elif div_main.a['href'] is None:   # If no url exists
            album_href = 'None'
        else:
            album_href = div_main.a['href']
    return album_href




def futures_albums(uploaders, album_ids, lim=2000):
    """
    Creates futures sessions to obtain the album hrefs
    for every file that exists in the Sangeethapriya
    database.
    args : uploaders
         : album_ids
    kwargs : lim - number of parallel futures sessions
    return : list of all album urls
    """
    
    session = FuturesSession()
    marker = 0
    lim = lim
    all_album_urls = []
    url = "https://www.sangeethapriya.org/locate_album.php"
    
    while(marker) < (min(len(uploaders)+lim-1, len(uploaders))):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Current Time =", current_time) # Takes about 90 minutes to run
        futures = []
        for i in range(marker, min(marker+lim, len(uploaders))):
            payload = "UPLOADER={}&CONCERT_ID={}".format(uploaders[i], album_ids[i])
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            futures.append(session.post(url, headers = headers, data = payload))
        album_urls = [get_album_href_t(f.result()) for f in futures]
        all_album_urls.extend(album_urls)
        marker=marker+lim
    return all_album_urls    

def get_no_null_df(df):
    """
    Gets the dataframe after removing null entries for album hrefs
    args: df - dataframe containing Album hrefs
    return: df - dataframe without null entries in Album hrefs
    """
    return df[df['Album hrefs'] != 'None']

 def high_ragam_counts_sample(df, x, samp):
    """
    Picking ragams that have at least x number of 
    files in the database. This will remove rare ragams from
    the dataframe. The dataframe that is input is the one
    that contains no null entries in the Album hrefs.
    args: df - dataframe containing the Ragam
    
    """
    ragam_counts = df['Ragam'].value_counts()
    high_ragam_counts = ragam_counts[ragam_counts > x]
    over_x_df = df[df.groupby('Ragam')['Ragam'].transform('size')>x]
    sample_df = pd.DataFrame()    
    for i in range(len(high_ragam_counts)):
        high_ragams_df = over_x_df[over_x_df['Ragam']==list(high_ragam_counts.keys())[i]]
        sample_df.append(high_ragams_df.sample(samp, random_state = 0))
    ##Still have to probably save the df

    return sample_df

## Have to write function to get the urls from the album hrefs


def freq_ragams_df(df):
