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
        : x - number of tracks per ragam
        : samp - number of tracks to sample in a ragam
    return: None
    Saves : Saves a csv file with the dataframe of sampled tracks    
    """
    ragam_counts = df['Ragam'].value_counts()
    high_ragam_counts = ragam_counts[ragam_counts > x]
    over_x_df = df[df.groupby('Ragam')['Ragam'].transform('size')>x]
    sample_df = pd.DataFrame()    
    for i in range(len(high_ragam_counts)):
        high_ragams_df = over_x_df[over_x_df['Ragam']==list(high_ragam_counts.keys())[i]]
        sample_df.append(high_ragams_df.sample(samp, random_state = 0))
    
    sample_df.to_csv('over{}ragams{}sample.csv'.format(x,sample))
    return sample_df


def freq_ragams_df(df):





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
    soup = BeautifulSoup(response.text)
    filelist_text = soup.find('ul',{'id':'filelist'})

    if filelist_text is None:
        return('None')
    else:
        print(filelist_text)
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



def download_urls(df, start = 0, end = 10, cookie = cookie):
    """
    Obtain downloads urls given the dataframe including the album hrefs
    args: df - dataframe containing album hrefs
        : start - start of df
        : end - end of df - default set to 10 - must use len(df)
        : cookie - cookie required to get the post requests
    returns: all_download_urls - list of all download urls
    """
    all_download_urls = []
    for i in range(start, end):
        #Print the current time for every 50 urls obtained
        if i%50 ==0:
            now = datetime.now()
            current_time = str(now.strftime("%H:%M:%S"))
            print("{} Current Time = {}".format(i, current_time))
        payload = {}
        headers = {'Cookie': cookie}
         
        url = df['Album hrefs'][i]
        track = df['Track'][i]

        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        try:
            response = session.get(url, headers = headers, data = payload)
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

def clean_no_null(df):
    """
    Removes the entries that do not have download_urls
    args: df
    returns: df
    """
    return(df[df['Download URLs'] != 'None'])

def main():
    

if __name__ == '__main__':
    main()