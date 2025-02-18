import time
import random
import requests
from lxml import html
import logging
import regex

from utils import isAccount
import settings

_googleURL = 'https://www.google.com/'
time_cutter = 10

# ===================================================================================

class GoogleScraper():
    def __init__(self, gui, pause):
        self.gui = gui
        self.pause = pause
        self.starting_search = True
        s = gui.nbFollowerSearch[gui.nbFollowers.get()]
        self.min_value = s[2]
        self.max_value = s[3]
        self.prefix = s[4]

    def search2(self, googleURL, nextLinksNeeded):
        r = requests.get(googleURL, headers=settings.headers)
        logging.info('[{}] {}'.format(r.status_code, googleURL))
        logging.debug(r.text)

        # be nice with google...
        if self.starting_search:
            self.starting_search = False
        else:
            sleeping_time = random.randint(self.pause, self.pause * 1.2)
            logging.info('sleeping {} seconds...'.format(sleeping_time))
            deci_sec = sleeping_time * time_cutter
            for i in range(deci_sec):
                self.gui.lbl_info['text'] = "Waiting... %4.1fs" % (float(deci_sec - i) / 10)
                self.gui.update()
                time.sleep(1.0 / time_cutter)
                if self.gui.cancel_requested:
                    break
            self.gui.lbl_info['text'] = ""
            self.gui.update()

        if r.status_code >= 500:
            raise Exception(r.status_code, r.text)

        links = []
        tree = html.fromstring(r.content)
        res = tree.xpath('//div[@class="g"]/div[@class="s"]')
        for e in res:
            html_text_account_info = ''
            html_text_account_link = ''
            for child in e.getchildren():
                logging.debug("tag: {}    items:{}".format(child.tag, child.items()))
                if child.tag == 'span':
                    html_text_account_info = child.text_content()
                elif child.tag == 'div':
                    child2 = child.getchildren()[0]
                    logging.debug(child2.tag)
                    html_text_account_link = child2.text
            logging.info("account link: {}".format(html_text_account_link))
            logging.info("account info: {}".format(html_text_account_info))
            if not isAccount(html_text_account_link):
                logging.info("Not an account link: ignored")
            elif html_text_account_info and html_text_account_link:
                html_text_account_info = html_text_account_info.replace('\n', '')
                m = regex.match(f".*?([\.0-9]*)[{self.prefix.lower()}{self.prefix.upper()}] [fF]ollowers.*", html_text_account_info)
                if m:
                    html_text_nb_followers = m.groups()[0]
                    logging.info("[Regex] Nb followers: {}{}".format(html_text_nb_followers, self.prefix))
                    if self.min_value <= float(html_text_nb_followers) <= self.max_value:
                        elt = (html_text_account_link, html_text_account_info, html_text_nb_followers)
                        links.append(elt)
                        logging.info("User selected")
                    else:
                        logging.info("not in interval: ignored")
                else:
                    logging.info("User ignored")

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
        for serp_block in serp_links:
            self.micro_sleep()
            yield serp_block

        for next_link in next_links:
            logging.debug('next link item : %s' % next_link)
            serp_links2, next_links2 = self.search2(_googleURL + next_link, False)
            for serp_block in serp_links2:
                self.micro_sleep()
                yield serp_block

    def micro_sleep(self):
        r = float(random.randint(2, 4)) / 10
        time.sleep(r)
