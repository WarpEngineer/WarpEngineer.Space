#!/usr/bin/env python

import urllib2
import json
import time

URL = "https://nhl-score-api.herokuapp.com/api/scores/latest"

def main():
	try:
		f = urllib2.urlopen(URL)
	except:
		print "# Oops! Something went wrong"
		return 1

	data_coded = f.read()
	data_decoded = json.loads(data_coded)
	try:
		game_date = data_decoded['date']['pretty']
	except:
		print "# Oops! Something went wrong"
		return 1

	print "# WarpEngineer's NHL Scores"
	print "## %s" % game_date
	print "### Updated every 10 minutes or so"
	print "### Last update: %sZ" % time.asctime()

	try:
		games = data_decoded['games']
	except:
		print "# Oops! Something went wrong"
		return 1

	try:
		if len(games) > 0 and type(games) is list:
			for game in games:
				away_team = game['teams']['away']['abbreviation']
				home_team = game['teams']['home']['abbreviation']
				print
				print "# %s at %s" % ( away_team, home_team )
				current_state  = game['status']['state']
				if current_state.lower() == "live":
					current_period = game['status']['progress']['currentPeriod']
					if int(current_period) > '3':
						current_period = 'OT'
					current_remain = game['status']['progress']['currentPeriodTimeRemaining']['pretty']
					away_scrore = game['scores'][away_team]
					home_scrore = game['scores'][home_team]
					if current_remain.lower() == "end":
						if int(current_period) == 1:
							period = "1st"
						elif int(current_period) == 2:
							period = "2nd"
						elif int(current_period) == 3:
							period = "3rd"
						else:
							period = ""
						print "## END of %s Period" % period
					else:
						print "## Period: %s   Time Remaining: %s" % (current_period, current_remain)
					print "### %s: %s" % ( away_team, away_scrore )
					print "### %s: %s" % ( home_team, home_scrore )
				elif current_state.lower() == "final":
					away_scrore = game['scores'][away_team]
					home_scrore = game['scores'][home_team]
					overtime = None
					if game['scores'].has_key('overtime'):
						overtime = game['scores']['overtime']
					print "### %s: %s" % ( away_team, away_scrore )
					print "### %s: %s" % ( home_team, home_scrore )
					if overtime:
						print "### Final Overtime"
					else:
						print "### Final"
				elif current_state.lower() == "preview":
					start_time = game['startTime']
					print "## Starts at %s" % start_time
				print

	except:
		print "# Oops! Something went wrong"
		return 1

	return 0

if __name__ == "__main__":
	main()

