from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from urllib import request
import requests, csv, sys, os

help_text = '''
Welcome to the Apple App BundleID finder.
-------------------------------------------

** IMPORTANT **
You must use the most accurate title you can. Ideally the title as displayed in
the app store.

To use program, either run it with no arugument or with the argument --csv to specifiy
a csv file with a list of apps.

Example: ./bundleID.py
When running without arguments, you will be prompted to add apps to the list by selecting the 'A' option in the menu. When you have finished adding apps, choose the 'D' option to return your reults.

-- csv:
Example: ./bundleID.py --csv my_app_list.csv
This takes input from a CSV containing the names of apps you want a Bundle ID for.
The CSV does not need a header. Place all apps in the first column.
When using the csv option, the program will output "results.csv" with all of the matched data.

Please contact magicmatteo on GitHub for issues.
'''

def program_mode():
	global mode
	
	if len(sys.argv) < 2:
		mode = 'single'

	elif sys.argv[1].lower() == '--csv':
		mode = 'csv'

	elif sys.argv[1].lower() == '--help':
		print(help_text)
		sys.exit()

def single_menu():
	count = 0
	while True:
		if count == 0:
			print('\nWelcome to the bundleIDfinder.. run bundleIDfinder --help for help.\nPlease choose from the following options:')
			count =+ 1
		selection = input('\nA: Add app to list\nD: Done adding apps\nQ: Quit\nSelection: ')
		if selection.lower() == 'a':
			a = input('\nEnter name of app: ')
			apps.append(a)
			print(f'{a} added')

		elif selection.lower() == 'd':
			break
		elif selection.lower() == 'q':
			sys.exit()
		else: print('Please enter a valid response')

def csv_reader():
	if os.path.exists(sys.argv[2]):
		reader = csv.reader(open(sys.argv[2]))
		try:
			for row in reader:
				apps.append(row[0])
		except IndexError:
			print('Please verify CSV file. Consult --help for help.')
			sys.exit()

	else:
		print("File not found. Please enter a valid CSV filename.")
		sys.exit()

program_mode()

# Check for http proxy settings
systemProxy = request.getproxies()

# Declare apps list outside of loops
apps = []

# if CSV mode, Parse through CSV adding each entry to apps LIST.
if mode == 'csv':
	csv_reader()

#if single mode, present menu
if mode == 'single':
	single_menu()


# This function grabs the numeric ID out of the app store URL.
def find_id(url):
	return url.partition('id')[2].partition('?')[0]


# Declare matches outside of loops to prevent overwrite
matches = []
failures = []

for app in apps:
    appToFind = app
    appForURL = appToFind.translate({ord(' '): ord('-')}).lower()  # Translate sapces to hyphons for URL

    count = 0

    # Skip apps with symbols and explain.
    if set('[~!@#$%^&*()_+{}":;\']+$').intersection(app):
        print('We found symbols in: %s - Please remove them' % app)
        continue

    h = {
        'rawUa': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15',
        'referer': 'https://google.com.au'}

    payload = {'search': appForURL, 'platform': 'iPadSoftware'}

    r = requests.get('https://theappstore.org/search.php', params=payload, headers=h, proxies=systemProxy)

    soup = BeautifulSoup(r.text, 'html.parser')

    for item in soup.find_all('div', class_='appmain'):
        title = item.find('div', class_='apptitle').text.translate({ord(' '): None}).strip()
        appURL = item.find('a', href=True)['href']
        appID = find_id(appURL)

        s = SequenceMatcher(a=title, b=appToFind)

        # Find anything that has a high match ratio and create a dict of its values then
        # append those to the matches list
        if s.ratio() > .70:
            match = {'title': title,
                     'ID': appID,
                     'ratio': s.ratio()}
            matches.append(match)
            count += 1

    if count == 0:
        failures.append(app)

if matches:
    print('We found %s matches for %s apps' % (len(matches), len(apps)))
    
    if mode == 'csv':
	    with open('results.csv', mode='w') as csv_file:
	        fieldnames = ['title', 'ID', 'bundleID', 'ratio']
	        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

	        writer.writeheader()  # write header outside of loop for only one entry

	        # for each match, get the bundle ID out of json from request to itunes using the
	        # numeric app ID. Add bundle ID to dict and write all data to CSV
	        for m in matches:
	            itunesURL = 'https://itunes.apple.com/lookup?id=' + m['ID']
	            r = requests.get(itunesURL)
	            appManifest = r.json()['results']
	            m['bundleID'] = appManifest[0]['bundleId']
	            writer.writerow(m)
    
    if mode == 'single':

    	for m in matches:
	            itunesURL = 'https://itunes.apple.com/lookup?id=' + m['ID']
	            r = requests.get(itunesURL)
	            appManifest = r.json()['results']
	            m['bundleID'] = appManifest[0]['bundleId']
	            print('App name: {} - {}'.format(m['title'], m['bundleID']))


else:
    print('No matches found for any apps in list.')

if failures:
    for n in failures:
        print('%s was not found in the store' % (n))
