import requests
import re
import random
import sys

def make_request(): # Function to extract proxy data. Returns list.
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
	           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	           'Accept-Encoding': 'none',
	           'Accept-Language': 'en-US,en;q=0.8',
		   'Connection': 'keep-alive',
	           'Content-Encoding': 'gzip',
	           'Content-Type': 'text/html; charset=utf-8',}
	response = requests.get('https://free-proxy-list.net/', headers=headers).text # makes request to the site and retrieves source code
	# Regex to extract "valuable stuff" from the source code.
	return re.findall(r"<tr><td>[^<]*</td><td>[^<]*</td><td>[^<]*</td><td class='hm'>[^<]*</td><td>[^<]*</td><td class='hm'>[^<]*</td><td class='hx'>[^<]*</td><td class='hm'>[^<]*</td></tr>", response)

def one(): # function to fetch one proxy. Returns string.
	match = random.choice(make_request()) # selects random item from "valuable stuff" list
	result = match.split('</td>') # makes list of match by spliting it from '</td>'
	ip_address = result[0].strip('<tr><td>') # fetches first item of result list and removes '<tr><td>' from it
	port = result[1].strip('</td>') # fetches 2nd item of result list and removes '</td>' from it
	if result[6].strip('<td class=\'hx\'>') == 'yes': # fetches fifth item of result list and removes ''<td class='hx'>'' from it and checks if its equal to 'yes'
		typ = 'https'
	else:
		typ = 'http'
	return typ + '://' + ip_address + ':' + port # returns http(s)://ip_address:port

def many(): # function to fetch many proxies. Returns list.
	proxies = [] # list to store proxies, obvious lmao
	for match in make_request(): # iterating over the "valueable stuff" list
		result = match.split('</td>') # makes list of match by spliting it from '</td>'
		ip_address = result[0].strip('<tr><td>') # fetches first item of result list and removes '<tr><td>' from it
		port = result[1].strip('</td>') # fetches 2nd item of result list and removes '</td>' from it
		if result[6].strip('<td class=\'hx\'>') == 'yes': # fetches fifth item of result list and removes ''<td class='hx'>'' from it and checks if its equal to 'yes'
			typ = 'https'
		else:
			typ = 'http'
		proxies.append(typ + '://' + ip_address + ':' + port)
	return proxies

def get(number): # function to fetch specific number of proxies. Returns list.
	proxies = [] # list to store proxies, obvious lmao
	if number > 300: # Maximum number of proxies we can fetch in one is 300
		number = 300
	matches = make_request()[:number] # fetching n items from the "valueable stuff" list
	for match in matches: # iterating over the n items
		result = match.split('</td>') # makes list of match by spliting it from '</td>'
		ip_address = result[0].strip('<tr><td>') # fetches first item of result list and removes '<tr><td>' from it
		port = result[1].strip('</td>') # fetches 2nd item of result list and removes '</td>' from it
		if result[6].strip('<td class=\'hx\'>') == 'yes': # fetches fifth item of result list and removes ''<td class='hx'>'' from it and checks if its equal to 'yes'
			typ = 'https'
		else:
			typ = 'http'
		proxies.append(typ + '://' + ip_address + ':' + port)
	return proxies

if __name__ == '__main__':
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    else:
        n = 50
    p = get(n)
    print (p)
    print ("{} proxies".format(len(p)))

