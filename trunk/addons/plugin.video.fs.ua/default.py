#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   Writer (c) 23/06/2011, Khrysev D.A., E-mail: x86demon@gmail.com
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
import xbmcplugin, xbmcgui, xbmcaddon, xbmc
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import socket
socket.setdefaulttimeout(50)

icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'icon.png'))
siteUrl = 'fs.ua'
httpSiteUrl = 'http://' + siteUrl
__settings__ = xbmcaddon.Addon(id='plugin.video.fs.ua')

h = int(sys.argv[1])

def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

def htmlEntitiesDecode(string):
	return BeautifulStoneSoup(string, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents[0]

def showMessage(heading, message, times = 3000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

headers  = {
		'User-Agent' : 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00',
		'Accept'     :' text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*',
		'Accept-Language':'ru-RU,ru;q=0.9,en;q=0.8',
		'Accept-Charset' :'utf-8, utf-16, *;q=0.1',
		'Accept-Encoding':'identity, *;q=0'
	}

sid_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin_video_fs_ua.sid')

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

		if response.status in (301, 302):
			target = response.getheader('location', '')
			return GET(httpSiteUrl + target, referer, post_params)

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

def getCategories(params):
	sortBy = __settings__.getSetting("Sort by")
	sortByMap = {'0': 'new', '1': 'rating', '2': 'year'}
	sortByString = '?sort=' + sortByMap[sortBy]

	li = xbmcgui.ListItem('Tv Shows')
	uri = construct_request({
		'href': httpSiteUrl + '/serials' + sortByString,
		'mode': 'readcategory',
		'section': 'serials',
		'firstPage': 'yes'
	})
	xbmcplugin.addDirectoryItem(h, uri, li, True)

	li = xbmcgui.ListItem('Movies')
	uri = construct_request({
		'href': httpSiteUrl + '/films' + sortByString,
		'mode': 'readcategory',
		'section': 'films',
		'firstPage': 'yes'
	})
	xbmcplugin.addDirectoryItem(h, uri, li, True)

	li = xbmcgui.ListItem('Clips')
	uri = construct_request({
		'href': httpSiteUrl + '/clips' + sortByString,
		'mode': 'readcategory',
		'section': 'clips',
		'firstPage': 'yes'
	})
	xbmcplugin.addDirectoryItem(h, uri, li, True)

	li = xbmcgui.ListItem('Music')
	uri = construct_request({
		'href': httpSiteUrl + '/music' + sortByString,
		'mode': 'readcategory',
		'section': 'music',
		'firstPage': 'yes'
	})
	xbmcplugin.addDirectoryItem(h, uri, li, True)

	xbmcplugin.endOfDirectory(h)

def readcategory(params):
	sortBy = __settings__.getSetting("Sort by")
	newLook = params['firstPage'] == 'yes' and sortBy == "1"

	categoryUrl = urllib.unquote_plus(params['href'])
	http = GET(categoryUrl, httpSiteUrl)
	if http == None: return False

	beautifulSoup = BeautifulSoup(http)
	if newLook:
		items = beautifulSoup.findAll('div', 'b-poster')
	else:
		items = beautifulSoup.findAll('a', 'subject-link')

	if len(items) == 0:
		showMessage('ОШИБКА', 'Неверная страница', 3000)
		return False
	else:
		for item in items:
			title = None
			cover = None
			href = None

			if newLook:
				coverRegexp = re.compile('url\s*\(([^\)]+)')
				cover = coverRegexp.findall(str(item['style']))[0]

				linkItem = item.find('a', 'details-link')
				href = httpSiteUrl + '/dl' + linkItem['href']
				title = re.sub('\s+', ' ', str(linkItem.string))
				title = re.sub('(^\s+|\s+$)', '', title)
			else:
				img = item.find('img')
				if img != None:
					cover = img['src']
					title = img['alt']
					href = httpSiteUrl + '/dl' + item['href']

			if title != None:
				li = xbmcgui.ListItem(htmlEntitiesDecode(title), iconImage = cover)
				li.setProperty('IsPlayable', 'false')

				isMusic = 'no'
				if params['section'] == 'music':
					isMusic = 'yes'

				uri = construct_request({
					'href': href,
					'referer': categoryUrl,
					'mode': 'readdir',
					'cover': cover,
					'isMusic': isMusic
				})

				xbmcplugin.addDirectoryItem(h, uri, li, True)

	nextPageLink = beautifulSoup.find('a', 'next-link')
	if nextPageLink != None:
		li = xbmcgui.ListItem('[NEXT PAGE >]')
		li.setProperty('IsPlayable', 'false')
		uri = construct_request({
			'href': httpSiteUrl + nextPageLink['href'],
			'mode': 'readcategory',
			'section': params['section'],
			'firstPage': 'no'
		})
		xbmcplugin.addDirectoryItem(h, uri, li, True)

	xbmcplugin.endOfDirectory(h)

def readdir(params):
	folderUrl = urllib.unquote_plus(params['href'])
	cover = urllib.unquote_plus(params['cover'])

	http = GET(folderUrl, httpSiteUrl)
	if http == None: return False

	beautifulSoup = BeautifulSoup(http)
	mainItems = beautifulSoup.find('ul', 'filelist')
	if mainItems == None:
		showMessage('ОШИБКА', 'No filelist', 3000)
		return False

	items = mainItems.findAll('li')

	if len(items) == 0:
		showMessage('ОШИБКА', 'Неверная страница', 3000)
		return False
	else:
		for item in items:
			linkItem = item.find('a', 'link-material')
			isFolder = item['class'] == 'folder'

			if linkItem != None:
				title = str(linkItem.find('span').string)
				href = linkItem['href']

				li = None
				uri = None
				if isFolder:
					li = xbmcgui.ListItem(htmlEntitiesDecode(title), iconImage = cover)
					li.setProperty('IsPlayable', 'false')

					uri = construct_request({
						'cover': cover,
						'href': httpSiteUrl + href,
						'referer': folderUrl,
						'mode': 'readdir',
						'isMusic': params['isMusic']
					})
				else:
					li = xbmcgui.ListItem(htmlEntitiesDecode(title), iconImage = cover, path = href)
					li.setProperty('IsPlayable', 'true')
					type = 'video'
					if params['isMusic'] == 'yes':
						type = 'music'
					li.setInfo(type = type, infoLabels={'title': title})

					uri = href

				xbmcplugin.addDirectoryItem(h, uri, li, isFolder)

	xbmcplugin.endOfDirectory(h)


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
	getCategories(params)

if (mode != None):
	try:
		func = globals()[mode]
	except:
		pass
	if func: func(params)
