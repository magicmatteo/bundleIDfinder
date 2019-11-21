
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from urllib import request
import requests, csv, sys, os

if len(sys.argv) < 2:
	print("\nYou Must enter a csv filename! For example...\nbundleid.py apps.csv\n For help run --help")
	sys.exit()

if sys.argv[1].lower() == '--help':
	print(
		'''
		Welcome to the Apple App BundleID finder.
		-------------------------------------

		This takes input from a CSV containing the names of apps you want a Bundle ID for.
		The CSV does not need a header. Place all apps in the first column.

		** IMPORTANT **
		You must use the most accurate title you can. Ideally the title as displayed in
		the app store.

		To use program, run it with an argument of your chosen CSV file.

		Example: ./bundleID.py my_app_list.csv

		The program will output "results.csv" with all of the matched data.

		Please contact magicmatteo on GitHub for issues.

		''')
	sys.exit()

if os.path.exists(sys.argv[1]):
	reader = csv.reader(open(sys.argv[1]))
else:
	print("File not found. Please enter a valid CSV filename.")

#Check for http proxy settings
systemProxy = request.getproxies()

# Parse through CSV adding each entry to apps LIST.
apps = []
for row in reader:
	apps.append(row[0])

# This function grabs the numeric ID out of the app store URL.
def find_ID(url):
	return url.partition('id')[2].partition('?')[0]

# Declare matches outside of loops to prevent overwrite
matches = []
failures = []

for app in apps:
	appToFind = app
	appForURL = appToFind.translate({ord(' '): ord('-')}).lower() # Translate sapces to hyphons for URL

	count = 0

	# Skip apps with symbols and explain.
	if set('[~!@#$%^&*()_+{}":;\']+$').intersection(app):
		print('We found symbols in: %s - Please remove them' % app)
		continue

	h = {'rawUa': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15',
	  'referer': 'https://google.com.au'}

	payload = {'search': appForURL, 'platform': 'iPadSoftware'}

	r = requests.get('https://theappstore.org/search.php', params=payload, headers=h, proxies=systemProxy)

	soup = BeautifulSoup(r.text, 'html.parser')

	for item in soup.find_all('div', class_='appmain'):
		title = item.find('div', class_='apptitle').text.translate({ord(' '): None}).strip()
		appURL = item.find('a', href=True)['href']
		appID = find_ID(appURL)

		s = SequenceMatcher(a=title, b=appToFind)
		
		# Find anything that has a very high match ratio and create a dict of its values then
		# append those to the matches list
		if s.ratio() > .80:
			match = {'title': title,
					 'ID'	: appID,
					 'ratio': s.ratio()}
			matches.append(match)
			count += 1

	if count == 0:
		failures.append(app)

if matches:
	print('We found %s out of %s matches' % (len(matches), len(apps)))
	with open('results.csv', mode='w') as csv_file:
		fieldnames = ['title', 'ID', 'bundleID', 'ratio']
		writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
		
		writer.writeheader() #write header outside of loop for only one entry
		
		# for each match, get the bundle ID out of json from request to itunes using the
		# numeric app ID. Add bundle ID to dict and write all data to CSV
		for m in matches:
			itunesURL = 'https://itunes.apple.com/lookup?id=' + m['ID']
			r = requests.get(itunesURL)
			appManifest = r.json()['results']
			m['bundleID'] = appManifest[0]['bundleId']
			writer.writerow(m)

else: print('No matches found for any apps in list.')

if failures:
	for n in failures:
		print('%s was not found in the store' % (n))
