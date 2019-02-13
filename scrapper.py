# coding: utf8
 
import time
import requests
from unidecode import unidecode
from lxml import html
from tkinter import *
import tldextract
import regex
import random
import logging

from utils import get_tld_cache_file
import settings

mail_re = [r'.*[" >]([a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z0-9]+)[" <].*',
        r'.*[" >]([a-zA-Z0-9]+ @ [a-zA-Z0-9]+\.[a-zA-Z0-9]+)[" <].*',
        r'.*[" >]([a-zA-Z0-9]+ @ [a-zA-Z0-9]+ \. [a-zA-Z0-9]+)[" <].*',
        r'.*[" >]([a-zA-Z0-9]+ [aA][tT] [a-zA-Z0-9]+\.[a-zA-Z0-9]+)[" <].*',
        r'.*[" >]([a-zA-Z0-9]+ [aA][tT] [a-zA-Z0-9]+ \. [a-zA-Z0-9]+)[" <].*',
        r'.*[" >]([a-zA-Z0-9]+ [aA][tT] [a-zA-Z0-9]+ [dD][oO][tT] [a-zA-Z0-9]+)[" <].*'
        ]

mail_kw = ['contact', 'mail', 'team', 'info']

class Scrapper():

    def __init__(self, url, gui, nb_pages):
        self.scrapped = []
        self.mails = []
        self.tree = None
        self.gui = gui
        self.url_site = url
        self.nb_pages = nb_pages
        self.te = tldextract.TLDExtract(cache_file=get_tld_cache_file())
        self.dn = 'http://' + self.te(self.url_site).registered_domain
        self.r = None

    def isSameDomain(self, d):
        d1 = self.te(self.url_site)
        d2 = self.te(d)
        return d1.domain == d2.domain and d1.suffix == d2.suffix

    def absoluteDomain(self, url):
        if len(url) == 0:
            url = self.dn + '/'
        elif len(url) < 4 or url[:4] != 'http':
            if url[0] == '/':
                url = self.dn + url
            else:
                url = self.dn + '/' + url
        return url

    def search_handle(self):
        # FIXME
        handle = self.url_site
        self.mails.append(handle)

    def scrap(self, url=''):
        self.gui.update()
        if self.gui.cancel_requested:
            logging.debug('cancel requested')
            return
        if '#' in url:
            return
        if len(self.scrapped) >= self.nb_pages:
            return

        self.scrapped.append(self.absoluteDomain(url))
        if url == '':
            url = self.url_site
        else:
            url = self.absoluteDomain(url)

        if self.isSameDomain(url):
            logging.info('scrapping : %s' % url)
            try:
                self.search_handle()
                time.sleep(random.randint(1,2))
            except requests.TooManyRedirects:
                logging.warning('Too many redirects')
            except Exception as e:
                try:
                    logging.warning(e.message)
                except:
                    logging.warning('unknown exception')

    def scrap_next(self):
        links = self.tree.xpath('//a')
        for link in links:
            if self.gui.cancel_requested:
                break
            if link.text is not None and any(kw in link.text for kw in mail_kw):
                self.scrap(link.text)
        if len(self.mails) == 0:
            links = self.tree.xpath('//a/@href')
            for link in links:
                if self.gui.cancel_requested:
                    break
                self.scrap(link)

