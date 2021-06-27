
"""Script that scrapes informationf from https://apps.cra-arc.gc.ca/ebci/hacc/srch/pub/dsplyBscSrch?request_locale=en"""
import bs4 as bs
from selenium import webdriver
import time
import json


keyword = "cadets"

url = "https://apps.cra-arc.gc.ca/ebci/hacc/srch/pub/bscSrch?&q.srchNm=" + keyword
#For Mac - If you use windows change the chromedriver location
chrome_path = '/usr/local/bin/chromedriver'

driver = webdriver.Chrome(chrome_path)


def searchKeyword(url):
    # use the session to get the data

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-popup-blocking")

    driver.maximize_window()

    start_time = time.monotonic()

    while True:
        page = 1 #Start at first page and iterate over the next pages
        newUrl = url + "dsrdPg=" + str(page)
        try:
            driver.get(newUrl)
            soup = bs.BeautifulSoup(driver.page_source, 'tr')
            charitiesURL = returnCharitiesURL(soup)
            for url in charitiesURL:
                scrapeCharity("https://apps.cra-arc.gc.ca" + url)
            page += 1


        except:
            print("got all charities")
            break




def returnCharitiesURL(soup):
    urls = []
    tr = soup.find_all('tr', {"headers": "headername"})
    for element in tr:
        print(element.findChild().href)
        urls.append(element.findChild().href)

    return urls


def scrapeCharity(url):
    driver.get(url)
    registration_number = driver.find_element_by_class_name("col-xs-12 col-sm-6 col-md-6 col-lg-9").text.replace(" ", "")
    print("Registration Number", registration_number)
    full_view_url = "https://apps.cra-arc.gc.ca/ebci/hacc/srch/pub/dsplyT3010FrFlngPrd?selectedFilingPeriodIndex=0&selectedCharityBn=" + registration_number
    driver.get(full_view_url)

    return url


if __name__ == '__main__':
    searchKeyword(url)