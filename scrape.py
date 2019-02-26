import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from lxml import html
import requests
from selenium import webdriver


def scrape():
    link = 'http://www.nikonusa.com/en/nikon-products/camera-lenses/all-lenses/index.page'

    driver = webdriver.Firefox()

    driver.get(link)
    #driver.window_handles

    # Get urls for each lens
    button1 = driver.find_elements_by_xpath('//*/td[3]/h3')

    urls = [None for _ in range(len(button1))]
    names = [None for _ in range(len(button1))]

    for i,button in enumerate(button1):
        driver.execute_script("arguments[0].scrollIntoView();", button)

        names[i] = button.text

        button.click()

        try:
            path_ = "//*[@id=\"table-view-product-quick-view-target-{}\"]/div/div[2]/div[2]/div[2]/a".format(i)

            button2 = driver.find_element_by_xpath(path_)
            urls[i] = button2.get_attribute('href')
        except:
            pass

    driver.close()

    # Error checking
    # print("len set: {}".format(len(set(urls))))

    # Filter out empty URLs
    urls = [url for url in urls if url is not None]
    # print("len set after removing empty: {}".format(len(set(urls))))

    # Create empty dataframe to hold lens data
    r = requests.get(urls[0])
    soup = BeautifulSoup(r.text, "lxml")

    columns_ = [s.text for s in soup.findAll('h4', {'class':'spec-title col-sm-6'})]
    columns_ += [ 'Url', 'Price' ]

    lenses = pd.DataFrame(columns = columns_)

    driver = webdriver.Firefox()

    for url in urls:
        # Find and click "specs" link and scrape data
        driver.get(url)
        specs_link = driver.find_element_by_xpath('//*[@id="1427413602983"]/div/div[2]/nav/div/ul/li[2]/div/a')

        # Scrape Price
        price_path = '//*[@id="1422462142038"]/div/div[1]/div/div/div[2]/section[2]/div/div/span/span[3]'
        price = driver.find_element_by_xpath( price_path ).text

        # Click on "Specs" button to view data
        driver.execute_script("arguments[0].scrollIntoView();", specs_link)
        specs_link.click()

        specs = driver.current_url

        r = requests.get(specs)
        soup = BeautifulSoup(r.text, "lxml")

        # Get rows containing data
        rows = soup.findAll('li', {'class' : 'spec-content row'})

        # Loop over rows and extract contents of "Tech Specs" page
        cols, vals = [], []

        for row in rows:
            col = row.find('h4', {'class':'spec-title col-sm-6'}).string
            cols.append(col)

            # Extract values from row and extract into string (separated by commas)
            values_ = [r for r in row.findAll('span', {'class':'value'}) if r.string is not None]

            val = ','.join([v.string for v in values_])
            vals.append(val)

        vals.append(url)
        vals.append(price)

        # Create temporary dataframe and append to final dataframe
        cols += ['Url','Price']
        df = pd.DataFrame([vals], columns = cols)
        lenses = pd.concat([lenses,df], ignore_index = True)

    driver.close()

    return lenses
