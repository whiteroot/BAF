# coding: utf8

from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Progressbar

from scrapper import Scrapper
import googleSearch
import settings

import tldextract
import logging
import random
import time
import tempfile
from utils import get_tld_cache_file
from platform import system

class gui():

    def __init__(self, resolution, current_resolution, ign_sites):
        self.site_to_search = 'instagram.com'
        self.window = Tk()
        title_window = settings.software['name']
        title_window += ' '
        title_window += str(settings.software['version_major'])
        title_window += '.'
        title_window += str(settings.software['version_minor'])
        if settings.software['version_patch'] > 0:
            title_window += '.'
            title_window += str(settings.software['version_patch'])
        title_window += ' by '
        title_window += settings.software['editor']
        self.window.title(title_window)
        cur_width = resolution[current_resolution][0]
        cur_height = resolution[current_resolution][1]
        self.window.geometry(str(cur_width) + 'x' + str(cur_height))
        tk_width = cur_width / 10
        tk_height = cur_height / 20

        self.lbl_search = Label(self.window, text="Keywords")
        self.lbl_search.grid(column=1, row=0, padx=20, pady=5)
        self.lbl_site_to_search = Label(self.window, text="Search on site")
        self.lbl_site_to_search.grid(column=3, row=0, padx=20)

        self.txt = Entry(self.window, width=int(tk_width * 0.55))
        self.txt.grid(column=1, row=1, padx=20, pady=10)
        self.txt.focus()

        self.search_btn = Button(self.window, text="Search", command=lambda inst=self: inst.search())
        self.search_btn.grid(column=1, row=2, padx=20, pady=5)

        self.cancel_btn = Button(self.window, text="Cancel", command=lambda inst=self: inst.cancel())
        self.cancel_btn.grid(column=2, row=2, padx=20, pady=5)

        self.export_btn = Button(self.window, text="Export", command=lambda inst=self: inst.export())
        self.export_btn.grid(column=3, row=2, padx=20, pady=5)

        self.list_res = Listbox(self.window, width=int(tk_width * 0.9), height=int(tk_height * 0.85))
        self.list_res.grid(column=1, row=3, padx=20, pady=3, columnspan=3)

        self.pbar = Progressbar(self.window, orient=HORIZONTAL, length=int(cur_width * 0.8), mode='determinate')
        self.pbar.grid(column=1, row=4, padx=20, pady=20, columnspan=3)

        self.cancel_requested = False
        self.ignored_sites = ign_sites
        self.all_mails = []


    def export(self):
        if len(self.all_mails) == 0:
            messagebox.showinfo("Info", "No mail to export!")
        else:
            temp_dir = tempfile.gettempdir()
            dir_sep = '\\' if system() == 'Windows' else '/'
            export_file = temp_dir + dir_sep + 'export.csv'
            logging.debug('export file : %s', export_file)
            with open(export_file, 'w') as f:
                f.write('site')
                f.write(settings.csv_sep)
                f.write('mail')
                f.write('\n')
                nb_lines = 0
                for x in self.all_mails:
                    if len(x['mails']) > 0:
                        f.write(x['site'])
                        f.write(settings.csv_sep)
                        for m in set(x['mails']):
                            f.write(m)
                            f.write(settings.csv_sep)
                        f.write('\n')
                        nb_lines += 1
                messagebox.showinfo("Info", "%d sites and mails exported in %s" % (nb_lines, export_file))


    def toggle(self):
        if self.search_btn['state'] == DISABLED:
            self.cancel_btn['state'] = DISABLED
            self.search_btn['state'] = NORMAL
            self.txt['state'] = NORMAL
            self.pbar.stop()
        else:
            self.cancel_btn['state'] = NORMAL
            self.search_btn['state'] = DISABLED
            self.txt['state'] = DISABLED
        self.export_btn['state'] = self.search_btn['state']
        self.window.update()


    def cancel(self):
        self.cancel_requested = True
        self.toggle()


    def search(self):
        kw = self.txt.get()
        if kw == '': return
        self.toggle()
        self.list_res.delete(0, END)
        self.window.update()

        serp = googleSearch.search(kw, self.site_to_search)
        self.all_mails = []
        visited_sites = []
        cpt = 0
        scraped_sites = 0
        te = tldextract.TLDExtract(cache_file=get_tld_cache_file())
        for site in serp:
            cpt += 1
            self.list_res.insert(0, site)
            if site.count('/') == 4:
                self.list_res.itemconfig(0, foreground="white", bg="green")
                self.all_mails.append({"site": site, "mails": 'x'})
            else:
                self.list_res.itemconfig(0, foreground="black", bg="white")
            if self.cancel_requested:
                logging.debug('cancel requested')
                break
            else:
                # be nice with google...
                sleeping_time = float(random.randint(2, 9)) / 10
                logging.debug('sleeping {} seconds...'.format(sleeping_time))
                time.sleep(sleeping_time)
            self.pbar.step(100 / settings.nb_serp_results)
            self.window.update()

        self.window.update()
        logging.info('MAILS FOUND')
        for x in self.all_mails:
            if len(x['mails']) > 0:
                mails = ''
                for m in set(x['mails']):
                    mails += m + ' '
                logging.info("site {} : {}".format(x['site'], mails))

        if self.cancel_requested:
            self.cancel_requested = False
        else:
            self.toggle()


    def mainloop(self):
        self.window.mainloop()


    def update(self):
        self.window.update()

