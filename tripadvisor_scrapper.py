import requests
import platform
import sys
from bs4 import BeautifulSoup
from time import sleep
import csv

if(len(sys.argv) != 2):
    print('Wrong arguments. Usage : python trip_advisor_scrapper.py CITY_ID')
else:
    pause = 0.02
    city_id = sys.argv[1]
    base_url = 'http://www.tripadvisor.com'
    hotel_query = '/Hotels-g'
    
    ofile  = open(city_id+'.csv', "w", newline='', encoding='utf-8')
    writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    row = ['city_name', 'hotel_name', 'hotel_star', 'review_reviewername', 'review_reviewerloc', 'review_quote', 'review_text']
    writer.writerow(row)

    city_url = base_url+hotel_query+city_id
    sleep(pause)
    city_response = requests.get(city_url)
    city_html = city_response.text
    city_soup = BeautifulSoup(city_html, 'html.parser')
    city_name = city_soup.find('span', class_='geoName').text

    counter = 0;

    citypage_step=0
    hotelids_first = []
    while True:        
        
        citypage_url = '%s%s%s-oa%s' % (base_url, hotel_query, city_id, str(citypage_step))
        sleep(pause)
        citypage_response = requests.get(citypage_url)
        citypage_html = citypage_response.text
        citypage_soup = BeautifulSoup(citypage_html, 'html.parser')
        hotelids_rs = citypage_soup.find_all('div', class_='listing')

        hotelids = []
        for hotelid in hotelids_rs:
            hotelids.append(hotelid['id'])

        if(citypage_step == 0):
            hotelids_first = hotelids
        else:
            if(hotelids_first == hotelids):
                break

        citypage_step += 30

        for hotel in hotelids_rs:
            hotel_title = hotel.find('a', class_='property_title')

            hotel_url = hotel_title['href'][:31]
            while not hotel_url[-1].isdigit():
                hotel_url = hotel_url[:-1]
            hotel_name = hotel_title.text

            print(citypage_step, hotel_name) #debug

            hotelpage_step = 0
            reviewids_first = []
            while True:
                print('  ', hotelpage_step) #debug
                hotelpage_url = '%s%s-Reviews-or%s' % (base_url, hotel_url, str(hotelpage_step))
                sleep(pause)
                hotelpage_response = requests.get(hotelpage_url)
                hotelpage_html = hotelpage_response.text
                hotelpage_soup = BeautifulSoup(hotelpage_html, 'html.parser')
                reviewids_rs = hotelpage_soup.find_all('div', class_='reviewSelector')

                reviewids = []
                for reviewid in reviewids_rs:
                    reviewids.append(reviewid['id'])

                hotel_star = ''
                if(hotelpage_step == 0):
                    reviewids_first = reviewids
                    hotel_star = hotelpage_soup.find(title='Hotel class')
                    if hotel_star is None:
                        hotel_star = '0'
                    else:
                        hotel_star = hotel_star['alt'][:1]
                else:
                    if(reviewids_first == reviewids):
                        break

                hotelpage_step += 10
                i = 0
                for review in reviewids_rs:
                    review_q = review.find('div', class_='quote')
                    if review_q:
                        review_url = base_url + review_q.a['href'][:-17]
                        sleep(pause)
                        review_response = requests.get(review_url)
                        review_html = review_response.text
                        review_soup = BeautifulSoup(review_html, 'html.parser')
                        
                        review_info = review_soup.find('div', id='REVIEWS')
                        review_quote = review_info.find('div', class_='quote').text[1:-1]
                        review_text = review_info.find('div', class_='entry').p.text[1:-1]
                        review_reviewername = review_info.find('div', class_='username').span.text
                        review_reviewerloc = review_info.find('div', class_='location').text
                        

                        row = [city_name, hotel_name, hotel_star, review_reviewername, review_reviewerloc, review_quote, review_text]
                        writer.writerow(row)

                        print('  ', '  ', counter) #debug
                        counter += 1

    ofile.close()
