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

import httplib
import urllib
import urllib2
import re
import sys
import os
import Cookie

import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import socket
socket.setdefaulttimeout(50)

icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'icon.png'))
siteUrl = 'kino-live.org'
httpSiteUrl = 'http://' + siteUrl
sid_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin.video.kino-live.org.cookies.sid')

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

def GET(target, referer, post_params = None, accept_redirect = True, get_redirect_url = False):
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

		if response.status == 403:
			raise Exception("Forbidden, check credentials")
		if response.status == 404:
			raise Exception("File not found")
		if accept_redirect and response.status in (301, 302):
			target = response.getheader('location', '')
			if target.find("://") < 0:
				target = httpSiteUrl + target
			if get_redirect_url:
				return target
			else:
				return GET(target, referer, post_params, False)

		try:
			sc = Cookie.SimpleCookie()
			sc.load(response.msg.getheader('Set-Cookie'))
			fh = open(sid_file, 'w')
			fh.write(sc['session'].value)
			fh.close()
		except: pass

		if get_redirect_url:
			return False
		else:
			http = response.read()
			return http

	except Exception, e:
		showMessage('Error', e, 5000)
		return None

def mainScreen(params):
	li = xbmcgui.ListItem('[Категории]')
	uri = construct_request({
		'href': httpSiteUrl,
		'mode': 'getCategories'
	})
	xbmcplugin.addDirectoryItem(h, uri, li, True)

	li = xbmcgui.ListItem('[Поиск]')
	uri = construct_request({
		'mode': 'runSearch'
	})
	xbmcplugin.addDirectoryItem(h, uri, li, True)

	readCategory({
		'href': httpSiteUrl
	});

def readCategory(params, postParams = None):
	categoryUrl = urllib.unquote_plus(params['href'])
	http = GET(categoryUrl, httpSiteUrl, postParams)
	if http == None: return False

	beautifulSoup = BeautifulSoup(http)
	content = beautifulSoup.find('div', attrs={'id': 'dle-content'})
	dataRows = content.findAll('div', 'tezt')

	if len(dataRows) == 0:
		showMessage('ОШИБКА', 'Неверная страница', 3000)
		return False
	else:
		for data in dataRows:
			img = data.find('img')
			cover = img['src']
			if cover.find("://") < 0:
				cover = httpSiteUrl + cover
			titleText = img['alt'].encode('utf-8', 'cp1251')

			link = data.findNextSibling('div', 'more').find('a')
			href = link['href']
			plotEl = data.find('div', id=re.compile('news-id-\d+'))
			itemInfo = []
			for plotItemRow in plotEl.contents:
			    try:
				itemInfo.append(plotItemRow.encode('utf-8', 'cp1251'))
			    except:
				pass
			plot = "\n".join(itemInfo[2:])
			li = xbmcgui.ListItem(titleText, iconImage = cover, thumbnailImage = cover)
			li.setProperty('IsPlayable', 'false')
			li.setInfo(type='video', infoLabels={'title': titleText, 'plot': plot})
			uri = construct_request({
				'mode': 'getFiles',
				'cover': cover,
				'title': titleText,
				'href': href
			})
			xbmcplugin.addDirectoryItem(h, uri, li, True)

	#TODO: Find a way to use pager in search results
	if postParams == None:
		try:
			pager = content.find('div', 'pages')
			pages = pager.findAll('a')
			nextPageLink = pages[len(pages) - 1]
			if nextPageLink != None:
				li = xbmcgui.ListItem('[NEXT PAGE >]')
				li.setProperty('IsPlayable', 'false')
				uri = construct_request({
					'href': nextPageLink['href'],
					'mode': 'readCategory'
				})
				xbmcplugin.addDirectoryItem(h, uri, li, True)
		except:
			pass

	xbmcplugin.endOfDirectory(h)

def getCategories(params):
	categoryUrl = urllib.unquote_plus(params['href'])
	http = GET(categoryUrl, httpSiteUrl)
	if http == None: return False

	beautifulSoup = BeautifulSoup(http)
	categoryContainer = beautifulSoup.find('ul', 'cats')
	categories = categoryContainer.findAll('a')
	if len(categories) == 0:
		showMessage('ОШИБКА', 'Неверная страница', 3000)
		return False
	else:
		for link in categories:
			if link != None:
				title = link.string
				if title == None:
					title = link.find("h2").string
				href = link['href']
				if href.find("://") < 0:
					href = httpSiteUrl + href
				li = xbmcgui.ListItem('[%s]' % title)
				li.setProperty('IsPlayable', 'false')
				uri = construct_request({
					'href': href,
					'mode': 'readCategory'
				})
				xbmcplugin.addDirectoryItem(h, uri, li, True)

	xbmcplugin.endOfDirectory(h)

def getFiles(params):
	folderUrl = urllib.unquote_plus(params['href'])
	cover = urllib.unquote_plus(params['cover'])
	itemName = urllib.unquote_plus(params['title'])

	http = GET(folderUrl, httpSiteUrl)
	if http == None: return False

	playListRegexp = re.compile('pl=([^"]+)',re.IGNORECASE + re.DOTALL + re.MULTILINE)
	playlist = playListRegexp.findall(http)

	if len(playlist) > 0:
		commentRegexp = re.compile('"comment":"\s*([^"]+)',re.IGNORECASE + re.DOTALL + re.MULTILINE)
		fileRegexp = re.compile('"file":"\s*([^"]+)',re.IGNORECASE + re.DOTALL + re.MULTILINE)
		playlistJson = GET(playlist[0], folderUrl)
		comments = commentRegexp.findall(playlistJson)
		files = fileRegexp.findall(playlistJson)
		i = 0
		for comment in comments:
			li = xbmcgui.ListItem(comment, iconImage = cover, thumbnailImage = cover)
			li.setProperty('IsPlayable', 'true')
			li.setInfo(type='video', infoLabels={'title': itemName + ' - ' + comment})
			uri = construct_request({
				'mode': 'play',
				'file': files[i],
				'referer': folderUrl
			})
			xbmcplugin.addDirectoryItem(h, uri, li)
			i = i + 1
			xbmcplugin.endOfDirectory(h)
	else:
		fileRegexp = re.compile('file=([^"]+)',re.IGNORECASE + re.DOTALL + re.MULTILINE)
		files = fileRegexp.findall(http)

		li = xbmcgui.ListItem(itemName, iconImage = cover, thumbnailImage = cover)
		li.setProperty('IsPlayable', 'true')
		li.setInfo(type='video', infoLabels={'title': itemName})
		xbmc.Player().play(files[0], li)

def runSearch(params):
	skbd = xbmc.Keyboard()
	skbd.setHeading('Что ищем?')
	skbd.doModal()
	if skbd.isConfirmed():
		SearchStr = skbd.getText()
		params = {
			'href': httpSiteUrl
		}
		postParams = {
			'do': 'search',
			'subaction': 'search',
			'story': SearchStr.decode('utf-8').encode('cp1251')
		}
		return readCategory(params, postParams)

def play(params):
	referer = urllib.unquote_plus(params['referer'])
	file = urllib.unquote_plus(params['file'])
	headers['Referer'] = referer

	file = urllib.urlopen(file)
	fileUrl = file.geturl()

	i = xbmcgui.ListItem(path = fileUrl)
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
	mainScreen(params)

if (mode != None):
	try:
		func = globals()[mode]
	except:
		pass
	if func: func(params)
