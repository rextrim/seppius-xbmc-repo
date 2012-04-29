#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# 	Copyright (c) 2011 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
# 	Writer (c) 2011, Kostynoy S.A., E-mail: seppius2@gmail.com
# 	Writer (c) 2012, Nevenkin A.V., E-mail: nuimons@gmail.com
#   This Program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2, or (at your option)
#   any later version.
#
#   This Program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; see the file COPYING.  If not, write to
#   the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#   http://www.gnu.org/licenses/gpl.html

import httplib
import urllib
import urllib2

import re

import sys
import os

import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon
import time
import random
from urllib import unquote, quote
import json

__addon__ = xbmcaddon.Addon( id = 'plugin.video.twitch.tv' )
__language__ = __addon__.getLocalizedString
addon_icon    = __addon__.getAddonInfo('icon')
addon_fanart  = __addon__.getAddonInfo('fanart')
addon_path    = __addon__.getAddonInfo('path')
addon_type    = __addon__.getAddonInfo('type')
addon_id      = __addon__.getAddonInfo('id')
addon_author  = __addon__.getAddonInfo('author')
addon_name    = __addon__.getAddonInfo('name')
addon_version = __addon__.getAddonInfo('version')
hos = int(sys.argv[1])

UA = '%s/%s %s/%s/%s' % (addon_type, addon_id, urllib.quote_plus(addon_author), addon_version, urllib.quote_plus(addon_name))



def showMessage(heading, message, times = 3000, pics = addon_icon):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
	except Exception, e:
		xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )

def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))
	
def GET(target, post=None):
	#print target
	try:
		req = urllib2.Request(url = target, data = post, headers = {'User-Agent':UA})
		resp = urllib2.urlopen(req)
		CE = resp.headers.get('content-encoding')
		http = resp.read()
		resp.close()
		return http
	except Exception, e:
		xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
		showMessage('HTTP ERROR', e, 5000)


def main_menu(params):
	http = GET('http://api.justin.tv/api/stream/list.json?category=gaming&language=ru,en')
	json1=json.loads(http)
	games=[]
	for entries in json1:
		try: 
			if entries['meta_game'] not in games:
				li = xbmcgui.ListItem((entries['meta_game']), addon_fanart, addon_icon)
				li.setProperty('IsPlayable', 'false')
				uri = construct_request({
					'game': entries['meta_game'],
					'func': 'get_stream_list'
				})
				xbmcplugin.addDirectoryItem(hos, uri, li, True)
				games.append(entries['meta_game'])
		except: pass
	xbmcplugin.addSortMethod(hos,xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(hos)
	print games
	
	
	
def get_stream_list(params):
	http = GET('http://api.justin.tv/api/stream/list.json?category=gaming&language=ru,en')
	json1=json.loads(http)
	for entries in json1:
		try:
			print entries['title']
			if entries['meta_game']==params['game']:
				li = xbmcgui.ListItem((entries['title']), addon_fanart, addon_icon)
				li.setProperty('IsPlayable', 'true')
				uri = construct_request({
					'name': entries['name'],
					'func': 'get_stream'
				})
				xbmcplugin.addDirectoryItem(hos, uri, li, True)
			
		except: pass
	xbmcplugin.endOfDirectory(hos)
	
def get_stream(params):	
	playLive(params['name'],True)
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
def playLive(name, play=False):
		name=name.replace('live_user_','')
		headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
			'Referer' : 'http://www.justin.tv/'+name}
		url1 = 'http://usher.justin.tv/find/'+name+'.json?type=live'
		data = json.loads(GET(url1))
		print url1
		print data
		if data == []:
			showMessage('Twitch.TV','Стрим не найден')
			return
		else:
			try:
				token = ' jtv='+data[0]['token'].replace('\\','\\5c').replace(' ','\\20').replace('"','\\22')
			except:
				showMessage('Twitch.TV','Стрим не найден')
				return
			rtmp = data[0]['connect']+'/'+data[0]['play']
			swf = ' swfUrl=%s swfVfy=1' % getSwfUrl(name)
			Pageurl = ' Pageurl=http://www.justin.tv/'+name
			url1 = rtmp+token+swf+Pageurl
			print url1
			if play == True:
				info = xbmcgui.ListItem(name)
				playlist = xbmc.PlayList(1)
				playlist.clear()
				playlist.add(url1, info)
				xbmc.executebuiltin('playlist.playoffset(video,0)')
			else:
				item = xbmcgui.ListItem(path=url)
				xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)	
def getSwfUrl(channel_name):
        """Helper method to grab the swf url, resolving HTTP 301/302 along the way"""
        base_url = 'http://www.justin.tv/widgets/live_embed_player.swf?channel=%s' % channel_name
        headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
                   'Referer' : 'http://www.justin.tv/'+channel_name}
        req = urllib2.Request(base_url, None, headers)
        response = urllib2.urlopen(req)
        return response.geturl()	
	
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
		del params['func']
	except:
		func = None
		xbmc.log( '[%s]: Primary input' % addon_id, 1 )
		main_menu(params)
	if func != None:
		try: pfunc = globals()[func]
		except:
			pfunc = None
			xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
			showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
		if pfunc: pfunc(params)
