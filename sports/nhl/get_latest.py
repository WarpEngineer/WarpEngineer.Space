#!/usr/bin/env python

import os
# set time zone to eastern
os.putenv("TZ","America/New_York")

import urllib2
import json
import time
from datetime import datetime
from tz import UTC, LocalTimezone

# Date format = YYYY-MM-DD
URL = "https://statsapi.web.nhl.com/api/v1/schedule?startDate=%s&endDate=%s&hydrate=team(leaders(categories=[points,goals,assists],gameTypes=[R])),linescore,broadcasts(all),tickets,game(content(media(epg),highlights(scoreboard)),seriesSummary),radioBroadcasts,metadata,decisions,scoringplays,seriesSummary(series)&site=en_nhl&teamId=&gameType=&timecode="

def error(msg=None):
	print "# Oops! Something went wrong"
	if msg:
		err_file = os.path.join(os.getenv("HOME"), "nhl_error.%s.log" % time.strftime("%Y_%m_%d_%H_%M"))
		f = open(err_file, "w")
		f.write(msg)
		f.close()
	return 1

def main():
	query_date = time.strftime("%Y-%m-%d")
	try:
		op = urllib2.build_opener()
		op.addheaders = [('User-Agent', 'Mozilla/5.0')]
		f = op.open(URL % ( query_date, query_date  ))
	except:
		return error("Failed to fetch")

	data_coded = f.read()
	data_decoded = json.loads(data_coded)
	try:
		game_date = data_decoded['dates'][0]['date']
	except:
		return error(data_coded)
	try:
		game_time = time.strptime(game_date,"%Y-%m-%d")
		game_date = time.strftime("%a %b %d", game_time)
	except:
		# just use it as is then
		pass

	print "# WarpEngineer's NHL Scores"
	print "## Games for %s" % game_date
	print "### All times are Eastern"
	print "### Updated every 10 minutes or so"
	print "### Last update: %s" % time.asctime()

	try:
		games = data_decoded['dates'][0]['games']
	except:
		return error(data_coded)

	try:
		if len(games) > 0 and type(games) is list:
			for game in games:
				away_team = game['teams']['away']['team']['abbreviation']
				home_team = game['teams']['home']['team']['abbreviation']
				print
				print "# %s at %s" % ( away_team, home_team )
				current_state  = game['status']['codedGameState']
				if current_state.lower() in ["3","4"]: # in progess
					current_period = game['linescore']['currentPeriod']
					current_period_ord = game['linescore']['currentPeriodOrdinal']
					if int(current_period) > 3:
						current_period = 'OT'
					current_remain = game['linescore']['currentPeriodTimeRemaining']
					away_scrore = game['teams']['away']['score']
					home_scrore = game['teams']['home']['score']
					if current_remain.lower() == "end":
						print "## END of %s Period" % current_period_ord
					else:
						print "## Period: %s   Time Remaining: %s" % (current_period, current_remain)
					print "### %s: %s" % ( away_team, away_scrore )
					print "### %s: %s" % ( home_team, home_scrore )
				elif current_state.lower() in ["5", "6", "7"]: # final
					away_scrore = game['teams']['away']['score']
					home_scrore = game['teams']['home']['score']
					current_period = game['linescore']['currentPeriod']
					overtime = ""
					if int(current_period) > 3:
						overtime = "Overtime"
					if game['linescore']['hasShootout']:
						overtime = "OT/SO"
					print "### %s: %s" % ( away_team, away_scrore )
					print "### %s: %s" % ( home_team, home_scrore )
					print "### Final %s" % overtime
				elif current_state.lower() in ["1", "2"]: # preview, scheduled
					start_time = game['gameDate']
					try:
						t = datetime.strptime(start_time,"%Y-%m-%dT%H:%M:%SZ")
						t1 = datetime(t.year,t.month,t.day,t.hour,t.minute,t.second,tzinfo=UTC())
						start_time = t1.astimezone(LocalTimezone()).strftime("%Y-%m-%d %H:%M")
					except:
						# just use as is then
						pass
					print "## Starts at %s" % start_time
				print
		print
		print "version 0.3"

	except:
		return error(data_coded)

	return 0

if __name__ == "__main__":
	main()

