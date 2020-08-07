#Imports
import requests as req
from bs4 import BeautifulSoup as bs
from splinter import Browser
import re
import pandas as pd
from time import sleep

#URLs
url_nasa = "https://mars.nasa.gov/news"
url_jpl = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
url_mars = "https://space-facts.com/mars/"
url_astro = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"


def init_browser():
    executable_path = {'executable_path': 'chromedriver'}
    return Browser('chrome', **executable_path,headless=True)

def getNasaData(browser):
    browser.visit(url_nasa)
    sleep(1)
    soup = bs(browser.html,'html.parser')
    article_titles = soup.find_all(class_='content_title')
    article_teasers = soup.find_all(class_='article_teaser_body')

    return [article_titles[1].text,article_teasers[0].text]

def getJPLImage(browser):
    browser.visit(url_jpl)
    sleep(1)
    soup = bs(browser.html,'html.parser')

    carousel_image = soup.find(class_='carousel_item')
    image_location = re.search("background-image: url\(\'(.*)\'\)",carousel_image['style'])

    featured_image_url = "https://www.jpl.nasa.gov" + image_location.group(1)
    
    return featured_image_url

def getMarsFacts():
    table = pd.read_html(url_mars)
    tablehtml = (table[0].to_html(index=False,header=False))
    tablehtml = tablehtml.replace("\n", "")
    return (str(tablehtml))


# Note - uses the sample file rather than full sized image as full sized image is in tif format and would need to be converted before displaying in web browser.
def getMarsHemispheres(browser):
    browser.visit(url_astro)
    sleep(1)
    soup = bs(browser.html,'html.parser')

    items = soup.find_all(class_='item')

    hemisphere_image_urls = []

    for item in items:
        link = item.a['href']

        browser.visit("https://astrogeology.usgs.gov/" + link)
        soup = bs(browser.html,"html.parser")
        
        title = soup.find('h2').text[:-9]

        file_div = soup.find_all('div',class_="downloads")
        file_url = file_div[0].find_all('li')[0].a['href']  # change 0 to a '1' to get full sized image
        
        hemisphere_image_urls.append({"title":title, "image_url": file_url})
        
    return hemisphere_image_urls

def scrape():
    browser = init_browser()
    resultset = {}

    nasaData = getNasaData(browser)
    resultset["title"] = nasaData[0]
    resultset["desc"] = nasaData[1]

    resultset["featured_image_url"] = getJPLImage(browser)

    resultset["tablehtml"] = getMarsFacts()
    
    resultset["hemi_imgs"] = getMarsHemispheres(browser)

    #print(resultset)

    return resultset
    
    

if __name__ == '__main__':
    scrape()