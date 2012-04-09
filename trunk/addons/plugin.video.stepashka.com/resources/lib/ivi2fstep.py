#!/usr/bin/python
# -*- coding: utf-8 -*-

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
import xbmcaddon




__addon__ = xbmcaddon.Addon( id = 'plugin.video.stepashka.com' )
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
show_len=50

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

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import socket
socket.setdefaulttimeout(50)

icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'icon.png'))
siteUrl = 'stepashka.com'
httpSiteUrl = 'http://' + siteUrl
sid_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin.video.stepashka.com.cookies.sid')


def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))


def showMessage(heading, message, times = 3000, pics = addon_icon):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
	except Exception, e:
		xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )

headers  = {
	'User-Agent' : 'XBMC',
	'Accept'     :' text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*',
	'Accept-Language':'ru-RU,ru;q=0.9,en;q=0.8',
	'Accept-Charset' :'utf-8, utf-16, *;q=0.1',
	'Accept-Encoding':'identity, *;q=0'
}

def GET(target, post=None):
	#print target
	try:
		req = urllib2.Request(url = target, data = post, headers = headers)
		resp = urllib2.urlopen(req)
		CE = resp.headers.get('content-encoding')
		http = resp.read()
		resp.close()
		return http
	except Exception, e:
		xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
		showMessage('HTTP ERROR', e, 5000)

def mainScreen(params):
	http = GET(httpSiteUrl)
	if http == None: return False
	dat_file = os.path.join(addon_path, 'categories.txt')
	f = open(dat_file, 'r')
	for line in f:
		title = line.split(',')[1]
		href = line.split(',')[0]
		li = xbmcgui.ListItem('[%s]' % title, addon_fanart, addon_icon)
		li.setProperty('IsPlayable', 'false')
		uri = construct_request({
			'href': href,
			'func': 'readCategory'
		})
		xbmcplugin.addDirectoryItem(hos, uri, li, True)

	xbmcplugin.endOfDirectory(hos)

	

def readCategory(params, postParams = None):
	fimg=None
	http = GET(params['href'])
	if http == None: return False
	beautifulSoup = BeautifulSoup(http)
 	content = beautifulSoup.find('div', attrs={'id': 'dle-content'})
	dataRows = beautifulSoup.findAll('div', attrs={'class': 'base shortstory'})
	if len(dataRows) == 0:
		showMessage('ОШИБКА', 'Неверная страница', 3000)
		return False
	else:
		for link in dataRows:
			sec=0
			if link != None:
				title = link.find('a').string
				if sec==1:
					sec=0
				else:
					sec=1
					href = link.find('a')['href']
					fimg=link.find('img')
					li = xbmcgui.ListItem('[%s]' % title, addon_icon, fimg['src'])
					li.setProperty('IsPlayable', 'false')
					uri = construct_request({
						'title': title,
						'href': href,
						'func': 'readFile',
						'src': fimg['src']
						})
					xbmcplugin.addDirectoryItem(hos, uri, li, True)
	dataRows1 = beautifulSoup.find('div', attrs={'class': 'navigation'})
	dataRows = dataRows1.findAll('a')
	#print dataRows
	if len(dataRows) == 0:
		showMessage('ОШИБКА', 'Неверная страница', 3000)
		return False
	else:
		for link in dataRows:
			href = link['href']
			title = link.string
			li = xbmcgui.ListItem('[%s]' % title, addon_icon, addon_icon)
			li.setProperty('IsPlayable', 'false')
			uri = construct_request({
				'title': title,
				'href': href,
				'func': 'readCategory',
				})
			xbmcplugin.addDirectoryItem(hos, uri, li, True)
	xbmcplugin.endOfDirectory(hos)

def readFile(params):
	http = GET(params['href'])
	if http == None: return False
	beautifulSoup = BeautifulSoup(http)
	content = beautifulSoup.find('param', attrs={'name': 'flashvars'})
	findfile=str(content)
	vurl=findfile.split(';')
	for ur in vurl:	findfile=ur
	vurl=findfile.split('"')
	lurl=vurl[0]
	if lurl.split('=')[0]=='file': 
		print 'play file ' + lurl.split('=')[1]
		li = xbmcgui.ListItem(params['title'], addon_icon, params['src'])
		li.setProperty('IsPlayable', 'true')
		uri = construct_request({
			'func': 'play',
			'file': lurl.split('=')[1]
			})
		xbmcplugin.addDirectoryItem(hos, uri, li, False)
	else: 
		print 'playlist in ' + lurl.split('=')[1]
		http = GET(lurl.split('=')[1])
		jsdata = json.loads(http)
		has_sesons=False
		playlist = jsdata['playlist']
		for file in playlist:
			for t in file['playlist']:
				li = xbmcgui.ListItem(t['comment'], addon_icon, params['src'])
				li.setProperty('IsPlayable', 'true')
				uri = construct_request({
					'func': 'play',
					'file': t['file']
					})
				has_sesons=True
				xbmcplugin.addDirectoryItem(hos, uri, li, False)
			if has_sesons==False:
				li = xbmcgui.ListItem(file['comment'], addon_icon, params['src'])
				li.setProperty('IsPlayable', 'true')
				uri = construct_request({
					'func': 'play',
					'file': file['file']
					})
				xbmcplugin.addDirectoryItem(hos, uri, li, False)
	xbmcplugin.endOfDirectory(hos)

	
def geturl(url):
	f = None
	url=url[1:len(url)]
	myhttp = 'http://fcsd.tv/ru/xmlinfo/?idv=%s' % url
	http = GET('http://fcsd.tv/ru/xmlinfo/?idv=%s' % url)
	if http == None: return False
	beautifulSoup = BeautifulSoup(http)
	furl=beautifulSoup.find('video')
	f=furl.find('hq')
	if not f: f=furl.find('rq')
	return f['url']

def play(params):
	i = xbmcgui.ListItem(path = params['file'])
	xbmcplugin.setResolvedUrl(hos, True, i)
	
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
		mainScreen(params)
	if func != None:
		try: pfunc = globals()[func]
		except:
			pfunc = None
			xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
			showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
		if pfunc: pfunc(params)
