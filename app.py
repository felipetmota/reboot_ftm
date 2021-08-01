#IMPORT LIBRARIES
import requests 
import pandas as pd
import boto3
import re
import os

from datetime import datetime

import selenium
from selenium import webdriver

from bs4 import BeautifulSoup

from secrets import access_key, secret_access_key

#Create User-Agent for requests
headers = { 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36" }


def uk_cities_name():

    #URL with 20 top cities
    url = 'https://www.tripadvisor.co.uk/Restaurants-g186216-United_Kingdom.html'

    
    #result of the URL request
    result_cities = requests.get(url, headers=headers )

    #SET html.parser and text to result
    soup = BeautifulSoup( result_cities.text, 'html.parser' )

    #Cities Name = Find the tag DIV with class='geo_name'
    allcities = soup.find_all( 'div', class_='geo_name')

    #Take the CITIES NAME
    allcitiesname = [p.get_text() for p in allcities]

    #Replace \n and Restaurant to nothing
    allcitiesname = [s.replace('\n', '') for s in allcitiesname]
    allcitiesname = [s.replace('Restaurants', '') for s in allcitiesname]

    #Take the LINK allcities[0].find('a').get('href')
    allcitieslinks = [p.find('a').get('href') for p in allcities]

    #Take the City ID
    city_id = [i.split('-')[1] for i in allcitieslinks]

    #Take the City URL
    city_url = [i.split('-')[2] for i in allcitieslinks]

    #Create DataFrame with feauters
    data = pd.DataFrame([allcitiesname,city_id,city_url]).T

    #Alter columns name
    data.columns = ['city','city_id','city_url']

    #Code VEGAN
    data['code_vegan'] = 'zfz10697'

    #Add new colum with datetime
    data['scrap_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return data

def colect_data_cities():

    #get data from uk_cities_name function
    data = uk_cities_name()
  
    #empty data frame
    df_details = pd.DataFrame()
   
    for i in range( len ( data ) ):

        print(range(len(data)))
        print(i)
        #URL with 20 top cities
        url = 'https://www.tripadvisor.co.uk/Restaurants-'+ data.loc[i, 'city_id']+'-'+ data.loc[i, 'code_vegan']+'-'+ data.loc[i, 'city_url']+''

        #result of the URL request
        result_cities = requests.get(url, headers=headers )

        soup = BeautifulSoup(result_cities.text, 'html.parser')

        #Take the City URL
        city_url2 = url.split('-')
        city_url2 = city_url2[1]
        city_url2

        #Take the SORT BY
        sortby = soup.find( 'div', class_='_1NO-LVmX _1xde6MOz')
        sortby = sortby.text

        #Get the AMOUNT of the RESTAURANTS
        path = 'selenium\chromedriver.exe'

        #driver = webdriver.Chrome(executable_path="chromedriver\chromedriver.exe")
        driver = webdriver.Chrome(path)
        driver.get(url)
        #Find class name _1D_QUaKi
        total_rest = driver.find_element_by_class_name("_1D_QUaKi")
        #Get text without html code.
        results_restaurants = total_rest.text
        #close the browser screen
        driver.quit()
        
        #Get first 5 restaurants
        list_item = soup.find( 'div', class_='_1kXteagE')
        #Get first 5 restaurants - each item list
        each_item = soup.find_all('div', attrs={'data-test':re.compile("^[1-5]_list_item")})
        #get the name of the restaurantes
        restaurant_name = [r.find('a', class_='_15_ydu6b').get_text() for r in each_item]
        #create the restaurants name DataFrame
        restaurant_name = pd.DataFrame(restaurant_name)
        #rename the columns
        restaurant_name.columns = ['Restaurants']
        

        #Create DataFrame with feauters
        data2 = pd.DataFrame([city_url2,sortby,results_restaurants, restaurant_name]).T

        #Alter columns name
        data2.columns = ['city_id','sort_by','results_rest', 'restaurant_name']

        #Create data final
        dataOverview = pd.merge(data, data2, how='left', on='city_id')
        
        df_details = pd.concat( [df_details, dataOverview], axis=0 )
        
    return df_details

def save_csv():
    #all 
    data_final = colect_data_cities()
   
    #Save data in CSV with datetime
    data_final.to_csv('data.csv', index=False)

    client = boto3.client('s3',
                     aws_access_key_id = access_key,
                    aws_secret_access_key = secret_access_key)

    for file in os.listdir():
        if '.csv' in file:
            upload_file_bucket = 'bucketname'
            upload_file_key = file
            client.upload_file(file,upload_file_bucket,upload_file_key)

if __name__ == "__main__":

    uk_cities_name()
    colect_data_cities()
    save_csv()

