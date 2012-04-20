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

import time
import random
from urllib import unquote, quote


__addon__ = xbmcaddon.Addon( id = 'plugin.video.fcsd.tv' )
__language__ = __addon__.getLocalizedString

addon_icon    = __addon__.getAddonInfo('icon')
addon_fanart  = __addon__.getAddonInfo('fanart')
addon_path    = __addon__.getAddonInfo('path')
addon_type    = __addon__.getAddonInfo('type')
addon_id      = __addon__.getAddonInfo('id')
addon_author  = __addon__.getAddonInfo('author')
addon_name    = __addon__.getAddonInfo('name')
addon_version = __addon__.getAddonInfo('version')

VERSION = '4.3as'
DOMAIN = '131896016'
UATRACK = 'UA-31027962-2'
conf_file = os.path.join(xbmc.translatePath('special://temp/'), 'settings.fcsd.dat')

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
	
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import socket
socket.setdefaulttimeout(50)

icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'icon.png'))
siteUrl = 'fcsd.tv'
httpSiteUrl = 'http://' + siteUrl
sid_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin.video.fcsd.tv.cookies.sid')


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
	beautifulSoup = BeautifulSoup(http)
	content = beautifulSoup.find('td', 'menu')
	categories = content.findAll('a')
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
				li = xbmcgui.ListItem('[%s]' % title, addon_fanart, addon_icon)
				li.setProperty('IsPlayable', 'false')
				uri = construct_request({
					'href': href,
					'func': 'readCategory'
				})
				xbmcplugin.addDirectoryItem(hos, uri, li, True)

	xbmcplugin.endOfDirectory(hos)

	

def readCategory(params, postParams = None):
	track_page_view(params['href'])
	fimg=None
	http = GET(params['href'])
	if http == None: return False
	beautifulSoup = BeautifulSoup(http)
 	content = beautifulSoup.find('div', attrs={'class': 'main_preview_abs'})
	if content == None:
		content = beautifulSoup.find('div', attrs={'class': 'contentleft'})
	dataRows = content.findAll('a')
	if len(dataRows) == 0:
		showMessage('ОШИБКА', 'Неверная страница', 3000)
		return False
	else:
		for link in dataRows:
			#print link
			if link != None:
				title = link.string
				if title == None:
					fimg=link.find('img')
					if fimg: print fimg['src']
				else:
					href = link['href']
					if href.find("://") < 0:
						href = httpSiteUrl + href
					vurl=href.split('/')
					for ur in vurl:	lurl=ur
					if len(lurl)> 0: 
						if lurl[0]=='v': 
							print link
							li = xbmcgui.ListItem('%s' % title, addon_icon, fimg['src'])
							li.setProperty('IsPlayable', 'true')
							uri = construct_request({
								'href': href,
								'func': 'play',
								'file': lurl
							})
							xbmcplugin.addDirectoryItem(hos, uri, li, False)
						else: 
							li = xbmcgui.ListItem('[%s]' % title)
							li.setProperty('IsPlayable', 'false')
							uri = construct_request({
								'href': href,
								'func': 'readCategory'
							})
							xbmcplugin.addDirectoryItem(hos, uri, li, True)

	xbmcplugin.endOfDirectory(hos)

	
def geturl(url):
	#print url
	f = None
	url=url[1:len(url)]
	myhttp = 'http://fcsd.tv/ru/xmlinfo/?idv=%s' % url
	#print myhttp
	http = GET('http://fcsd.tv/ru/xmlinfo/?idv=%s' % url)
	if http == None: return False
	beautifulSoup = BeautifulSoup(http)
	furl=beautifulSoup.find('video')
	#print furl['img']
	f=furl.find('hq')
	if not f: f=furl.find('rq')
	#print f['url']
	return f['url']

def play(params):
	track_page_view('','event','5(Video*Videostart)')
	fileUrl= geturl(params['file'])
	i = xbmcgui.ListItem(path = fileUrl)
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
	#xbmc.log( '[s]: play' , 2 )
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
