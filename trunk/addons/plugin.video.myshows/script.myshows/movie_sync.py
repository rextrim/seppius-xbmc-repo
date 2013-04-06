# -*- coding: utf-8 -*-

import xbmc
import xbmcgui
import xbmcaddon
from utilities import xbmcJsonRequest, Debug, notification, chunks, get_bool_setting

__setting__   = xbmcaddon.Addon('script.myshows').getSetting
__getstring__ = xbmcaddon.Addon('script.myshows').getLocalizedString

add_movies_to_myshows = get_bool_setting('add_movies_to_myshows')
myshows_movie_playcount = get_bool_setting('myshows_movie_playcount')
xbmc_movie_playcount = get_bool_setting('xbmc_movie_playcount')
clean_myshows_movies = get_bool_setting('clean_myshows_movies')

progress = xbmcgui.DialogProgress()

def xbmc_to_myshows_movie(movie, playcount=False):
	""" Helper to convert XBMC movie into a format myshows can use. """

	myshows_movie = {'title': movie['title'], 'year': movie['year']}

	if movie['imdbnumber'].startswith('tt'): #IMDB
		myshows_movie['imdb_id'] = movie['imdbnumber']

	elif movie['imdbnumber'].isdigit(): #TVDB
		myshows_movie['tmdb_id'] = movie['imdbnumber']

	if playcount:
		myshows_movie['plays'] = movie['playcount']

	return myshows_movie

class SyncMovies():
	def __init__(self, show_progress=False, api=None):
		self.myshowsapi = api
		if self.myshowsapi == None:
			from myshowsapi import myshowsAPI
			self.myshowsapi = myshowsAPI()

		self.xbmc_movies = None
		self.myshows_movies_seen = None
		self.myshows_movies_collection = None
		self.show_progress = show_progress
		self.notify = __setting__('show_sync_notifications') == 'true'

		if self.show_progress:
			progress.create('%s %s' % (__getstring__(1400), __getstring__(1402)), line1=' ', line2=' ', line3=' ')

	def Canceled(self):
		if self.show_progress and progress.iscanceled():
			Debug('[Movies Sync] Sync was canceled by user')
			return True
		elif xbmc.abortRequested:
			Debug('XBMC abort requested')
			return True
		else:
			return False

	def GetFromXBMC(self):
		Debug('[Movies Sync] Getting movies from XBMC')
		if self.show_progress:
			progress.update(5, line1=__getstring__(1422), line2=' ', line3=' ')

		result = xbmcJsonRequest({'jsonrpc': '2.0', 'id': 0, 'method': 'VideoLibrary.GetMovies', 'params': {'properties': ['title', 'imdbnumber', 'year', 'playcount']}})

		# sanity check, test for empty result
		if not result:
			Debug("[Movies Sync] xbmc json request was empty.")
			return

		if 'movies' in result:
			self.xbmc_movies = result['movies']
			Debug("[Movies Sync] XBMC JSON Result: '%s'" % str(self.xbmc_movies))
		else:
			Debug('[Movies Sync] Key "movies" not found')

	def GetFrommyshowsCollection(self):
		Debug('[Movies Sync] Getting movie collection from myshows.tv')
		if self.show_progress:
			progress.update(10, line1=__getstring__(1423), line2=' ', line3=' ')
		self.myshows_movies_collection = self.myshowsapi.getMovieLibrary()

	def GetFrommyshowsSeen(self):
		Debug('[Movies Sync] Getting seen movies from myshows.tv')
		if self.show_progress:
			progress.update(15, line1=__getstring__(1424), line2=' ', line3=' ')
		self.myshows_movies_seen = self.myshowsapi.getWatchedMovieLibrary()

	def AddTomyshows(self):
		Debug('[Movies Sync] Checking for XBMC movies that are not on myshows.tv')
		if self.show_progress:
			progress.update(30, line1=__getstring__(1425), line2=' ', line3=' ')

		add_to_myshows = []
		myshows_imdb_ids = [x['imdb_id'] for x in self.myshows_movies_collection if 'imdb_id' in x]
		myshows_tmdb_ids = [x['tmdb_id'] for x in self.myshows_movies_collection if 'tmdb_id' in x]
		myshows_titles = [x['title'] for x in self.myshows_movies_collection if 'title' in x]

		for xbmc_movie in self.xbmc_movies:
			#Compare IMDB IDs
			if xbmc_movie['imdbnumber'].startswith('tt'):
				if xbmc_movie['imdbnumber'] not in myshows_imdb_ids:
					Debug('[Movies Sync][AddTomyshows] %s' % xbmc_movie)
					add_to_myshows.append(xbmc_movie)

			#Compare TMDB IDs
			elif xbmc_movie['imdbnumber'].isdigit():
				if xbmc_movie['imdbnumber'] not in myshows_tmdb_ids:
					Debug('[Movies Sync][AddTomyshows] %s' % xbmc_movie)
					add_to_myshows.append(xbmc_movie)

			#Compare titles if unknown ID type
			else:
				if xbmc_movie['title'] not in myshows_titles:
					Debug('[Movies Sync][AddTomyshows] %s' % xbmc_movie)
					add_to_myshows.append(xbmc_movie)

		if add_to_myshows:
			Debug('[Movies Sync] %i movie(s) will be added to myshows.tv collection' % len(add_to_myshows))
			if self.Canceled():
				return

			if self.show_progress:
				progress.update(45, line2='%i %s' % (len(add_to_myshows), __getstring__(1426)))

			params = {'movies': [xbmc_to_myshows_movie(x) for x in add_to_myshows]}
			self.myshowsapi.addMovie(params)
						
		else:
			Debug('[Movies Sync] myshows.tv movie collection is up to date')


	def UpdatePlaysmyshows(self):
		Debug('[Movies Sync] Checking if myshows.tv playcount is up to date')
		if self.show_progress:
			progress.update(60, line1=__getstring__(1427), line2=' ', line3=' ')

		update_playcount = []
		myshows_playcounts = {}
		xbmc_movies_seen = [x for x in self.xbmc_movies if x['playcount']]

		for myshows_movie in self.myshows_movies_seen:
			if 'tmdb_id' in myshows_movie:
				myshows_playcounts[myshows_movie['tmdb_id']] = myshows_movie['plays']

			if 'imdb_id' in myshows_movie:
				myshows_playcounts[myshows_movie['imdb_id']] = myshows_movie['plays']

			myshows_playcounts[myshows_movie['title']] = myshows_movie['plays']

		for xbmc_movie in xbmc_movies_seen:
			if xbmc_movie['imdbnumber'] in myshows_playcounts:
				if myshows_playcounts[xbmc_movie['imdbnumber']] < xbmc_movie['playcount']:
					Debug('[Movies Sync][UpdatePlaysmyshows] %s' % xbmc_movie)
					update_playcount.append(xbmc_movie)
				else:
					pass

			elif xbmc_movie['title'] in myshows_playcounts:
				if myshows_playcounts[xbmc_movie['title']] < xbmc_movie['playcount']:
					Debug('[Movies Sync][UpdatePlaysmyshows][Update] %s' % xbmc_movie)
					update_playcount.append(xbmc_movie)
				else:
					pass

			else:
				Debug('[Movies Sync][UpdatePlaysmyshows][Update] %s' % xbmc_movie)
				update_playcount.append(xbmc_movie)

		if update_playcount:
			Debug('[Movies Sync] %i movie(s) playcount will be updated on myshows.tv' % len(update_playcount))
			if self.Canceled():
				return

			if self.show_progress:
				progress.update(75, line2='%i %s' % (len(update_playcount), __getstring__(1428)))

			# Send request to update playcounts on myshows.tv
			params = {'movies': [xbmc_to_myshows_movie(x, playcount=True) for x in update_playcount]}
			self.myshowsapi.updateSeenMovie(params)

		else:
			Debug('[Movies Sync] myshows.tv movie playcount is up to date')


	def UpdatePlaysXBMC(self):
		Debug('[Movies Sync] Checking if XBMC playcount is up to date')
		if self.show_progress:
			progress.update(85, line1=__getstring__(1429), line2=' ', line3=' ')

		update_playcount = []
		myshows_playcounts = {}

		for myshows_movie in self.myshows_movies_seen:
			if 'tmdb_id' in myshows_movie:
				myshows_playcounts[myshows_movie['tmdb_id']] = myshows_movie['plays']

			if 'imdb_id' in myshows_movie:
				myshows_playcounts[myshows_movie['imdb_id']] = myshows_movie['plays']

			myshows_playcounts[myshows_movie['title']] = myshows_movie['plays']

		for xbmc_movie in self.xbmc_movies:
			if xbmc_movie['imdbnumber'] in myshows_playcounts:
				if myshows_playcounts[xbmc_movie['imdbnumber']] > xbmc_movie['playcount']:
					xbmc_movie['playcount'] = myshows_playcounts[xbmc_movie['imdbnumber']]
					update_playcount.append(xbmc_movie)

			elif xbmc_movie['title'] in myshows_playcounts:
				if myshows_playcounts[xbmc_movie['title']] > xbmc_movie['playcount']:
					xbmc_movie['playcount'] = myshows_playcounts[xbmc_movie['title']]
					update_playcount.append(xbmc_movie)


		if update_playcount:
			Debug('[Movies Sync] %i movie(s) playcount will be updated on XBMC' % len(update_playcount))
			if self.show_progress:
				progress.update(90, line2='%i %s' % (len(update_playcount), __getstring__(1430)))

			#split movie list into chunks of 50
			chunked_movies = chunks([{"jsonrpc": "2.0", "method": "VideoLibrary.SetMovieDetails", "params": {"movieid": update_playcount[i]['movieid'], "playcount": update_playcount[i]['playcount']}, "id": i} for i in range(len(update_playcount))], 50)
			for chunk in chunked_movies:
				if self.Canceled():
					return
				xbmcJsonRequest(chunk)

		else:
			Debug('[Movies Sync] XBMC movie playcount is up to date')

	def RemoveFrommyshows(self):
		Debug('[Movies Sync] Cleaning myshows movie collection')
		if self.show_progress:
			progress.update(95, line1=__getstring__(1443), line2=' ', line3=' ')

		remove_from_myshows = []
		xbmc_imdb_ids = [x['imdbnumber'] for x in self.xbmc_movies if x['imdbnumber'].startswith('tt')]
		xbmc_tmdb_ids = [x['imdbnumber'] for x in self.xbmc_movies if x['imdbnumber'].isdigit()]
		xbmc_titles = [x['title'] for x in self.xbmc_movies]


		for myshows_movie in self.myshows_movies_collection:
			remove = True
			if 'imdb_id' in myshows_movie and myshows_movie['imdb_id'] in xbmc_imdb_ids:
				remove = False
			if 'tmdb_id' in myshows_movie and myshows_movie['tmdb_id'] in xbmc_tmdb_ids:
				remove = False
			if myshows_movie['title'] in xbmc_titles:
				remove = False

			if remove:
				Debug('[Movies Sync] %s (%i) will be removed from myshows collection' % (myshows_movie['title'].encode('utf-8'), myshows_movie['year']))
				remove_from_myshows.append(myshows_movie)

		if remove_from_myshows:
			Debug('[Movies Sync] %i movie(s) will be removed from myshows.tv collection' % len(remove_from_myshows))

			if self.Canceled():
				return

			if self.show_progress:
				progress.update(95, line2='%i %s' % (len(remove_from_myshows), __getstring__(1444)))
			
			params = {'movies': remove_from_myshows}
			self.myshowsapi.removeMovie(params)

		else:
			Debug('[Movies Sync] myshows.tv movie collection is clean')

	def Run(self):
		if not self.show_progress and __setting__('sync_on_update') == 'true' and self.notify:
			notification('%s %s' % (__getstring__(1400), __getstring__(1402)), __getstring__(1420)) #Sync started

		self.GetFromXBMC()

		# sanity check, test for non-empty xbmc movie list
		if self.xbmc_movies:

			if not self.Canceled() and add_movies_to_myshows:
				self.GetFrommyshowsCollection()
				self.AddTomyshows()

			if myshows_movie_playcount or xbmc_movie_playcount:
				if not self.Canceled():
					self.GetFrommyshowsSeen()

			if not self.Canceled() and myshows_movie_playcount:
				self.UpdatePlaysmyshows()

			if not self.Canceled() and xbmc_movie_playcount:
				self.UpdatePlaysXBMC()

			if not self.Canceled() and clean_myshows_movies:
				if not add_movies_to_myshows:
					self.GetFrommyshowsCollection()
				if not self.Canceled():
					self.RemoveFrommyshows()

		else:
			Debug("[Movies Sync] XBMC Movie list is empty, aborting Movies Sync.")

		if not self.Canceled() and self.show_progress:
			progress.update(100, line1=__getstring__(1431), line2=' ', line3=' ')
			progress.close()

		if not self.show_progress and __setting__('sync_on_update') == 'true' and self.notify:
			notification('%s %s' % (__getstring__(1400), __getstring__(1402)), __getstring__(1421)) #Sync complete

		Debug('[Movies Sync] Complete')
