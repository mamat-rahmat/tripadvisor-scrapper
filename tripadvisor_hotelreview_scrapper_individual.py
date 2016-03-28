#!/usr/bin/python3
import requests
import platform
import sys
from bs4 import BeautifulSoup
from time import sleep
import csv
import timeit

def ignore_ascii(s):
    return s.encode('ascii', 'ignore').decode('ascii')

if(len(sys.argv) < 4):
    print('Wrong arguments. Usage : "python trip_advisor_scrapper.py [en|id] CITY_ID DATA1 DATA2 ...". While DATA is in format gLOCATION_ID-dHOTEL_ID')
else:
    start_time = timeit.default_timer()

    pause = 1
    lang = sys.argv[1]
    city_id = sys.argv[2]
    base_url = ''
    filename =  city_id + '_' + lang + '.csv'
    
    ofile  = open(filename, 'a', newline='', encoding='utf-8')
    writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    header = ['city_id', 'hotel_name', 'hotel_star', 'review_reviewername', 'review_reviewerloc', 'review_quote', 'review_text']
    # writer.writerow(header)

    if(lang == 'en'):
        base_url = 'http://www.tripadvisor.com'
    elif(lang == 'id'):
        base_url = 'http://www.tripadvisor.co.id'
    else:
        lang = 'en'
        base_url = 'http://www.tripadvisor.com'

    hotel_query = '/Hotel_review-'
    counter = 0
    for i in range(3, len(sys.argv)):
        hotel_id = sys.argv[i]
        hotel_url = base_url + hotel_query + hotel_id
        
        hotelpage_step = 0
        reviewids_first = []
        hotel_star = ''
        hotel_name = ''
        while True:
            hotelpage_url = '%s-Reviews-or%s' % (hotel_url, str(hotelpage_step))
            sleep(pause)
            hotelpage_response = requests.get(hotelpage_url)
            hotelpage_html = hotelpage_response.text
            hotelpage_soup = BeautifulSoup(hotelpage_html, 'html.parser')
            reviewids_rs = hotelpage_soup.find_all('div', class_='reviewSelector')

            reviewids = []
            for reviewid in reviewids_rs:
                reviewids.append(reviewid['id'])
            
            if(hotelpage_step == 0):
                reviewids_first = reviewids
                hotel_name = hotelpage_soup.find('h1').text
                print(hotel_name)
                hotel_star = hotelpage_soup.find(title='Hotel class')
                if hotel_star is None:
                    hotel_star = '0'
                else:
                    hotel_star = hotel_star['alt'][:1]
            else:
                if(reviewids_first == reviewids):
                    break
            
            print('# page', hotelpage_step) #debug

            hotelpage_step += 10

            for review in reviewids_rs:
                review_q = review.find('div', class_='quote')
                if review_q:
                    review_url = base_url + review_q.a['href'][:-17]
                    sleep(pause)
                    try:
                       review_response = requests.get(review_url)
                    except requests.exceptions.RequestException as e:
                       print(e)
                    review_html = review_response.text
                    review_soup = BeautifulSoup(review_html, 'html.parser')
                    
                    review_info = review_soup.find('div', id='REVIEWS')
                    if review_info is None:
                       review_quote=''
                       review_text=''
                       review_reviewername=''
                    else:
                       review_quote = review_info.find('div', class_='quote').text[1:-1]
                       review_text = review_info.find('div', class_='entry').p.text[1:-1]
                       review_reviewername = review_info.find('div', class_='username')
                    #print(review_reviewername)
                    if not hasattr(review_reviewername, 'span') or review_reviewername.span is None:
                        review_reviewername = ''
                    else:
                        review_reviewername = review_reviewername.span.text
                    review_reviewerloc = review_info.find('div', class_='location')
                    if not hasattr(review_reviewerloc, 'text') or review_reviewerloc.text is None:
                        review_reviewerloc = ''
                    else:
                        review_reviewerloc = review_reviewerloc.text[1:-1]
                    

                    row = [city_id, ignore_ascii(hotel_name), hotel_star, ignore_ascii(review_reviewername), ignore_ascii(review_reviewerloc), ignore_ascii(review_quote), ignore_ascii(review_text)]
                    print(counter, row)
                    writer.writerow(row)
                    counter += 1
    ofile.close()
    end_time = timeit.default_timer() 
    elapsed = end_time - start_time
    print('finished get', counter, 'data in', elapsed, 'seconds')
