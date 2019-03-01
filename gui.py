import os
import logging
import tempfile
from random import shuffle, seed

import regex
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Progressbar

from googleSearch import GoogleScraper
import settings
from utils import getMillionList, KILO, MEGA

# format of each element of the list: (row, column, min, max, prefix)
nbFollowerSearch = [
        (1, 1, 10, 99, KILO),
        (1, 2, 100, 999, KILO),
        (1, 3, 1, 4, MEGA),
        (2, 1, 5, 9, MEGA),
        (2, 2, 10, 49, MEGA),
        (2, 3, 50, 99, MEGA)
        ]
SUB_LIST_LENGTH = 10


class gui():

    def __init__(self, resolution, current_resolution):
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
        self.lbl_search.grid(column=1, row=1, padx=20, pady=20)

        self.txt = Entry(self.window, width=int(tk_width * 0.5))
        self.txt.grid(column=2, row=1, padx=20, pady=20)
        self.txt.focus()

        self.search_btn = Button(self.window, text="Search", command=lambda inst=self: inst.search())
        self.search_btn.grid(column=1, row=10, pady=5)

        self.export_btn = Button(self.window, text="Export", command=lambda inst=self: inst.export(), state=DISABLED)
        self.export_btn.grid(column=2, row=10, pady=5)

        self.cancel_btn = Button(self.window, text="Cancel", command=lambda inst=self: inst.cancel(), state=DISABLED)
        self.cancel_btn.grid(column=3, row=10, pady=5)

        self.nbFollowers = IntVar()
        self.rbNbFollowers = []
        i = 0
        for x, y, min_value, max_value, prefix in nbFollowerSearch:
            self.rbNbFollowers.append(Radiobutton(self.window, text="{} to {} {}".format(min_value, max_value, prefix),
                        variable=self.nbFollowers, value=i, command=lambda inst=self: inst.selectNbFollowers()))
            self.rbNbFollowers[i].grid(column=y, row=15+x, padx=2, pady=5)
            i += 1
        self.nbFollowers.set(3)

        self.lbl_count = Label(self.window, text="")
        self.lbl_count.grid(column=1, row=20, padx=20, pady=5, columnspan=3)

        self.lbl_info = Label(self.window, text="")
        self.lbl_info.grid(column=1, row=25, padx=20, pady=5, columnspan=3)

        self.list_res = Listbox(self.window, width=int(tk_width),
                height=int(tk_height * 0.75), font=("Courier", 10, "bold"))
        self.list_res.grid(column=1, row=30, padx=80, pady=3, columnspan=3)

        self.cancel_requested = False
        self.big_accounts = []
        self.update()


    def millions(self):
        s = nbFollowerSearch[self.nbFollowers.get()]
        self.millionList = getMillionList(s[2], s[3], s[4])
        seed()
        shuffle(self.millionList)
        while self.millionList:
            list10 = [ self.format_q(n,x) for n,x in list(enumerate(self.millionList[:SUB_LIST_LENGTH])) ]
            str10 = "".join(list10)
            logging.debug(str10)
            for i in range(10):
                del self.millionList[0]
            yield str10

    def format_q(self, i, x):
        if x[1] == 0:
            decimal_part = ""
        else:
            decimal_part = ".{}".format(x[1])
        if i == 0:
            return "({}{}{} ".format(x[0], decimal_part, x[2])
        elif i == SUB_LIST_LENGTH-1:
            return "OR {}{}{})".format(x[0], decimal_part, x[2])
        else:
            return "OR {}{}{} ".format(x[0], decimal_part, x[2])


    def selectNbFollowers(self):
        self.update()


    def export(self):
        if len(self.big_accounts) == 0:
            messagebox.showinfo("Info", "No account to export!")
        else:
            temp_dir = tempfile.gettempdir()
            export_file = "{}{}baf.{}.csv".format(temp_dir, os.sep, self.txt.get().replace(' ', '-'))
            logging.debug('export file : %s', export_file)
            s = nbFollowerSearch[self.nbFollowers.get()]
            prefix = s[4]
            with open(export_file, 'w') as f:
                f.write('account')
                f.write(settings.csv_sep)
                f.write('followers')
                f.write('\n')
                nb_lines = 0
                for x,y in self.big_accounts:
                    f.write(x)
                    f.write(settings.csv_sep)
                    f.write("{}{}".format(y, prefix))
                    f.write('\n')
                    nb_lines += 1
                messagebox.showinfo("Info", "%d big accounts exported in %s" % (nb_lines, export_file))


    def toggle(self):
        if self.search_btn['state'] == DISABLED:
            logging.info('toggle ON')
            self.cancel_btn['state'] = DISABLED
            self.search_btn['state'] = NORMAL
            self.txt['state'] = NORMAL
            self.lbl_info['text'] = ''
        else:
            logging.info('toggle OFF')
            self.cancel_btn['state'] = NORMAL
            self.search_btn['state'] = DISABLED
            self.txt['state'] = DISABLED
            self.lbl_count['text'] = ''
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
        self.update()
        self.big_accounts = []
        google_scraper = GoogleScraper(self, 10)

        for q in self.millions():
            if self.cancel_requested:
                logging.info('cancel requested')
                break
            try:
                self.searchMillion(q, google_scraper)
            except Exception as e:
                # most often, a captcha error
                logging.fatal(e)
                break

        logging.info('BIG ACCOUNTS FOUND: {}'.format(len(self.big_accounts)))


    def searchMillion(self, q, google_scraper):
        kw = "{} {} Followers -tag -explore".format(self.txt.get(), q)
        logging.info('searching: {}'.format(kw))
        self.lbl_info['text'] = "Searching accounts..."
        self.update()
        s = nbFollowerSearch[self.nbFollowers.get()]
        prefix = s[4]

        serp = google_scraper.search(kw, self.url_to_search)
        for url, info, nb in serp:
            if self.cancel_requested:
                logging.info('cancel requested')
                break
            self.update()
            logging.info('url: {}'.format(url))

            m = regex.match(".*gram.com/(.*)/", url)
            if m:
                account = m.groups()[0]
                if (account, nb) in self.big_accounts:
                    logging.info(f"{account} already selected")
                else:
                    list_elt = f"{account:30s} {nb:6s}{prefix}"
                    self.list_res.insert(0, list_elt)
                    self.list_res.itemconfig(0, foreground="white", bg="blue")
                    logging.info('account: {}'.format(account))
                    self.big_accounts.append( (account, nb) )

            self.lbl_count['text'] = "{} account{} found".format(
                    len(self.big_accounts),
                    's' if len(self.big_accounts)>1 else '')
            self.update()


    def mainloop(self):
        self.window.mainloop()


    def update(self):
        self.window.update()
