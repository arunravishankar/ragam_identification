
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import csv

def sangeethapriya_meta_data_scraper():
    """
    This function scrapes out the list of unique values of the
    meta-data of all the audio files that exist in the database of Sangeethapriya.org.
    The meta-data includes Concert ID, Track, Kriti, Ragam,
    Composer and Main Artist.
    args:
    returns: composers, ragams, kritis, artists, uploaders 
    """  
    
    page = requests.get("https://www.sangeethapriya.org/display_tracks.php")
    soup = BeautifulSoup(page.text, 'html.parser')

    dropdown_items = soup.select('option[value]')
    values = [item.get('value') for item in dropdown_items]
    text_values = [item.text for item in dropdown_items]
    box_indices = [i for i, x in enumerate(values) if x == ""]

    composers = values[box_indices[0]+1:box_indices[1]]
    ragams = values[box_indices[1]+1:box_indices[2]]
    kritis = values[box_indices[2]+1:box_indices[3]]
    artists = values[box_indices[3]+1:box_indices[4]]
    uploaders = text_values[box_indices[4]+1:]

    return(composers, ragams, kritis, artists, uploaders)


def sangeethapriya_df(composers, ragams, kritis, artists, uploaders, savefile = 'df_sangeethapriya'):
    """
    This function goes through the pages of Sangeethapriya's database
    and scrapes out the specific meta-data for each of the tracks in their
    database
    args: composers, ragams, kritis, artists, uploaders
    These are the lists of unique values that are returned by the function
    sangeethapriya_meta_data_scraper
    savefile : name of file to save
    args:composers, ragams, kritis, artists, uploaders
    returns: None (saves a file as filename)
    """
    url = "https://www.sangeethapriya.org/fetch_tracks.php?ragam"
    ragams_tables_html = []
    for i in range(len(ragams)):
        ragams_tables_html.append(requests.post(url,{"FIELD_TYPE": ragams[i]}).text)
    
    output_rows = []
    for i in range(len(ragams)):
        soup = BeautifulSoup(ragams_tables_html[i])
        table = soup.find("table")
        for table_row in table.findAll('tr'):
            columns = table_row.findAll('td')
            output_row = []
            for column in columns:
                output_row.append(column.text)
            output_rows.append(output_row)
            
    with open('{}.csv'.format(savefile), 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(output_rows)
        
    return

def main():
    composers, ragams, kritis, artists, uploaders = sangeethapriya_meta_data_scraper()
    sangeethapriya_df(composers, ragams, kritis, artists, uploaders, 'df_sangeethapriya')
    return

if __name__ == 'main':
    main()