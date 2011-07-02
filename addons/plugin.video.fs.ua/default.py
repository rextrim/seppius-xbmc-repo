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

import urllib
import urllib2
import re
import sys
import os
import cookielib

import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import socket
socket.setdefaulttimeout(50)

icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'icon.png'))
siteUrl = 'fs.ua'
httpSiteUrl = 'http://' + siteUrl
__settings__ = xbmcaddon.Addon(id='plugin.video.fs.ua')
cookiepath = os.path.join(xbmc.translatePath('special://temp/'), 'plugin.video.fs.ua.cookies.lwp')

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

def GET(url, referer, post_params = None):
	headers['Referer'] = referer

	if post_params != None:
		post_params = urllib.urlencode(post_params)
		headers['Content-Type'] = 'application/x-www-form-urlencoded'
	elif headers.has_key('Content-Type'):
		del headers['Content-Type']

	jar = cookielib.LWPCookieJar(cookiepath)
	if os.path.isfile(cookiepath):
		jar.load()

	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
	urllib2.install_opener(opener)
	req = urllib2.Request(url, post_params, headers)

	response = opener.open(req)
	the_page = response.read()
	response.close()

	jar.save()

	return the_page

def check_login():
	login = __settings__.getSetting("Login")
	password = __settings__.getSetting("Password")

	if len(login) > 0:
		http = GET(httpSiteUrl, httpSiteUrl)
		if http == None: return False

		beautifulSoup = BeautifulSoup(http)
		userPanel = beautifulSoup.find('div', 'b-user-panel')

		if userPanel == None:
			loginResponse = GET(httpSiteUrl + '/login.aspx', httpSiteUrl, {
				'login': login,
				'passwd': password,
				'remember': 1
			})

			loginSoup = BeautifulSoup(loginResponse)
			userPanel = loginSoup.find('div', 'b-user-panel')
			if userPanel == None:
				showMessage('Login', 'Check login and password', 3000)
			else:
				return True
		else:
			return True
	return False

def getSortBy():
	sortBy = __settings__.getSetting("Sort by")
	sortByMap = {'0': 'new', '1': 'rating', '2': 'year'}
	return '?sort=' + sortByMap[sortBy]

def getCategories(params):
	sortByString = getSortBy()

	li = xbmcgui.ListItem('Tv Shows')
	uri = construct_request({
		'href': httpSiteUrl + '/serials' + sortByString,
		'mode': 'readcategory',
		'section': 'serials',
		'filter': '',
		'firstPage': 'yes'
	})
	xbmcplugin.addDirectoryItem(h, uri, li, True)

	li = xbmcgui.ListItem('Movies')
	uri = construct_request({
		'href': httpSiteUrl + '/films' + sortByString,
		'mode': 'readcategory',
		'section': 'films',
		'filter': '',
		'firstPage': 'yes'
	})
	xbmcplugin.addDirectoryItem(h, uri, li, True)

	li = xbmcgui.ListItem('Clips')
	uri = construct_request({
		'href': httpSiteUrl + '/clips' + sortByString,
		'mode': 'readcategory',
		'section': 'clips',
		'filter': '',
		'firstPage': 'yes'
	})
	xbmcplugin.addDirectoryItem(h, uri, li, True)

	li = xbmcgui.ListItem('Music')
	uri = construct_request({
		'href': httpSiteUrl + '/music' + sortByString,
		'mode': 'readcategory',
		'section': 'music',
		'filter': '',
		'firstPage': 'yes'
	})
	xbmcplugin.addDirectoryItem(h, uri, li, True)

	if check_login():
		li = xbmcgui.ListItem('Favorites')
		uri = construct_request({
			'mode': 'readfavorites'
		})
		xbmcplugin.addDirectoryItem(h, uri, li, True)

	xbmcplugin.endOfDirectory(h)

def readfavorites(params):
	sortByString = getSortBy()

	favoritesUrl = httpSiteUrl + '/myfavourites.aspx' + sortByString
	http = GET(favoritesUrl, httpSiteUrl)
	if http == None: return False

	beautifulSoup = BeautifulSoup(http)
	items = beautifulSoup.findAll('div', 'b-poster')
	if len(items) == 0:
		showMessage('ОШИБКА', 'В избранном пусто', 3000)
		return False
	else:
		for item in items:
			coverRegexp = re.compile('url\s*\(([^\)]+)')
			cover = coverRegexp.findall(str(item['style']))[0]
			linkItem = item.find('a', 'details-link')

			href = httpSiteUrl + '/dl' + linkItem['href']
			title = re.sub('\s+', ' ', str(linkItem.string))
			title = re.sub('(^\s+|\s+$)', '', title)

			li = xbmcgui.ListItem(htmlEntitiesDecode(title), iconImage = cover)
			li.setProperty('IsPlayable', 'false')

			isMusic = "no"
			if re.search('music', href):
				isMusic = "yes"

			uri = construct_request({
				'href': href,
				'referer': favoritesUrl,
				'mode': 'readdir',
				'cover': cover,
				'isMusic': isMusic
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
		if params['firstPage'] == 'yes':
			#Add search list item
			li = xbmcgui.ListItem("[ПОИСК]")
			li.setProperty('IsPlayable', 'false')
			uri = construct_request({
				'mode': 'runsearch',
				'section': params['section']
			})
			xbmcplugin.addDirectoryItem(h, uri, li, True)

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
			'filter': params['filter'],
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
						'href': httpSiteUrl + str(href.encode('utf-8')),
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
					
					if type == 'music' or __settings__.getSetting('Autoplay next') == 'true':
						uri = construct_request({
							'file': str(href.encode('utf-8')),
							'referer': folderUrl,
							'mode': 'play'
						})
					else:
						uri = href

				xbmcplugin.addDirectoryItem(h, uri, li, isFolder)

	xbmcplugin.endOfDirectory(h)

def runsearch(params):
	skbd = xbmc.Keyboard()
	skbd.setHeading('Что ищем?')
	skbd.doModal()
	if skbd.isConfirmed():
		SearchStr = skbd.getText()
		searchUrl = '%s/%s/search/?search=%s' % (httpSiteUrl, params['section'], urllib.quote_plus(SearchStr))
		params = {
			'href': searchUrl,
			'section': params['section']
		}
		return render_search_results(params)


def render_search_results(params):
	searchUrl = urllib.unquote_plus(params['href'])
	http = GET(searchUrl, httpSiteUrl + '/' + params['section'])
	if http == None: return False

	beautifulSoup = BeautifulSoup(http)
	items = beautifulSoup.find('div', 'main').findAll('tr')

	if len(items) == 0:
		showMessage('ОШИБКА', 'Ничего не найдено', 3000)
		return False
	else:
		for item in items:
			link = item.find('a', 'title')

			title = link.string
			href = httpSiteUrl + '/dl' + link['href']
			cover = item.find('img')['src']

			if title != None:
				li = xbmcgui.ListItem(htmlEntitiesDecode(title), iconImage = cover)
				li.setProperty('IsPlayable', 'false')

				isMusic = 'no'
				if params['section'] == 'music':
					isMusic = 'yes'

				uri = construct_request({
					'href': href,
					'referer': params['href'],
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
				'mode': 'render_search_results',
				'section': params['section']
			})
			xbmcplugin.addDirectoryItem(h, uri, li, True)

	xbmcplugin.endOfDirectory(h)

def play(params):
	referer = urllib.unquote_plus(params['referer'])
	file = urllib.unquote_plus(params['file'])

	headers['Referer'] = referer

	i = xbmcgui.ListItem(path = file)
	xbmcplugin.setResolvedUrl(h, True, i)

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
