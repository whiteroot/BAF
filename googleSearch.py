import time
import random
import sys
import requests
from unidecode import unidecode
from lxml import html
import logging
import settings

_googleURL = 'https://google.com/'
time_cutter = 10

# ===================================================================================

class GoogleScraper():
    def __init__(self, gui, pause):
        self.gui = gui
        self.pause = pause
        self.starting_search = True

    def search2(self, googleURL, nextLinksNeeded):
        r = requests.get(googleURL, headers=settings.headers)
        logging.info('[{}] {}'.format(r.status_code, googleURL))

        # be nice with google...
        if self.starting_search:
            self.starting_search = False
        else:
            sleeping_time = random.randint(self.pause, self.pause * 1.2)
            logging.info('sleeping {} seconds...'.format(sleeping_time))
            lbl_copy = self.gui.lbl_info['text']
            deci_sec = sleeping_time * time_cutter
            for i in range(deci_sec):
                self.gui.lbl_info['text'] = "Waiting... %4.1fs" % (float(deci_sec - i) / 10)
                self.gui.update()
                time.sleep(1.0 / time_cutter)
                if self.gui.cancel_requested:
                    self.gui.lbl_info['text'] = ''
                    break

        if r.status_code >= 500:
            raise Exception(r.status_code, r.text)

        links = []
        tree = html.fromstring(r.content)
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

    def search(self, _searched_string, on_site):
        _searched_string += ' site:{}'.format(on_site)
        url = _googleURL + 'search?q=' + _searched_string
        logging.info('search string : %s' % _searched_string)
        serp_links, next_links = self.search2(url, True)
        logging.info('SERP links : %s' % serp_links)
        logging.info('next links : %s' % next_links)
        for link in serp_links:
            self.micro_sleep()
            yield link

        for next_link in next_links:
            logging.debug('next link item : %s' % next_link)
            serp_links2, next_links2 = self.search2(_googleURL + next_link, False)
            for link in serp_links2:
                self.micro_sleep()
                yield link

    def micro_sleep(self):
        r = float(random.randint(1, 10)) / 10
        time.sleep(r)
