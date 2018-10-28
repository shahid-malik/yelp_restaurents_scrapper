# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
import time
import csv
import os
import re
import pandas as pd
import sys
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

# CITY_NAME = "DE-BE:Berlin"
# NEIGHBORHOOD_LIST_FILE_NAME = "data/yelp_neighborhood_{}.csv".format(CITY_NAME)
BUSINESS_TYPE = "Restaurants"
RESULTS_PER_PAGE = 30
STARTING_LOCATION_ID = 0  # first location in file is id zero
STARTING_PAGE_TO_CRAWL = 26  # first page is id zero


class YelpCrawler:

    def __init__(self, city):
        # def __init__(self):
        self.CITY_NAME = city
        # self.CITY_NAME = "DE-BE:Berlin"
        # self.NEIGHBORHOOD_LIST_FILE_NAME = "data/yelp_neighborhood_{}.csv".format(self.CITY_NAME)
        self.NEIGHBORHOOD_LIST_FILE_NAME = "data/cities.csv"

        chrome_options = Options()
        chrome_options.add_argument('--dns-prefetch-disable')
        chrome_options.add_argument('--disable-browser-side-navigation')
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument('disable-infobars')
        driver = Chrome(chrome_options=chrome_options)

        driver.set_page_load_timeout(10000)

        # self.browser = webdriver.Chrome()
        self.browser = driver

        self.locations_list = []
        self.location_id = 0  # row of location in file to start crawling (starting from 0)
        self.current_page = 11
        self.end_of_results = False

    def iterate_crawl(self, location_id, current_page):
        self.location_id = location_id
        print(self.location_id)
        self.current_page = current_page
        for location in self.locations_list[self.location_id:]:
            self.end_of_results = False

            while not self.end_of_results:
                print("crawling {}, page={}".format(self.locations_list[self.location_id], self.current_page))
                self.crawl_page()
                self.current_page += 1

            # reset page and go to next location
            self.current_page = 0
            self.location_id += 1
        self.browser.quit()

    def read_locations(self):
        with open(self.NEIGHBORHOOD_LIST_FILE_NAME, 'r') as f:
            content = f.readlines()
            self.locations_list = [self.url_encode(x.strip()) for x in content]
            print(self.locations_list)

    def url_encode(self, loc_str):
        str_list = loc_str.split(" ")
        if len(str_list) == 1:
            return loc_str
        else:
            encoded_str = ""
            for x in range(len(str_list)):
                if x is len(str_list) - 1:
                    encoded_str += str_list[x]
                else:
                    encoded_str += str_list[x] + "_"
            return encoded_str

    def build_url(self):
        url = "https://www.yelp.com/search?"
        if BUSINESS_TYPE is not "":
            url += "find_desc={}".format(BUSINESS_TYPE)
        url += "&start={}".format(self.current_page * RESULTS_PER_PAGE)
        url += "&find_loc={}".format(self.CITY_NAME)
        return url

    def crawl_page(self):
        self.browser.get(self.build_url())
        yelp_biz = []
        yelp_biz_urls = []
        # collect all urls to business page
        yelp_titles = self.browser.find_elements_by_css_selector(".indexed-biz-name")
        for title in yelp_titles:
            yelp_biz_urls.append(title.find_element_by_css_selector("a[href*='/biz/']").get_attribute("href"))
        print("{} business links found on page".format(len(yelp_biz_urls)))
        if len(yelp_biz_urls) == 0:
            self.end_of_results = True

        for yelp_biz_url in yelp_biz_urls:
            biz_obj = {}
            self.browser.get(yelp_biz_url)
            try:
                biz_obj["name"] = self.browser.find_element_by_css_selector(".biz-page-title").text
            except:
                biz_obj["name"] = ""
            try:
                biz_obj["phone"] = self.browser.find_element_by_css_selector(".biz-phone").text
            except:
                biz_obj["phone"] = ""
            try:
                biz_obj["address"] = self.browser.find_element_by_css_selector(".map-box-address").text.replace("\n",
                                                                                                                ", ").strip()
            except:
                biz_obj["address"] = ""
            try:
                biz_obj["categories"] = " ".join([x.text for x in self.browser.find_element_by_css_selector(
                    ".category-str-list").find_elements_by_tag_name("a")])
            except:
                biz_obj["categories"] = ""
            try:
                biz_obj["review_count"] = self.browser.find_element_by_css_selector(".review-count").text[
                                          :-8]  # remove " reviews"
            except:
                biz_obj["review_count"] = ""
            try:
                biz_obj["rating"] = self.browser.find_element_by_css_selector(".rating-very-large").get_attribute(
                    "title")[:3]  # get only first 3 chars = rating
            except:
                biz_obj["rating"] = ""
            biz_obj["yelp_url"] = yelp_biz_url
            biz_obj["neighborhood"] = self.locations_list[self.location_id]
            try:
                biz_obj["biz_url"] = self.browser.find_element_by_css_selector(
                    ".biz-website").find_element_by_css_selector("a[href*='/']").text
            except:
                biz_obj["biz_url"] = ""
            yelp_biz.append(biz_obj)

        df = pd.DataFrame(yelp_biz,
                          columns=["neighborhood", "name", "phone", "address", "categories", "review_count", "rating",
                                   "biz_url", "yelp_url"])
        try:
            df.to_csv("data/temp/{}.csv".format(self.CITY_NAME), mode='a',header=False, index=False)
        except Exception as e:
            print("Exception", e)


if __name__ == '__main__':
    with open('data/cities.csv', 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            print(row[0])
            file_name = "data/yelp_neighborhood_"+row[0]+".csv"
            try:
                if os.path.exists(file_name):
                    pass
                else:
                    with open(file_name, 'w') as f:
                        pass
            except:
                print("Exception")
            yc = YelpCrawler(row[0])
            yc.read_locations()
            yc.iterate_crawl(STARTING_LOCATION_ID, STARTING_PAGE_TO_CRAWL)

    # yc = YelpCrawler()
    # yc.read_locations()
    # yc.iterate_crawl(STARTING_LOCATION_ID, STARTING_PAGE_TO_CRAWL)
