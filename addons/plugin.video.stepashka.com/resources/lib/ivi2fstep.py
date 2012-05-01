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
import httplib
import urllib
import urllib2

import re
try:
	from hashlib import md5
except:
	from md5 import md5

import sys
import os
import Cookie
import subprocess

import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon
import time
import random
from urllib import unquote, quote


VERSION = '4.3as'
DOMAIN = '131896016'
UATRACK = 'UA-31027962-1'
conf_file = os.path.join(xbmc.translatePath('special://temp/'), 'settings.stepashka.dat')

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
UA = '%s/%s %s/%s/%s' % (addon_type, addon_id, urllib.quote_plus(addon_author), addon_version, urllib.quote_plus(addon_name))

if os.path.isfile(conf_file):
	try:
		f = open(conf_file, 'r')
		GAcookie=f.readline()
		uniq_id=f.readline()
	except:
		f = open(conf_file, 'w')
		GAcookie ="__utma%3D"+DOMAIN+"."+str(random.randint(0, 0x7fffffff))+"."+str(random.randint(0, 0x7fffffff))+"."+str(int(time.time()))+"."+str(int(time.time()))+".1%3B"
		uniq_id=random.random()*time.time()
		f.write(GAcookie)
		f.write('\n')
		f.write(str(uniq_id))
		f.close()
else: 
	f = open(conf_file, 'w')
	GAcookie ="__utma%3D"+DOMAIN+"."+str(random.randint(0, 0x7fffffff))+"."+str(random.randint(0, 0x7fffffff))+"."+str(int(time.time()))+"."+str(int(time.time()))+".1%3B"
	uniq_id=random.random()*time.time()
	f.write(GAcookie)
	f.write('\n')
	f.write(str(uniq_id))
	f.close()
#print GAcookie
#print uniq_id

def get_random_number():
	return str(random.randint(0, 0x7fffffff))

#COOKIEJAR = None
#COOKIEFILE = os.path.join(xbmc.translatePath('special://temp/'), 'cookie.%s.txt' % DOMAIN)


def send_request_to_google_analytics(utm_url, ua):

	try:
		req = urllib2.Request(utm_url, None, {'User-Agent':UA} )
		response = urllib2.urlopen(req).read()
		#print utm_url
		
	except:
		#print ("GA fail: %s" % utm_url)     
		showMessage('IVI Player', "GA fail: %s" % utm_url, 2000)
	#print str(response)
	return response
           
def track_page_view(path,nevent='', tevent=''):
	domain = DOMAIN
	document_path = unquote(path)
	utm_gif_location = "http://www.google-analytics.com/__utm.gif"
	extra = {}
	extra['screen'] = xbmc.getInfoLabel('System.ScreenMode')

        # // Construct the gif hit url.
	utm_url = utm_gif_location + "?" + \
		"utmwv=" + VERSION + \
		"&utmn=" + get_random_number() + \
		"&utmsr=" + quote(extra.get("screen", "")) + \
		"&utmt=" + nevent + \
		"&utme=" + tevent +\
		"&utmhn=localhost" + \
		"&utmr=" + quote('-') + \
		"&utmp=" + quote(document_path) + \
		"&utmac=" + UATRACK + \
		"&utmcc="+ GAcookie
        # dbgMsg("utm_url: " + utm_url) 
	#print "Analitycs: %s" % utm_url
	return send_request_to_google_analytics(utm_url, UA)

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
siteUrl = 'online.stepashka.com'
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
	li = xbmcgui.ListItem('[Поиск]', addon_fanart, addon_icon)
	li.setProperty('IsPlayable', 'false')
	uri = construct_request({
		'func': 'doSearch'
		})
	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	http = GET(httpSiteUrl)
	if http == None: return False
	beautifulSoup = BeautifulSoup(http)
	content = beautifulSoup.find('ul', attrs={'class': 'lmenu reset'})
	cats=content.findAll('a')
	#print content
	#dat_file = os.path.join(addon_path, 'categories.txt')
	#f = open(dat_file, 'r')
	for line in cats:
		title=None
		if line.string:	title = str(line.string)
		else: title = str(line.find('b').string)
		if title!='None':
			li = xbmcgui.ListItem(title, addon_fanart, addon_icon)
			li.setProperty('IsPlayable', 'false')
			href = line['href']
			uri = construct_request({
				'href': href,
				'func': 'readCategory'
			})
			xbmcplugin.addDirectoryItem(hos, uri, li, True)

	xbmcplugin.endOfDirectory(hos)

def doSearch(params):
	track_page_view('search')
	kbd = xbmc.Keyboard()
	kbd.setDefault('')
	kbd.setHeading('Поиск')
	kbd.doModal()
	if kbd.isConfirmed():
		sts=kbd.getText();
		params['href'] = 'http://online.stepashka.com/?do=search&subaction=search&story=' + sts
		readCategory(params)	

def readCategory(params, postParams = None):
	track_page_view(params['href'])
	fimg=None
	http = GET(params['href'])
	if http == None: return False
	beautifulSoup = BeautifulSoup(http)
 	content = beautifulSoup.find('div', attrs={'id': 'dle-content'})
	dataRows = beautifulSoup.findAll('div', attrs={'class': 'base shortstory'})
	print dataRows
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
	try:
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
	except: pass
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
		jsdata=None
		try: jsdata = json.loads(http)
		except: pass
		if not jsdata: exit
		has_sesons=False
		playlist = jsdata['playlist']
		for file in playlist:
			try:
				li = xbmcgui.ListItem(file['comment'], addon_icon, params['src'])
				li.setProperty('IsPlayable', 'true')
				uri = construct_request({
					'func': 'play',
					'file': file['file']
					})
				xbmcplugin.addDirectoryItem(hos, uri, li, False)
			except: pass
			try:
				for t in file['playlist']:
				#print t
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
			except: pass
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
	track_page_view('','event','5(Video*Videostart)')
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
