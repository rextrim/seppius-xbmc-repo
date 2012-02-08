#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2011-2012 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
# Writer (c) 2012, Kostynoy S.A., E-mail: seppius@xbmc.ru


import sys, xbmc, xbmcgui, xbmcplugin, xbmcaddon, re
import os, urllib, urllib2

__addon__ = xbmcaddon.Addon( id = 'plugin.audio.101.ru' )
__language__ = __addon__.getLocalizedString

addon_id      = __addon__.getAddonInfo( 'id' )
addon_path    = __addon__.getAddonInfo( 'path' )
addon_name    = __addon__.getAddonInfo( 'name' )
addon_version = __addon__.getAddonInfo( 'version' )
addon_author  = __addon__.getAddonInfo( 'author' )

icon = xbmc.translatePath( os.path.join( addon_path, 'icon.png' ) )

xbmc.log('[%s] Starting version [%s]' % (addon_id, addon_version), 1)

UA = 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; appLanguage) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543a Safari/419.3'

h = int(sys.argv[1])

try:
	import json
except ImportError:
	try:
		import simplejson as json
		xbmc.log( '[%s]: Error import json. Uses module simplejson' % addon_id, 2 )
	except ImportError:
		try:
			import demjson3 as json
			xbmc.log( '[%s]: Error import simplejson. Uses module demjson3' % addon_id, 3 )
		except ImportError:
			xbmc.log( '[%s]: Error import demjson3. Sorry.' % addon_id, 4 )

def GET(targeturl, referer = None):
	req = urllib2.Request(targeturl)
	req.add_header(     'User-Agent',UA)
	if referer:
		req.add_header(     'Referer',referer)
	req.add_header( 'Accept-Language','ru-RU,ru;q=0.9,en;q=0.8')
	f = urllib2.urlopen(req)
	a = f.read()
	f.close()
	return a.decode('cp1251').encode('utf8')

def getitems(params):
	http = GET('http://m.101.ru/', 'http://101.ru/')
	if http != None:
		rr = re.compile('<td><a href=\"(.*?)\" class=\"mgroupstation mgchan\"><span>(.*?)</span></a></td>').findall(http)
		if len(rr):
			for href, name in rr:
				href = href.replace('&amp;', '&')
				i = xbmcgui.ListItem(name, iconImage = icon, thumbnailImage = icon)
				uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'getgroup', 'href':href}))
				xbmcplugin.addDirectoryItem(h, uri, i, True)
		xbmcplugin.endOfDirectory(h)

def getgroup(params):
	http = GET(params['href'], 'http://m.101.ru/')
	if http != None:
		rr = re.compile('<td><a href=\"(.*?)\" class=\"linkstream\"><span><img src=\"(.*?)\" width=\"14\" height=\"14\">(.*?)</span></a></td>').findall(http)
		if len(rr):
			for href, img, name in rr:
				href = href.replace('&amp;', '&')
				i = xbmcgui.ListItem(name, iconImage = icon, thumbnailImage = icon)
				uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'play', 'href':href, 'referer':params['href']}))
				xbmcplugin.addDirectoryItem(h, uri, i) # , False
		xbmcplugin.endOfDirectory(h)

def play(params):
	uu = '%s|%s' % (params['href'], urllib.urlencode({'User-Agent':UA, 'Referer':params['referer']}))
	#uu = params['href']
	#i = xbmcgui.ListItem()
	#i.setInfo(type='music', infoLabels = {'title': ''})
	#xbmcplugin.setResolvedUrl(h, True, i)
	#xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(uu, i)
	
	playList = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
	playList.clear()
	playList.add(uu)
	xbmc.Player().play(playList)

	
	
def get_params(paramstring):
	param=[]
	if len(paramstring)>=2:
		params=paramstring
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	if len(param) > 0:
		for cur in param:
			param[cur] = urllib.unquote_plus(param[cur])
	return param

def addon_main():
	params = get_params(sys.argv[2])
	try:
		func = params['func']
	except:
		func = None
		xbmc.log( '[%s]: Primary input' % addon_id, 1 )
		getitems(params)

	if func != None:
		try: pfunc = globals()[func]
		except:
			pfunc = None
			xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
			showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
		if pfunc: pfunc(params)
