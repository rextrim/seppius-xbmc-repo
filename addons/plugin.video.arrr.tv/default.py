#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   Writer (c) 05/05/2011, Khrysev D.A., E-mail: x86demon@gmail.com
#
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

import urllib, urllib2, re, sys, os, httplib, Cookie
#import simplejson as json
import xbmcplugin, xbmcgui, xbmcaddon, xbmc
from BeautifulSoup import BeautifulSoup
import socket
socket.setdefaulttimeout(50)

icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'icon.png'))
siteUrl = 'arrr.tv'
httpSiteUrl = 'http://' + siteUrl
__settings__ = xbmcaddon.Addon(id='plugin.video.arrr.tv')

h = int(sys.argv[1])

def showMessage(heading, message, times = 3000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))
	#print "%s - %s" % (heading, message)

headers  = {
		'User-Agent' : 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00',
		'Accept'     :' text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*',
		'Accept-Language':'ru-RU,ru;q=0.9,en;q=0.8',
		'Accept-Charset' :'utf-8, utf-16, *;q=0.1',
		'Accept-Encoding':'identity, *;q=0'
	}

sid_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin_video_arrr_tv.sid')
#sid_file = os.path.join('.', 'plugin_video_arrr_tv.sid')

def GET(target, referer, post_params = None):
	try:
		connection = httplib.HTTPConnection(siteUrl)

		if post_params == None:
			method = 'GET'
			post = None
		else:
			method = 'POST'
			post = urllib.urlencode(post_params)
			headers['Content-Type'] = 'application/x-www-form-urlencoded'

		if os.path.isfile(sid_file):
			fh = open(sid_file, 'r')
			csid = fh.read()
			fh.close()
			headers['Cookie'] = 'session=%s' % csid

		headers['Referer'] = referer
		connection.request(method, target, post, headers = headers)
		response = connection.getresponse()

		try:
			sc = Cookie.SimpleCookie()
			sc.load(response.msg.getheader('Set-Cookie'))
			fh = open(sid_file, 'w')
			fh.write(sc['session'].value)
			fh.close()
		except: pass

		http = response.read()

		return http

	except Exception, e:
		showMessage(target, e, 5000)
		return None


def getshows(params):
	http = GET(httpSiteUrl + '/all/', httpSiteUrl)
	if http == None: return False

	processedShows = [];

	beautifulSoup = BeautifulSoup(http)
	shows = beautifulSoup.findAll('div', 'cover')

	if len(shows) == 0:
		showMessage('ОШИБКА', 'Неверная страница', 3000)
		return False
	else:
		showTitleType = __settings__.getSetting("Show title")
		for show in shows:
			try:
				showId = show['id']
				try:
					processedShows.index(showId)
				except:
					processedShows.append(showId)
					originalName = showId.replace('id_', '').replace('-', ' ')
					originalName = originalName[0].upper() + originalName[1:]

					href = show.find('a')['href']
					name = show.find('h3').string
					cover = httpSiteUrl + show.find('img', 'fluffy_shadow')['src']
					title = originalName
					
					if showTitleType == "0":
						title = name
					if showTitleType == "2":
						title += '/' + name

					li = xbmcgui.ListItem(title, iconImage = cover, thumbnailImage = cover)
					uri = sys.argv[0] + '?mode=getseries'
					uri += '&href='+urllib.quote_plus(href)
					uri += '&referer='+urllib.quote_plus(httpSiteUrl + '/all/')
					uri += '&tvshow='+urllib.quote_plus(originalName)
					xbmcplugin.addDirectoryItem(h, uri, li, True)
			except:
				pass

		xbmcplugin.endOfDirectory(h)


def getseries(params):
	#params = {'href': 'http://arrr.tv/show/dexter/', 'referer': 'http://arrr.tv/all/'}
	href = httpSiteUrl + urllib.unquote_plus(params['href'])
	try:
		http = GET(href, urllib.unquote_plus(params['referer']))
		if http == None: return False
	except: return False

	tvshow = urllib.unquote_plus(params['tvshow'])

	headers['Referer'] = href

	beautifulSoup = BeautifulSoup(http)

	#TODO: get qualities and formats from JSON string
	#jsonRegexp = re.compile('var episodes = {([^;]+)')
	#episodesDataString = str(beautifulSoup.find(text = re.compile('var episodes') ))
	#episodesDataString = re.sub('\],[\s|\n|\t]*{', '] {',  jsonRegexp.findall(episodesDataString)[0])
	#print json.loads('{' + jsonRegexp.findall(episodesDataString)[0] + '}')

	episodes = beautifulSoup.findAll('div', 'episode')
	episodeRegexp = re.compile(u'Сезон (\d+), серия (\d+)', re.IGNORECASE + re.DOTALL + re.MULTILINE)
	for episode in episodes:
		episodeId = episode['name']
		name = episode.find('h3', 'title').find('a').string
		poster = episode.find('img', 'poster')['src']
		episodeDetails = episode.find('div', 'info').find('div', 'right').find('a').string
		
		(seasonNum, episodeNum) = episodeRegexp.findall(episodeDetails)[0]
		episodeNum = int(episodeNum)
		seasonNum = int(seasonNum)
		
		listName = "[s%de%02d] %s" % (seasonNum, episodeNum, name)
		uri = sys.argv[0] + '?mode=play'
		uri += '&href='+urllib.quote_plus(episodeId)
		uri += '&referer='+params['href']
		item = xbmcgui.ListItem(listName, iconImage=poster, thumbnailImage=poster)
		item.setInfo(type='video', infoLabels={'title': name,'episode': episodeNum, 'season': seasonNum, 'tvshowtitle': tvshow})			
		item.setProperty('IsPlayable', 'true')
		xbmcplugin.addDirectoryItem(h,uri,item)

	xbmcplugin.endOfDirectory(h)


def play(params):
	episodeId  = urllib.unquote_plus(params['href'])
	referer = urllib.unquote_plus(params['referer'])

	movieFile = detectUrl(episodeId)
	
	headers['Referer'] = referer
	i = xbmcgui.ListItem(path = movieFile)
	i.setProperty('mimetype', 'video/x-msvideo')
	xbmcplugin.setResolvedUrl(h, True, i)

def detectUrl(episodeId):
	formats = ['mp4', 'ogv', 'webm']

	qualities = ['p480', 'p720']
	if __settings__.getSetting("Prefer 720p") == "1":
		qualities = ['p720', 'p480']

	languages = ['ru', 'en']
	if __settings__.getSetting("Prefered language") == "1":
		languages = ['en', 'ru']
	
	cdns = ['http://cdn2.arrr.tv/', 'http://video8.neetee.tv/atv/']
	
	for language in languages:
		for quality in qualities:
			for format in formats:
				for server in cdns:
					url = server + episodeId + ':' + quality + ':' + language + '.' + format
					if(isRemoteFile(url)):
						return url
	return False

def isRemoteFile(url):
	if __settings__.getSetting("Use fast start") == "true":
		return True
	else:
		try:
			f = urllib2.urlopen(urllib2.Request(url))
			return True
		except:
			return False

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
	return param

params = get_params(sys.argv[2])

mode   = None
func   = None

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	getshows(params)

if (mode != None):
	try:
		func = globals()[mode]
	except:
		pass
	if func: func(params)
