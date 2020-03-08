# -*- coding: utf-8 -*-
"""
Buidling on the wishlist scraper to get a big dataset from PS store

created by: rodrigobarrela
date: 07/03/2020
"""

# import packages
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date
import numpy as np
import re

# getting css from site
pre_URL = 'https://store.playstation.com/pt-pt/grid/STORE-MSF75508-FULLGAMES/'
post_URL = '?direction=asc&platform=ps4&sort=name'

# getting first page
URL = pre_URL + str(1) + post_URL
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')

# finding the paginator that takes us to the last page
class_paginator = 'paginator-control__end paginator-control__arrow-navigation internal-app-link ember-view'
paginator = soup.find('a', class_ = class_paginator)['href']

# retrieving last page number
last_page = paginator.replace('/pt-pt/grid/STORE-MSF75508-FULLGAMES/', '')
last_page = last_page.replace('?direction=asc&platform=ps4&sort=name', '')
last_page = int(last_page)

# initializing empty dictionary
games_dict = {'title' : [],
              'original price' : [],
              'discount price': []
             }

for i in range(last_page):
    page_number = i
    URL = pre_URL + str(i) + post_URL
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    # scraping the grid for each game
    grid = soup.find('div', class_ = 'grid-cell-container')
    grid_body = grid.find_all('div', class_ = 'grid-cell__body')

    # getting the titles and prices of each game

    # loop for each game
    for game in range(len(grid_body)):
        title = grid_body[game].find('div', class_ = 'grid-cell__title').text
        title = title.replace("\n", "")
        games_dict['title'].append(title)
        
        price = grid_body[game].find('h3', class_ = 'price-display__price')
        strk_price = grid_body[game].find('span', class_ = 'price-display__strikethrough')
        
        # games without price
        if price is None:
            games_dict['original price'].append('')
            games_dict['discount price'].append('')
            continue
        
        # games not discounted
        if strk_price is None:
            games_dict['original price'].append(price.text)
            games_dict['discount price'].append('')
            
        # games discounted    
        else:
            games_dict['original price'].append(strk_price.text)
            games_dict['discount price'].append(price.text)
    
# putting data into dataframe
df = pd.DataFrame.from_dict(games_dict)

# prices from string to float
price_cols = ['original price', 'discount price']

df = df.apply(lambda x: x.str.replace(',', '.') if x.name in price_cols else x)
df = df.apply(lambda x: x.str.replace('\n', '') if x.name in price_cols else x)
df = df.apply(lambda x: x.str.replace('€', '') if x.name in price_cols else x)
df = df.apply(lambda x: x.replace('', np.nan) if x.name in price_cols else x)
df = df.apply(lambda x: x.astype(float) if x.name in price_cols else x)

# saving as csv
today = date.today()
df['Saved'] = 'Saved on ' + str(today)
df.iloc[1:,3] = ''
df.to_csv(r'C:\Users\Rodrigo-PC\projects\PS_Store.csv', index = False)
