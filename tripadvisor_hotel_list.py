#!/usr/bin/python3
import requests
import platform
import sys
from bs4 import BeautifulSoup
from time import sleep
import csv

if(len(sys.argv) != 2):
    print('Wrong arguments. Usage : python trip_advisor_scrapper.py CITY_ID')
else:
    pause = 1
    city_id = sys.argv[1]
    base_url = 'http://www.tripadvisor.com'
    hotel_query = '/Hotels-g'
    
    ofile  = open(city_id+'_list.csv', "w", newline='', encoding='utf-8')
    writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    
    row = ['hotel_name', 'hotel_id', 'n_reviews']
    writer.writerow(row)

    i = 0
    citypage_step = 0
    hotelids_first = []
    while True:
        print('# page', citypage_step+1)
        citypage_url = '%s%s%s-oa%s' % (base_url, hotel_query, city_id, str(citypage_step))
        citypage_response = requests.get(citypage_url)
        citypage_html = citypage_response.text
        citypage_soup = BeautifulSoup(citypage_html, 'html.parser')
        hotelids_rs = citypage_soup.find_all('div', class_='listing')

        hotelids = []
        for hotel in hotelids_rs:
            hotelids.append(hotel['id'])

        if(hotelids):
            # remove hotel ads
            hotelids_rs.pop(0)

            if(citypage_step == 0):
                hotelids_first = hotelids
            else:
                # if this list (hotelids) is same with the first list
                if(hotelids_first == hotelids):
                    break

            citypage_step += 30

            for hotel in hotelids_rs:
                hotel_id = hotel['id'][6:]
                hotel_name = hotel.find('a', class_='property_title').text
                hotel_reviews = hotel.find('span', class_='more')
                if hotel_reviews is None:
                    n_reviews = '0'
                else:    
                    n_reviews = hotel.find('span', class_='more').text[:-8].replace(',', '')

                i = i+1
                row = [hotel_name.encode('ascii', 'ignore').decode('ascii'), hotel_id, n_reviews]
                print(i, row)
                writer.writerow(row)

    print(i)
    ofile.close()
