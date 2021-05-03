import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from requests_futures.sessions import FuturesSession
from datetime import datetime
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Update this every time you run it
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    'sec-ch-ua-mobile': '?0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://www.sangeethamshare.org/login.php?url=%2Ftvg%2FUPLOADS-5201---5400%2F5268-V_Subramaniam%2F',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cookie': 'G_ENABLED_IDPS=google; _ga=GA1.2.1416645183.1618886299; G_AUTHUSER_H=0; sangeethamshare_login=arunravishankar%40gmail.com; _gid=GA1.2.589416232.1619580559; PHPSESSID=94sl2ikuaebethc0gu6t9vm0ud; _gat=1; sessiontime=1619866771; PHPSESSID=94sl2ikuaebethc0gu6t9vm0ud; sessiontime=1619866771'
}

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



def get_album_href_(response):
    """
    Gets the album urls for a file 
    by using the Concert ID and 
    Track number from the dataframe and scraping 
    Sangeethapriya.
    args: response - response from a futures request
    return: album_href
    """
    soup = BeautifulSoup(response.text, features = "html.parser")
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
        album_urls = [get_album_href_(f.result()) for f in futures]
        all_album_urls.extend(album_urls)
        marker=marker+lim
    return all_album_urls    


def high_ragam_counts_sample(df, x, samp):
    """
    Picking ragams that have at least x number of 
    files in the database. This will remove rare ragams from
    the dataframe. The dataframe that is input is the one
    that contains no null entries in the Album hrefs.
    args: df - dataframe containing the Ragam
        : x - number of tracks per ragam
        : samp - number of tracks to sample in a ragam
    return: None
    Saves : Saves a csv file with the dataframe of sampled tracks    
    """
    ragam_counts = df['Ragam'].value_counts()
    high_ragam_counts = ragam_counts[ragam_counts > x]
    over_x_df = df[df.groupby('Ragam')['Ragam'].transform('size')>x]
    sample_df = over_x_df[over_x_df['Ragam']==list(high_ragam_counts.keys())[0]].sample(samp, random_state = 0)

    for i in range(1,len(high_ragam_counts)):
        sample_df = sample_df.append(over_x_df[over_x_df['Ragam']==list(high_ragam_counts.keys())[i]].sample(samp, random_state = 0))
        
    
    sample_df.to_csv('over{}ragams{}sample.csv'.format(x,samp))
    return sample_df


def get_url_download_(response, track_table):
    """
    Parses html page to obtain the download url for the right track
    Contains error handling to handle pages that don't contain
    download urls or where the pages don't exist
    args: response from the get request. 
        : track_table - the track number that needs to be parsed
    returns: download_url for the appropriate file
    """
    regex = '0?{}'.format(track_table)
    soup = BeautifulSoup(response.text, features = "html.parser")
    filelist_text = soup.find('ul',{'id':'filelist'})
    if filelist_text is None:
        return('None')
    else:
        if filelist_text.find_all('li', {'class':'audio'}) is None:
            return('None')
        else:
            filelist_files = filelist_text.find_all('li',{'class':'audio'})

            for item in filelist_files:
                h2_text = item.find('h2').text
                track_no = re.findall("\d+", h2_text)
                if re.search(regex, track_no[0]) is None:
                    continue
                else:
                    download_item = item.find('a',{'class':'download'})
                    start = str(download_item).find('http')
                    down_start_str = str(download_item)[start:]
                    end = down_start_str.find('\"')
                    return(str(download_item)[start:start + end])
    return('None')



def download_urls(df, start = 0, end = 10, headers = headers):
    """
    Obtain downloads urls given the dataframe including the album hrefs
    args: df - dataframe containing album hrefs
        : start - start of df
        : end - end of df - default set to 10 - must use len(df)
        : cookie - cookie required to get the post requests
    returns: all_download_urls - list of all download urls
    """
    all_download_urls = []
    urls = list(df['Album hrefs'])
    tracks = list(df['Track'])

    for i in range(start, end):
        #Print the current time for every 50 urls obtained
        if i%50 ==0:
            now = datetime.now()
            current_time = str(now.strftime("%H:%M:%S"))
            print("{} Current Time = {}".format(i, current_time))
        payload = {}
        headers = headers
        url = urls[i]
        track = tracks[i]

        
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                all_download_urls.append(get_url_download_(response, str(track)))
            else:
                all_download_urls.append('None')
        except:
            all_download_urls.append('None')

    return all_download_urls


def append_download_urls_save_df(df, download_urls, filename):
    """
    Appends a column to the df to include the download urls
    for each file
    """
    df['Download URLs'] = download_urls
    df.to_csv(filename, index=False)
    return

def clean_no_null(df, column):
    """
    Removes the entries that do not have download_urls
    args: df
    returns: df
    """
    return(df[df[column] != 'None'])



def main():
    """
    Reads the file saved from sangeethapriya_scraper.py
    Obtains album hrefs for each of the files - this takes about 2 hours to run
    Cleans the df to remove those entries that do not contain an album page
    Saves that file as df_album_hrefs.csv
    Samples 100 tracks from all the ragams that contain more than 100 files in the database
    Parses through the album pages to obtain the download urls for each file
    Cleans the df to remove those entries that do not contain a download url
    Saves the df 
    """

    #df = pd.read_csv('df_sangeethapriya.csv', names=["Concert ID","Track","Kriti","Ragam","Composer","Main Artist"])
    #df = df_uploaders_album_ids(df)
    #df['Album hrefs'] = futures_albums(df['Uploader'], df['Album ID'], lim=2000)
    
    #Takes about 2 hours to run
    
    #df = clean_no_null(df, 'Album hrefs')
    #df = df.drop(['Uploader', 'Album ID'], axis=1)
    #df.to_csv('df_album_hrefs.csv', index = False)
    
    #df = pd.read_csv('df_album_hrefs.csv')
    #album_hrefs = list(df['Album hrefs'])
    #new_album_hrefs = ["https://www." + item[7:] + '/' for item in album_hrefs]
    #df['Album hrefs'] = new_album_hrefs
    #df = high_ragam_counts_sample(df, 100, 100)
    #df['Download URLs'] = download_urls(df, start = 0, end = len(df), headers = headers)
    #Takes about 8-9 hours to run
    #df = clean_no_null(df, 'Download URLs')
    #df.to_csv('sample_download_df.csv')
    
    #df = pd.read_csv('sample_download_df.csv')
    #ragams_130 = list(df['Ragam'].unique())
    #df_50 = df[df['Ragam'] == ragams_130[0]].sample(50, random_state = 0)
    #for i in range(1, len(ragams_130)):
        #df_50 = df_50.append(df[df['Ragam']==ragams_130[i]].sample(50, random_state = 0))
    #df_50.to_csv('sample_50_df.csv')
    #df_50 = pd.read_csv('sample_50_df.csv')
    #df_50 = df_50.sample(frac=1, random_state=0)
    #df_50.to_csv('sample_50_rand_df.csv')
    
    df_50 = pd.read_csv('sample_50_df.csv')
    df_50 = df_50.sample(frac=1, random_state = 0)
    df_50.to_csv('sample_50_rand_df.csv')    
    ## Write rows to files instead of writing the whole file directly
    ## If I am running parallel downloads, I will need to write to a dictionary
    ## and then read from that.
if __name__ == '__main__':
    main()