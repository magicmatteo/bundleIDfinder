# bundleIDfinder

I was having trouble.. sort of.. manual labour trouble.. getting the bundle ID's for ipad apps for use in my MDM (MS intune). To exclude certain apps from view or to reorganise them as per your design, you need to specify the apps Bundle ID. This became a 3 step process for me. I first needed a way of searching the app store.. which isnt native on a windows PC using a web browser.. I found a site (that is no longer maintained I believe) called theappstore.org.

This site allows you to search the app store basically. Upon finding the correct app on this, you need to click the link to get the app ID ie 998767232.. This is a long numeric string. You then need to insert this into an apple URL to lookup the app, which return a txt file download with some JSON data that contains your bundle ID at the end.

So you can see.. this is an annoying manual process. Doing this 100 times would be greuling..

I guess I'd say that this project was more for my development in python than anything. Since it took 7 hours.. I wont be saving any time in the long run. Learnt plenty though.

I though I'd put it up incase someone else finds it useful or would have any advice or improvements.

I could be completely wasting time in lieu of another solution... But I enjoyed it.

I will post the --help argument output below:

		Welcome to the Apple App BundleID finder.
		-------------------------------------

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
