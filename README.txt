Instructions For Crawling Yelp Businesses
=========================================
1. Search city of interest on Yelp and click on "All Filters".
2. Select any of the neighborhood and take note of the city name in the URL. Replace it in the crawl_neighborhoods.py file.
(Example for https://www.yelp.com/search?start=0&l=p:DE-BE:Berlin::Pankow, "DE-BE:Berlin" is the CITY_NAME)
3. Create a file called "yelp_neighborhood_[CITY_NAME].csv" in the data folder.
4. Click on "More Neighborhoods" and copy each of the items, line by line, into the new file.
5. Run "python crawl_neighborhoods.py" - the data for each neighborhood would be stored in the "data/temp/" folder.
6. In order to scrape the emails from individual business websites,
go to go_to_website.py file and edit FILE_IN to the city-neighborhood of choice.
7. Run "python go_to_website.py" to get the final lists in the "data/final/" folder.
8. Final list columns are in this order:
- neighborhood, name, phone, address, categories, review_count, rating, biz_url, yelp_url, email, menu

Requirements:
=============
> Python 3.4+
> Run 'pip install -r requirements.txt' first to install dependencies
> If you don't have chromedriver installed, run 'brew install chromedriver' (for Mac OS X)

Note:
====
There will definitely be some false positives in the results - email may be .png / .sentry.io, menu may be marketing EDM.
If you see "An error occured.", it is usually due to the website being down or blocking crawlers.
Each city / neighborhood's Yelp results count may be different.
Some show 10 results on a page and some show 30 results on a page (You can observe it while Selenium is running).
Please change the RESULTS_PER_PAGE value in crawl_neighborhoods.py accordingly in order to avoid duplicates.
