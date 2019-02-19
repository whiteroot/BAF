import os
import logging
import tempfile

import regex
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Progressbar

from googleSearch import GoogleScraper
import settings
from utils import get_tld_cache_file


def millions():
    for i in range(2, 0, -1):
        for j in range(9, 0, -1):
            yield "{}.{}m".format(i, j)
        yield "{}m".format(i)


class gui():

    def __init__(self, resolution, current_resolution, ign_urls):
        self.url_to_search = 'instagram.com'
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

        self.txt = Entry(self.window, width=int(tk_width * 0.55))
        self.txt.grid(column=1, row=1, padx=20, pady=10)
        self.txt.focus()

        self.search_btn = Button(self.window, text="Search", command=lambda inst=self: inst.search())
        self.search_btn.grid(column=2, row=1, pady=5)

        self.lbl_count = Label(self.window, text="")
        self.lbl_count.grid(column=3, row=1, padx=20, pady=5)

        self.export_btn = Button(self.window, text="Export", command=lambda inst=self: inst.export())
        self.export_btn.grid(column=1, row=2, pady=5)

        self.cancel_btn = Button(self.window, text="Cancel", command=lambda inst=self: inst.cancel())
        self.cancel_btn.grid(column=2, row=2, pady=5)

        self.lbl_info = Label(self.window, text="")
        self.lbl_info.grid(column=3, row=2, padx=20, pady=5, columnspan=3)

        self.list_res = Listbox(self.window, width=int(tk_width * 0.9), height=int(tk_height * 0.85))
        self.list_res.grid(column=1, row=3, padx=20, pady=3, columnspan=3)

        self.pbar = Progressbar(self.window, orient=HORIZONTAL, length=int(cur_width * 0.8), mode='determinate')
        self.pbar.grid(column=1, row=4, padx=20, pady=20, columnspan=3)

        self.cancel_requested = False
        self.ignored_urls = ign_urls
        self.big_accounts = []


    def export(self):
        if len(self.big_accounts) == 0:
            messagebox.showinfo("Info", "No account to export!")
        else:
            temp_dir = tempfile.gettempdir()
            export_file = "{}{}baf.{}.csv".format(temp_dir, os.sep, self.txt.get().replace(' ', '-'))
            logging.debug('export file : %s', export_file)
            with open(export_file, 'w') as f:
                f.write('account')
                f.write(settings.csv_sep)
                f.write('followers')
                f.write('\n')
                nb_lines = 0
                for x,y in self.big_accounts:
                    f.write(x)
                    f.write(settings.csv_sep)
                    f.write(y)
                    f.write('\n')
                    nb_lines += 1
                messagebox.showinfo("Info", "%d big accounts exported in %s" % (nb_lines, export_file))


    def toggle(self):
        if self.search_btn['state'] == DISABLED:
            logging.info('toggle ON')
            self.cancel_btn['state'] = DISABLED
            self.search_btn['state'] = NORMAL
            self.txt['state'] = NORMAL
            self.pbar.stop()
        else:
            logging.info('toggle OFF')
            self.cancel_btn['state'] = NORMAL
            self.search_btn['state'] = DISABLED
            self.txt['state'] = DISABLED
        self.export_btn['state'] = self.search_btn['state']
        self.window.update()


    def cancel(self):
        self.cancel_requested = True
        self.toggle()


    def search(self):
        if self.txt.get() == '': return
        self.cancel_requested = False
        self.toggle()
        self.list_res.delete(0, END)
        self.window.update()
        self.big_accounts = []
        google_scraper = GoogleScraper(self, 10)

        for n in millions():
            if self.cancel_requested:
                logging.info('cancel requested')
                break
            try:
                self.lbl_info['text'] = "Searching accounts with {} followers".format(n)
                self.searchMillion(n, google_scraper)
            except Exception as e:
                # most often, a captcha error
                logging.fatal(e)
                break
            self.window.update()

        logging.info('BIG ACCOUNTS FOUND: {}'.format(len(self.big_accounts)))


    def searchMillion(self, n, google_scraper):
        kw = "{} {} Followers -tag -explore".format(self.txt.get(), n)
        logging.info('searching: {}'.format(kw))
        serp = google_scraper.search(kw, self.url_to_search)
        cpt = 0
        for url in serp:
            cpt += 1
            if url.count('/') == 4:
                logging.info('url: {}'.format(url))
                m = regex.match(".*gram.com/(.*)/", url)
                if m:
                    account = m.groups()[0]
                    self.list_res.insert(0, account)
                    self.list_res.itemconfig(0, foreground="white", bg="blue")
                    logging.info('account: {}'.format(account))
                    self.big_accounts.append( (account, n) )
            self.pbar.step(100 / settings.nb_serp_results)
            self.lbl_count['text'] = "{} account{} found".format(
                    len(self.big_accounts),
                    's' if len(self.big_accounts)>1 else '')
            self.window.update()
            if self.cancel_requested:
                logging.info('cancel requested')
                break
            if len(self.big_accounts) > 99:
                break


    def mainloop(self):
        self.window.mainloop()


    def update(self):
        self.window.update()

