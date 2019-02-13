# coding: utf8
 
import time
import sys
import requests
from unidecode import unidecode
from lxml import html
import logging
import settings

_googleURL = 'https://google.fr/'

# ===================================================================================

def search2(googleURL, nextLinksNeeded):
    r = requests.get(googleURL, headers=settings.headers)
    logging.info('[{}] {}'.format(r.status_code, googleURL))
    if r.status_code >= 500:
        raise Exception(r.status_code, r.text)
    tree = html.fromstring(r.content)

    links = []
    res = tree.xpath('//div[@class="g"]/h3/a/@href')
    for link in res:
        logging.debug('google link #1 : %s' % link)
        pos = link.find('&sa=')
        if pos > 0:
            link = link[7:pos]
            if link[:4] == 'http':
                logging.debug('google link #2 : %s' % link)
                links.append(link)
        else:
            logging.error("can't parse google URL")
            return False

    if nextLinksNeeded:
        next_links = tree.xpath('//div[@id="foot"]/table[@id="nav"]/tr/td/a[@class="fl"]/@href')
    else:
        next_links = None
    return links, next_links

def search(_searched_string, on_site):
    _2points = '%' + str(hex(ord(':')))[2:].upper()
    _searched_string += ' site' + _2points + on_site
    _searched_string = _searched_string.replace(' ','+')

    url = _googleURL + 'search?q=' + _searched_string
    logging.info('search string : %s' % _searched_string)
    serp_links, next_links = search2(url, True)
    logging.info('SERP links : %s' % serp_links)
    logging.info('next links : %s' % next_links)
    for link in serp_links:
        yield link

    for next_link in next_links:
        logging.debug('next link item : %s' % next_link)
        serp_links2, next_links2 = search2(_googleURL + next_link, False)
        for link in serp_links2:
            yield link

