import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import re
import requests
import sys
import os
import glob

CITY_NAME = "DE-BE:Berlin"
# 'ALL': crawl websites of all neighborhoods in the city
# e.g. 'Bergmannkiez': crawl websites of particular neighborhood
NEIGHBORHOOD = "ALL"


def get_menu(website_url):
    print("Getting Menu...")
    if website_url == "" or not isinstance(website_url, str):
        print("URL not valid...")
        return ""
    else:
        url_tries = ["", "/speisekarte.html", "/speisekarte/", "/menu/", "/menu.html"]
        for url_try in url_tries:
            try:
                soup = create_soup(website_url + url_try)
                menu = find_menu(soup)
                if menu:
                    menu_path = download_menu(website_url, menu)
                    return menu_path
            except KeyboardInterrupt:
                sys.exit(0)
            except:
                print("An error occurred.")
        return ""


def download_menu(website_url, pdf_url):
    if "http" not in pdf_url:
        pdf_url = "http://www." + website_url + pdf_url
    print("Menu found: {}, downloading...".format(pdf_url))
    response = requests.get(pdf_url)
    filepath = 'data/menu/{}.pdf'.format(website_url)
    with open(filepath, 'wb') as f:
        f.write(response.content)
        f.close()
    return filepath


def get_email(website_url):
    print("Getting Email...")
    if website_url == "" or not isinstance(website_url, str):
        print("URL not valid...")
        return ""
    else:
        url_tries = ["", "/kontakt/", "/kontakt.html", "/impressum/", "/impressum.html", "/infos/"]
        for url_try in url_tries:
            try:
                soup = create_soup(website_url + url_try)
                email = find_email(soup)
                if email:
                    print("Email found: {}".format(email))
                    return email
            except KeyboardInterrupt:
                sys.exit(0)
            except:
                print("An error occurred.")
        return ""


def create_soup(url):
    print("trying {}...".format(url))
    response = requests.get("http://www." + str(url))
    return BeautifulSoup(response.text, 'html.parser')


def find_email(soup):  # TODO: also remove png and sentry false positives
    email_reg_tries = [r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", r"[a-z0-9\.\-+_]+\(at\)[a-z0-9\.\-+_]+\.[a-z]+"]
    # try two variants of email (name@email.com and name(at)email.com)
    for email_reg in email_reg_tries:
        email = soup.find(text=re.compile(email_reg))
        if email:
            email = re.search(email_reg, email).group(0)
            return email
    email = [a["href"] for a in soup.select("a[href^=mailto:]")]
    if email:
        return email[0]
    return None


def find_menu(soup):
    for link in soup.find_all('a'):
        current_link = link.get('href')
        if current_link.endswith('pdf'):
            print("Menu PDF: " + current_link)
            return current_link
    return None


def write_single_neighborhood(in_csv, out_csv):
    number_lines = sum(1 for row in (open(in_csv)))
    chunksize = 10

    # start looping through data writing it to a new file for each chunk
    for i in range(0, number_lines, chunksize):
        df = pd.read_csv(in_csv,
                         header=None,
                         nrows=chunksize,  # number of rows to read at each loop
                         skiprows=i)  # skip rows that have been read

        df[9] = df[7].apply(get_email)
        df[10] = df[7].apply(get_menu)

        df.to_csv(out_csv,
                  index=False,
                  header=False,
                  mode='a',
                  chunksize=chunksize)


if __name__ == "__main__":
    if NEIGHBORHOOD == "ALL":
        out_csv_file = "data/final/{}_ALL.csv".format(CITY_NAME)
        out_csv_temp = "data/temp/{}*.csv".format(CITY_NAME)
        try:
            out_csv = open(out_csv_file, 'r')
            out_csv = open(out_csv_temp, 'r')
        except:
            out_csv = open(out_csv_file, 'w')
            out_csv = open(out_csv_temp, 'w')
        for fname in glob.glob('data/temp/{}*.csv'.format(CITY_NAME)):
            write_single_neighborhood(fname, out_csv)
    else:
        in_csv = "data/temp/{}_{}.csv".format(CITY_NAME, NEIGHBORHOOD)
        out_csv = "data/final/{}_{}.csv".format(CITY_NAME, NEIGHBORHOOD)
        write_single_neighborhood(in_csv, out_csv)
