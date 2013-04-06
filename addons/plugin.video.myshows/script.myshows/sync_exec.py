# -*- coding: utf-8 -*-

import xbmcaddon
import xbmcgui
import globals
import xbmc
from movie_sync import SyncMovies
from episode_sync import SyncEpisodes

def get_bool(boolean):
	return xbmcaddon.Addon('script.myshows').getSetting(boolean) == 'true'

def do_sync(media_type):
	if media_type == 'movies':
		if get_bool('add_movies_to_myshows') or get_bool('myshows_movie_playcount') or get_bool('xbmc_movie_playcount') or get_bool('clean_myshows_movies'):
			return True
	else:
		if get_bool('add_episodes_to_myshows') or get_bool('myshows_episode_playcount') or get_bool('xbmc_episode_playcount') or get_bool('clean_myshows_episodes'):
			return True

	return False

if __name__ == '__main__':
    xbmc.executebuiltin('XBMC.ActivateWindow(Videos,plugin://plugin.video.myshows/)')
    #if do_sync('movies'):
    #    movies = SyncMovies(show_progress=True, api=globals.myshowsapi)
    #    movies.Run()

	#if do_sync('episodes'):
	#	episodes = SyncEpisodes(show_progress=True, api=globals.myshowsapi)
	#	episodes.Run()
