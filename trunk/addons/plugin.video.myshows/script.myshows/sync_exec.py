# -*- coding: utf-8 -*-

import xbmcaddon
import xbmcgui
import xbmc
import urllib, sys, json

def get_bool(boolean):
    return xbmcaddon.Addon('script.myshows').getSetting(boolean) == 'true'

def get_apps(paramstring=None):
    if not paramstring: paramstring=sys.argv[1].replace('|:|',',')
    print 'paramstring '+str(paramstring)
    if len(paramstring)>=2:
        apps=json.loads(urllib.unquote_plus(paramstring))
        return apps

try:apps=get_apps()
except:apps=None

if apps:
    from rating import rateMedia
    if 'kinopoiskId' in apps:
        media={'kinopoiskId':urllib.unquote_plus(apps['kinopoiskId']),
               'title':urllib.unquote_plus(apps['title']),'year':urllib.unquote_plus(apps['year'])}
        rateMedia('movie',media)
    elif 'title' in apps and 'year' in apps:
        media={'title':urllib.unquote_plus(apps['title']),'year':urllib.unquote_plus(apps['year'])}
        rateMedia('movie',media)

elif __name__ == '__main__':
    xbmc.executebuiltin('XBMC.ActivateWindow(Videos,plugin://plugin.video.myshows/)')
