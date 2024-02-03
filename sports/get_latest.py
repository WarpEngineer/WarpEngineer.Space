#!/usr/bin/env python3
###vim: set encoding=utf-8 :

import os
# set time zone to eastern
os.environ["TZ"] = "America/New_York"

import sys
from urllib.request import build_opener
import json
import time
from datetime import datetime, timedelta
#from tz import UTC, LocalTimezone
from backports.zoneinfo import ZoneInfo

VERSION = "version 0.10.0"

# Date format = YYYY-MM-DD
URL_NHL = "https://api-web.nhle.com/v1/score/%s"
URL_MLB = "https://bdfed.stitch.mlbinfra.com/bdfed/transform-mlb-scoreboard?stitch_env=prod&sortTemplate=4&sportId=1&startDate=%s&endDate=%s&gameType=E,S,R,F,D,L,W,A&=,,,,,,,&language=en&leagueId=103,104"

def error(msg=None, sport=""):
	print("# Oops! Something went wrong")
	if msg:
		err_file = os.path.join(os.getenv("HOME"), "%s_error.%s.log" % (sport,time.strftime("%Y_%m_%d_%H_%M")))
		f = open(err_file, "w")
		f.write(msg)
		f.close()
	return 1

def format_nhl_game(game):
	away_team = game['awayTeam']['abbrev']
	home_team = game['homeTeam']['abbrev']
	if game['gameType'] == 1:
		game_type = '(pre-season)'
	elif game['gameType'] == 2:
		game_type = ''
	elif game['gameType'] == 4:
		game_type = '(all-star)'
	else:
		game_type = '(post-season)'
	game_number = ''
	series_status = ''
	if game_type != '':
		try:
			game_number = game['seriesSummary']['gameLabel']
			series_status = game['seriesSummary']['seriesStatusShort']
		except:
			pass
	print()
	print("# %s at %s %s %s" % ( away_team, home_team, game_number, game_type ))
	if game_type != '' and series_status != '':
		print("### Series: %s" % ( series_status ))
	current_state  = game['gameState'].lower()
	if current_state in ["live","crit"]: # in progess
		current_period = game['periodDescriptor']['number']
		current_remain = game['clock']['timeRemaining']
		away_scrore = game['awayTeam']['score']
		home_scrore = game['homeTeam']['score']
		print("## Period: %d   Time Remaining: %s" % (current_period, current_remain))
		print("### %s: %s" % ( away_team, away_scrore ))
		print("### %s: %s" % ( home_team, home_scrore ))
	elif current_state == "postponed":
		print('## Postponed')
	elif current_state in ["final","off"]:
		away_scrore = game['awayTeam']['score']
		home_scrore = game['homeTeam']['score']
		current_period = game['periodDescriptor']['number']
		overtime = ""
		if current_period > 3:
			overtime = game['periodDescriptor']['periodType']
		# if game['linescore']['hasShootout']:
			# overtime = "OT/SO"
		print("### %s: %s" % ( away_team, away_scrore ))
		print("### %s: %s" % ( home_team, home_scrore ))
		print("### Final %s" % overtime)
	elif current_state in [ 'fut', 'pre' ]: # future
		start_time = game['startTimeUTC']
		try:
			t = datetime.strptime(start_time,"%Y-%m-%dT%H:%M:%SZ")
			# t1 = datetime(t.year,t.month,t.day,t.hour,t.minute,t.second,tzinfo=UTC())
			t1 = datetime(t.year,t.month,t.day,t.hour,t.minute,t.second,tzinfo=ZoneInfo("UTC"))
			# start_time = t1.astimezone(LocalTimezone()).strftime("%Y-%m-%d %H:%M")
			start_time = t1.astimezone(ZoneInfo(os.environ["TZ"])).strftime("%Y-%m-%d %H:%M")
		except:
			# just use as is then
			pass
		print("## Starts at %s" % start_time)

def format_mlb_game(game):
	away_team = game['teams']['away']['team']['abbreviation']
	home_team = game['teams']['home']['team']['abbreviation']
	game_type = game['gameType'].lower()
	if game_type == 'r':
		game_type = ""
	elif game_type == 'a':
		game_type = '(all-star)'
	else:
		game_type = '(post-season)'
	game_number = "" if game['doubleHeader'].lower() == "n" else "game #" + str(game['gameNumber'])
	print()
	print("# %s at %s %s %s" % ( away_team, home_team, game_number, game_type ))
	current_state = game['status']['codedGameState']
	if current_state.lower() == "i": # in progress
		current_inning = game['linescore']['currentInning']
		current_inning_state = game['linescore']['inningState']
		away_scrore = game['teams']['away']['score']
		home_scrore = game['teams']['home']['score']
		print("## %s of Inning %s" % (current_inning_state, current_inning))
		print("### %s: %s" % ( away_team, away_scrore ))
		print("### %s: %s" % ( home_team, home_scrore ))
	elif current_state.lower() in ["f","o"]: # final, over
		current_inning = game['linescore']['currentInning']
		scheduled_innings = game['linescore']['scheduledInnings']
		away_scrore = game['teams']['away']['score']
		home_scrore = game['teams']['home']['score']
		if int(current_inning) > int(scheduled_innings):
			print("## Final Score/%s" % current_inning)
		else:
			print("## Final Score")
		print("### %s: %s" % ( away_team, away_scrore ))
		print("### %s: %s" % ( home_team, home_scrore ))
	elif current_state.lower() == 'd': # delayed, postponed
		print('## Postponed: %s' % game['status']['reason'])
	elif current_state.lower() == 'u': # suspended
		print('## %s' % game['status']['reason'])
	elif current_state.lower() in ['s','p']: # scheduled, preview
		start_time = game['gameDate']
		try:
			t = datetime.strptime(start_time[:-6]+'Z',"%Y-%m-%dT%H:%M:%SZ")
			# t1 = datetime(t.year,t.month,t.day,t.hour,t.minute,t.second,tzinfo=UTC())
			t1 = datetime(t.year,t.month,t.day,t.hour,t.minute,t.second,tzinfo=ZoneInfo("UTC"))
			#start_time = t1.astimezone(LocalTimezone()).strftime("%Y-%m-%d %H:%M")
			start_time = t1.strftime("%Y-%m-%d %H:%M")
		except:
			# just use as is then
			pass
		print("## Starts at %s" % start_time)

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
		op = build_opener()
		op.addheaders = [('User-Agent', 'Mozilla/5.0')]
		if sport == 'nhl':
			f = op.open(URL % ( query_date ))
		else:
			f = op.open(URL % ( query_date, query_date ))
	except:
		return error("Failed to fetch", sport)

	data_coded = f.read()
	data_decoded = json.loads(data_coded)
	try:
		if 'dates' in data_decoded and len(data_decoded['dates']):
			game_date = data_decoded['dates'][0]['date']
		elif 'currentDate' in data_decoded:
			game_date = data_decoded['currentDate']
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

	print("# WarpEngineer's %s Scores" % sport.upper())
	print("## Games for %s" % game_date)
	print(day_links)
	print("### All times are Eastern")
	print(update_line)
	print("### Last update: %s" % time.asctime())

	try:
		if 'dates' in data_decoded and len(data_decoded['dates']):
			games = data_decoded['dates'][0]['games']
		elif 'games' in data_decoded:
			games = data_decoded['games']
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
				print()
		print()
		print(VERSION)

	except:
		return error(data_coded, sport)

	return 0

if __name__ == "__main__":
	main()

