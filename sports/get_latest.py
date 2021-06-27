#!/usr/bin/env python
###vim: set encoding=utf-8 :

import os
# set time zone to eastern
os.putenv("TZ","America/New_York")

import sys
import urllib2
import json
import time
from datetime import datetime, timedelta
from tz import UTC, LocalTimezone

VERSION = "version 0.8"

# Date format = YYYY-MM-DD
URL_NHL = "https://statsapi.web.nhl.com/api/v1/schedule?startDate=%s&endDate=%s&hydrate=team(leaders(categories=[points,goals,assists],gameTypes=[R])),linescore,broadcasts(all),tickets,game(content(media(epg),highlights(scoreboard)),seriesSummary),radioBroadcasts,metadata,decisions,scoringplays,seriesSummary(series)&site=en_nhl&teamId=&gameType=&timecode="
URL_MLB = "https://bdfed.stitch.mlbinfra.com/bdfed/transform-mlb-scoreboard?stitch_env=prod&sortTemplate=4&sportId=1&startDate=%s&endDate=%s&gameType=E,S,R,F,D,L,W,A&=,,,,,,,&language=en&leagueId=103,104"

def error(msg=None, sport=""):
	print "# Oops! Something went wrong"
	if msg:
		err_file = os.path.join(os.getenv("HOME"), "%s_error.%s.log" % (sport,time.strftime("%Y_%m_%d_%H_%M")))
		f = open(err_file, "w")
		f.write(msg)
		f.close()
	return 1

def format_nhl_game(game):
	away_team = game['teams']['away']['team']['abbreviation']
	home_team = game['teams']['home']['team']['abbreviation']
	game_type = '' if game['gameType'].lower() == 'r' else '(post-season)'
	game_number = ''
	if game_type != '':
		game_number = game['seriesSummary']['gameLabel']
		series_status = game['seriesSummary']['seriesStatusShort']
	print
	print "# %s at %s %s %s" % ( away_team, home_team, game_number, game_type )
	if game_type != '':
		print "### Series: %s" % ( series_status )
	current_state  = game['status']['codedGameState']
	if current_state.lower() in ["3","4"]: # in progess
		current_period = game['linescore']['currentPeriodOrdinal']
		current_period_ord = game['linescore']['currentPeriodOrdinal']
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
			overtime = game['linescore']['currentPeriodOrdinal']
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

def format_mlb_game(game):
	away_team = game['teams']['away']['team']['abbreviation']
	home_team = game['teams']['home']['team']['abbreviation']
	game_type = "" if game['gameType'].lower() == 'r' else '(post-season)'
	game_number = "" if game['doubleHeader'].lower() == "n" else "game #" + str(game['gameNumber'])
	print
	print "# %s at %s %s %s" % ( away_team, home_team, game_number, game_type )
	current_state = game['status']['codedGameState']
	if current_state.lower() == "i": # in progress
		current_inning = game['linescore']['currentInning']
		current_inning_state = game['linescore']['inningState']
		away_scrore = game['teams']['away']['score']
		home_scrore = game['teams']['home']['score']
		print "## %s of Inning %s" % (current_inning_state, current_inning)
		print "### %s: %s" % ( away_team, away_scrore )
		print "### %s: %s" % ( home_team, home_scrore )
	elif current_state.lower() in ["f","o"]: # final, over
		current_inning = game['linescore']['currentInning']
		scheduled_innings = game['linescore']['scheduledInnings']
		away_scrore = game['teams']['away']['score']
		home_scrore = game['teams']['home']['score']
		if int(current_inning) > int(scheduled_innings):
			print "## Final Score/%s" % current_inning
		else:
			print "## Final Score"
		print "### %s: %s" % ( away_team, away_scrore )
		print "### %s: %s" % ( home_team, home_scrore )
	elif current_state.lower() == 'd': # delayed, postponed
		print '## Postponed: %s' % game['status']['reason']
	elif current_state.lower() == 'u': # suspended
		print '## %s' % game['status']['reason']
	elif current_state.lower() in ['s','p']: # scheduled, preview
		start_time = game['gameDate']
		try:
			t = datetime.strptime(start_time,"%Y-%m-%dT%H:%M:%SZ")
			t1 = datetime(t.year,t.month,t.day,t.hour,t.minute,t.second,tzinfo=UTC())
			start_time = t1.astimezone(LocalTimezone()).strftime("%Y-%m-%d %H:%M")
		except:
			# just use as is then
			pass
		print "## Starts at %s" % start_time

def main():
	# pointers: White Left Pointing Backhand Index Emoji, White Right Pointing Backhand Index Emoji
	# argv1: nhl|mlb
	# argv2: today|yesterday|tomorrow
	sport = sys.argv[1]
	if sport == 'nhl':
		URL = URL_NHL
	else:
		URL = URL_MLB
	which_day = sys.argv[2].lower()
	td = timedelta(1)
	if which_day == "today":
		query_date = datetime.now().strftime("%Y-%m-%d")
		update_line = "### Updated every 10 minutes or so"
		day_links = "=> yesterday.gemini 👈 yesterday\n"
		day_links += "=> tomorrow.gemini 👉 tomorrow"
	elif which_day == "yesterday":
		query_date = (datetime.now() - td).strftime("%Y-%m-%d")
		update_line = "### Updated once or twice a day"
		day_links = "=> index.gemini 👉 today\n"
		day_links += "=> tomorrow.gemini 👉 tomorrow"
	else:
		query_date = (datetime.now() + td).strftime("%Y-%m-%d")
		update_line = "### Updated once or twice a day"
		day_links = "=> index.gemini 👈 today\n"
		day_links += "=> yesterday.gemini 👈 yesterday"
	try:
		op = urllib2.build_opener()
		op.addheaders = [('User-Agent', 'Mozilla/5.0')]
		f = op.open(URL % ( query_date, query_date ))
	except:
		return error("Failed to fetch", sport)

	data_coded = f.read()
	data_decoded = json.loads(data_coded)
	try:
                if len(data_decoded['dates']):
                    game_date = data_decoded['dates'][0]['date']
                else:
                    game_date = 'this day'
	except:
		return error(data_coded, sport)
	try:
		game_time = time.strptime(game_date,"%Y-%m-%d")
		game_date = time.strftime("%a %b %d", game_time)
	except:
		# just use it as is then
		pass

	print "# WarpEngineer's %s Scores" % sport.upper()
	print "## Games for %s" % game_date
	print day_links
	print "### All times are Eastern"
	print update_line
	print "### Last update: %s" % time.asctime()

	try:
                if len(data_decoded['dates']):
                    games = data_decoded['dates'][0]['games']
                else:
                    games = []
	except:
		return error(data_coded, sport)

	try:
		if len(games) > 0 and type(games) is list:
			for game in games:
				if sport == 'nhl':
					format_nhl_game(game)
				else:
					format_mlb_game(game)
				print
		print
		print VERSION

	except:
		return error(data_coded, sport)

	return 0

if __name__ == "__main__":
	main()

