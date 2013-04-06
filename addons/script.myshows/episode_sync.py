# -*- coding: utf-8 -*-

import xbmc
import xbmcgui
import xbmcaddon
from utilities import xbmcJsonRequest, Debug, notification, chunks, get_bool_setting

__setting__   = xbmcaddon.Addon('script.myshows').getSetting
__getstring__ = xbmcaddon.Addon('script.myshows').getLocalizedString

add_episodes_to_myshows = get_bool_setting('add_episodes_to_myshows')
myshows_episode_playcount = get_bool_setting('myshows_episode_playcount')
xbmc_episode_playcount = get_bool_setting('xbmc_episode_playcount')
clean_myshows_episodes = get_bool_setting('clean_myshows_episodes')

progress = xbmcgui.DialogProgress()

def compare_show(xbmc_show, myshows_show):
	missing = []
	myshows_seasons = [x['season'] for x in myshows_show['seasons']]

	for xbmc_episode in xbmc_show['episodes']:
		if xbmc_episode['season'] not in myshows_seasons:
			missing.append(xbmc_episode)
		else:
			for myshows_season in myshows_show['seasons']:
				if xbmc_episode['season'] == myshows_season['season']:
					if xbmc_episode['episode'] not in myshows_season['episodes']:
						missing.append(xbmc_episode)

	return missing

def compare_show_watched_myshows(xbmc_show, myshows_show):
	missing = []

	for xbmc_episode in xbmc_show['episodes']:
		if xbmc_episode['playcount']:
			if xbmc_episode['season'] not in [x['season'] for x in myshows_show['seasons']]:
				missing.append(xbmc_episode)
			else:
				for myshows_season in myshows_show['seasons']:
					if xbmc_episode['season'] == myshows_season['season']:
						if xbmc_episode['episode'] not in myshows_season['episodes']:
							missing.append(xbmc_episode)

	return missing

def compare_show_watched_xbmc(xbmc_show, myshows_show):
	missing = []

	for xbmc_episode in xbmc_show['episodes']:
		if not xbmc_episode['playcount']:
			for myshows_season in myshows_show['seasons']:
				if xbmc_episode['season'] == myshows_season['season']:
					if xbmc_episode['episode'] in myshows_season['episodes']:
						missing.append(xbmc_episode)

	return missing

class SyncEpisodes():
	def __init__(self, show_progress=False, api=None):
		self.myshowsapi = api
		if self.myshowsapi == None:
			from myshowsapi import myshowsAPI
			self.myshowsapi = myshowsAPI()
			
		self.xbmc_shows = []
		self.myshows_shows = {'collection': [], 'watched': []}
		self.notify = __setting__('show_sync_notifications') == 'true'
		self.show_progress = show_progress

		if self.show_progress:
			progress.create('%s %s' % (__getstring__(1400), __getstring__(1406)), line1=' ', line2=' ', line3=' ')

	def Canceled(self):
		if self.show_progress and progress.iscanceled():
			Debug('[Episodes Sync] Sync was canceled by user')
			return True
		elif xbmc.abortRequested:
			Debug('XBMC abort requested')
			return True
		else:
			return False

	def GetFromXBMC(self):
		Debug('[Episodes Sync] Getting episodes from XBMC')
		if self.show_progress:
			progress.update(5, line1=__getstring__(1432), line2=' ', line3=' ')

		shows = xbmcJsonRequest({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetTVShows', 'params': {'properties': ['title', 'imdbnumber']}, 'id': 0})

		# sanity check, test for empty result
		if not shows:
			Debug("[Episodes Sync] xbmc json request was empty.")
			return

		# test to see if tvshows key exists in xbmc json request
		if 'tvshows' in shows:
			shows = shows['tvshows']
			Debug("[Episodes Sync] XBMC JSON Result: '%s'" % str(shows))
		else:
			Debug("[Episodes Sync] Key 'tvshows' not found")
			return

		if self.show_progress:
			progress.update(10, line1=__getstring__(1433), line2=' ', line3=' ')

		for show in shows:
			if self.Canceled():
				return
			show['episodes'] = []

			episodes = xbmcJsonRequest({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetEpisodes', 'params': {'tvshowid': show['tvshowid'], 'properties': ['season', 'episode', 'playcount', 'uniqueid']}, 'id': 0})
			if 'episodes' in episodes:
				episodes = episodes['episodes']

				show['episodes'] = [x for x in episodes if type(x) == type(dict())]

		self.xbmc_shows = [x for x in shows if x['episodes']]

	def GetCollectionFrommyshows(self):
		Debug('[Episodes Sync] Getting episode collection from myshows.tv')
		if self.show_progress:
			progress.update(15, line1=__getstring__(1434), line2=' ', line3=' ')

		self.myshows_shows['collection'] = self.myshowsapi.getShowLibrary()

	def AddTomyshows(self):
		Debug('[Episodes Sync] Checking for episodes missing from myshows.tv collection')
		if self.show_progress:
			progress.update(30, line1=__getstring__(1435), line2=' ', line3=' ')

		add_to_myshows = []
		myshows_imdb_index = {}
		myshows_tvdb_index = {}
		myshows_title_index = {}

		for i in range(len(self.myshows_shows['collection'])):
			if 'imdb_id' in self.myshows_shows['collection'][i]:
				myshows_imdb_index[self.myshows_shows['collection'][i]['imdb_id']] = i

			if 'tvdb_id' in self.myshows_shows['collection'][i]:
				myshows_tvdb_index[self.myshows_shows['collection'][i]['tvdb_id']] = i

			myshows_title_index[self.myshows_shows['collection'][i]['title']] = i

		for xbmc_show in self.xbmc_shows:
			missing = []

			#IMDB ID
			if xbmc_show['imdbnumber'].startswith('tt'):
				if xbmc_show['imdbnumber'] not in myshows_imdb_index.keys():
					missing = xbmc_show['episodes']

				else:
					myshows_show = self.myshows_shows['collection'][myshows_imdb_index[xbmc_show['imdbnumber']]]
					missing = compare_show(xbmc_show, myshows_show)

			#TVDB ID
			elif xbmc_show['imdbnumber'].isdigit():
				if xbmc_show['imdbnumber'] not in myshows_tvdb_index.keys():
					missing = xbmc_show['episodes']

				else:
					myshows_show = self.myshows_shows['collection'][myshows_tvdb_index[xbmc_show['imdbnumber']]]
					missing = compare_show(xbmc_show, myshows_show)

			#Title
			else:
				if xbmc_show['title'] not in myshows_title_index.keys():
					missing = xbmc_show['episodes']

				else:
					myshows_show = self.myshows_shows['collection'][myshows_title_index[xbmc_show['title']]]
					missing = compare_show(xbmc_show, myshows_show)

			if missing:
				show = {'title': xbmc_show['title'], 'episodes': [{'episode': x['episode'], 'season': x['season'], 'episode_tvdb_id': x['uniqueid']['unknown']} for x in missing]}
				Debug('[Episodes Sync][AddTomyshows] %s' % show)

				if xbmc_show['imdbnumber'].isdigit():
					show['tvdb_id'] = xbmc_show['imdbnumber']
				else:
					show['imdb_id'] = xbmc_show['imdbnumber']

				add_to_myshows.append(show)

		if add_to_myshows:
			Debug('[Episodes Sync] %i shows(s) have episodes added to myshows.tv collection' % len(add_to_myshows))
			if self.show_progress:
				progress.update(35, line1=__getstring__(1435), line2='%i %s' % (len(add_to_myshows), __getstring__(1436)))

			for show in add_to_myshows:
				if self.Canceled():
					return
				if self.show_progress:
					progress.update(45, line1=__getstring__(1435), line2=show['title'].encode('utf-8', 'ignore'), line3='%i %s' % (len(show['episodes']), __getstring__(1437)))

				self.myshowsapi.addEpisode(show)

		else:
			Debug('[Episodes Sync] myshows.tv episode collection is up to date')

	def GetWatchedFrommyshows(self):
		Debug('[Episodes Sync] Getting watched episodes from myshows.tv')
		if self.show_progress:
			progress.update(50, line1=__getstring__(1438), line2=' ', line3=' ')

		self.myshows_shows['watched'] = self.myshowsapi.getWatchedEpisodeLibrary()

	def UpdatePlaysmyshows(self):
		Debug('[Episodes Sync] Checking watched episodes on myshows.tv')
		if self.show_progress:
			progress.update(60, line1=__getstring__(1438), line2=' ', line3=' ')

		update_playcount = []
		myshows_imdb_index = {}
		myshows_tvdb_index = {}
		myshows_title_index = {}

		for i in range(len(self.myshows_shows['watched'])):
			if 'imdb_id' in self.myshows_shows['watched'][i]:
				myshows_imdb_index[self.myshows_shows['watched'][i]['imdb_id']] = i

			if 'tvdb_id' in self.myshows_shows['watched'][i]:
				myshows_tvdb_index[self.myshows_shows['watched'][i]['tvdb_id']] = i

			myshows_title_index[self.myshows_shows['watched'][i]['title']] = i

		xbmc_shows_watched = []
		for show in self.xbmc_shows:
			watched_episodes = [x for x in show['episodes'] if x['playcount']]
			if watched_episodes:
				xbmc_shows_watched.append(show)

		for xbmc_show in xbmc_shows_watched:
			missing = []
			myshows_show = {}

			#IMDB ID
			if xbmc_show['imdbnumber'].startswith('tt') and xbmc_show['imdbnumber'] in myshows_imdb_index.keys():
				myshows_show = self.myshows_shows['watched'][myshows_imdb_index[xbmc_show['imdbnumber']]]

			#TVDB ID
			elif xbmc_show['imdbnumber'].isdigit() and xbmc_show['imdbnumber'] in myshows_tvdb_index.keys():
				myshows_show = self.myshows_shows['watched'][myshows_tvdb_index[xbmc_show['imdbnumber']]]

			#Title
			else:
				if xbmc_show['title'] in myshows_title_index.keys():
					myshows_show = self.myshows_shows['watched'][myshows_title_index[xbmc_show['title']]]

			if myshows_show:
				missing = compare_show_watched_myshows(xbmc_show, myshows_show)
			else:
				missing = [x for x in xbmc_show['episodes'] if x['playcount']]

			if missing:
				show = {'title': xbmc_show['title'], 'episodes': [{'episode': x['episode'], 'season': x['season'], 'episode_tvdb_id': x['uniqueid']['unknown']} for x in missing]}
				Debug('[Episodes Sync][UpdatePlaysmyshows] %s' % show)

				if xbmc_show['imdbnumber'].isdigit():
					show['tvdb_id'] = xbmc_show['imdbnumber']
				else:
					show['imdb_id'] = xbmc_show['imdbnumber']

				update_playcount.append(show)

		if update_playcount:
			Debug('[Episodes Sync] %i shows(s) shows are missing playcounts on myshows.tv' % len(update_playcount))
			if self.show_progress:
				progress.update(65, line1=__getstring__(1438), line2='%i %s' % (len(update_playcount), __getstring__(1439)))

			for show in update_playcount:
				if self.Canceled():
					return
				if self.show_progress:
					progress.update(70, line1=__getstring__(1438), line2=show['title'].encode('utf-8', 'ignore'), line3='%i %s' % (len(show['episodes']), __getstring__(1440)))

				self.myshowsapi.updateSeenEpisode(show)

		else:
			Debug('[Episodes Sync] myshows.tv episode playcounts are up to date')

	def UpdatePlaysXBMC(self):
		Debug('[Episodes Sync] Checking watched episodes on XBMC')
		if self.show_progress:
			progress.update(80, line1=__getstring__(1441), line2=' ', line3=' ')

		update_playcount = []
		myshows_imdb_index = {}
		myshows_tvdb_index = {}
		myshows_title_index = {}

		for i in range(len(self.myshows_shows['watched'])):
			if 'imdb_id' in self.myshows_shows['watched'][i]:
				myshows_imdb_index[self.myshows_shows['watched'][i]['imdb_id']] = i

			if 'tvdb_id' in self.myshows_shows['watched'][i]:
				myshows_tvdb_index[self.myshows_shows['watched'][i]['tvdb_id']] = i

			myshows_title_index[self.myshows_shows['watched'][i]['title']] = i

		for xbmc_show in self.xbmc_shows:
			missing = []
			myshows_show = None

			#IMDB ID
			if xbmc_show['imdbnumber'].startswith('tt') and xbmc_show['imdbnumber'] in myshows_imdb_index.keys():
				myshows_show = self.myshows_shows['watched'][myshows_imdb_index[xbmc_show['imdbnumber']]]

			#TVDB ID
			elif xbmc_show['imdbnumber'].isdigit() and xbmc_show['imdbnumber'] in myshows_tvdb_index.keys():
				myshows_show = self.myshows_shows['watched'][myshows_tvdb_index[xbmc_show['imdbnumber']]]

			#Title
			else:
				if xbmc_show['title'] in myshows_title_index.keys():
					myshows_show = self.myshows_shows['watched'][myshows_title_index[xbmc_show['title']]]

			if myshows_show:
				missing = compare_show_watched_xbmc(xbmc_show, myshows_show)
			else:
				Debug('[Episodes Sync] Failed to find %s on myshows.tv' % xbmc_show['title'])


			if missing:
				show = {'title': xbmc_show['title'], 'episodes': [{'episodeid': x['episodeid'], 'playcount': 1} for x in missing]}
				update_playcount.append(show)

		if update_playcount:
			Debug('[Episodes Sync] %i shows(s) shows are missing playcounts on XBMC' % len(update_playcount))
			if self.show_progress:
				progress.update(85, line1=__getstring__(1441), line2='%i %s' % (len(update_playcount), __getstring__(1439)))

			for show in update_playcount:
				if self.show_progress:
					progress.update(85, line1=__getstring__(1441), line2=show['title'].encode('utf-8', 'ignore'), line3='%i %s' % (len(show['episodes']), __getstring__(1440)))

				#split episode list into chunks of 50
				chunked_episodes = chunks([{"jsonrpc": "2.0", "method": "VideoLibrary.SetEpisodeDetails", "params": show['episodes'][i], "id": i} for i in range(len(show['episodes']))], 50)
				for chunk in chunked_episodes:
					if self.Canceled():
						return
					xbmcJsonRequest(chunk)

		else:
			Debug('[Episodes Sync] XBMC episode playcounts are up to date')

	def RemoveFrommyshows(self):
		Debug('[Movies Sync] Cleaning myshows tvshow collection')
		if self.show_progress:
			progress.update(90, line1=__getstring__(1445), line2=' ', line3=' ')

		def convert_seasons(show):
			episodes = []
			if 'seasons' in show and show['seasons']:
				for season in show['seasons']:
					for episode in season['episodes']:
						episodes.append({'season': season['season'], 'episode': episode})
			return episodes

		remove_from_myshows = []
		indices = {'imdb_id': {}, 'tvdb_id': {}, 'title': {}}

		for i in range(len(self.xbmc_shows)):
			if self.xbmc_shows[i]['imdbnumber'].startswith('tt'):
				indices['imdb_id'][self.xbmc_shows[i]['imdbnumber']] = i

			if self.xbmc_shows[i]['imdbnumber'].isdigit():
				indices['tvdb_id'][self.xbmc_shows[i]['imdbnumber']] = i

			indices['title'][self.xbmc_shows[i]['title']] = i

		for myshows_show in self.myshows_shows['collection']:
			matched = False
			remove = []

			if 'tvdb_id' in myshows_show:
				if myshows_show['tvdb_id'] in indices['tvdb_id']:
					matched = 'tvdb_id'

			if not matched and 'imdb_id' in myshows_show:
				if myshows_show['imdb_id'] in indices['imdb_id']:
					matched = 'imdb_id'

			if not matched:
				if myshows_show['title'] in indices['title']:
					matched = 'title'

			if matched:
				xbmc_show = self.xbmc_shows[indices[matched][myshows_show[matched]]]
				myshows_episodes = convert_seasons(myshows_show)
				xbmc_episodes = [{'season': x['season'], 'episode': x['episode']} for x in xbmc_show['episodes']]

				for episode in myshows_episodes:
					if episode not in xbmc_episodes:
						remove.append(episode)

			else:
				remove = convert_seasons(myshows_show)

			if remove:
				show = {'title': myshows_show['title'], 'year': myshows_show['year'], 'episodes': remove}
				if matched:
					show[matched] = myshows_show[matched]
				remove_from_myshows.append(show)

		if remove_from_myshows:
			Debug('[Episodes Sync] %ishow(s) will have episodes removed from myshows.tv collection' % len(remove_from_myshows))
			if self.show_progress:
				progress.update(90, line1=__getstring__(1445), line2='%i %s' % (len(remove_from_myshows), __getstring__(1446)))

			for show in remove_from_myshows:
				if self.Canceled():
					return

				if self.show_progress:
					progress.update(95, line1=__getstring__(1445), line2=show['title'].encode('utf-8', 'ignore'), line3='%i %s' % (len(show['episodes']), __getstring__(1447)))

				self.myshowsapi.removeEpisode(show)

		else:
			Debug('[Episodes Sync] myshows.tv episode collection is clean')

	def Run(self):
		if not self.show_progress and __setting__('sync_on_update') == 'true' and self.notify:
			notification('%s %s' % (__getstring__(1400), __getstring__(1406)), __getstring__(1420)) #Sync started

		self.GetFromXBMC()

		# sanity check, test for non-empty xbmc movie list
		if self.xbmc_shows:

			if not self.Canceled() and add_episodes_to_myshows:
				self.GetCollectionFrommyshows()
				if not self.Canceled():
					self.AddTomyshows()

			if myshows_episode_playcount or xbmc_episode_playcount:
				if not self.Canceled():
					self.GetWatchedFrommyshows()

			if not self.Canceled() and myshows_episode_playcount:
				self.UpdatePlaysmyshows()

			if xbmc_episode_playcount:
				if not self.Canceled():
					self.UpdatePlaysXBMC()

			if clean_myshows_episodes:
				if not self.Canceled() and not add_episodes_to_myshows:
					self.GetCollectionFrommyshows()
				if not self.Canceled():
					self.RemoveFrommyshows()

		else:
			Debug("[Episodes Sync] XBMC Show list is empty, aborting Episodes Sync.")

		if not self.show_progress and __setting__('sync_on_update') == 'true' and self.notify:
			notification('%s %s' % (__getstring__(1400), __getstring__(1406)), __getstring__(1421)) #Sync complete

		if not self.Canceled() and self.show_progress:
			progress.update(100, line1=__getstring__(1442), line2=' ', line3=' ')
			progress.close()

		Debug('[Episodes Sync] Complete')