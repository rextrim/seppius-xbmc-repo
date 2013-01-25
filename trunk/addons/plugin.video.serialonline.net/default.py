#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib
import urllib
import urllib2
import re
import sys
import os
import Cookie
import platform
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
import hashlib



__addon__ = xbmcaddon.Addon( id = 'plugin.video.serialonline.net' )
__language__ = __addon__.getLocalizedString
sys.path.append( os.path.join( __addon__.getAddonInfo( 'path' ), 'resources', 'lib') )

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

httpSiteUrl='http://serialonline.net/'

import sqlite3 as db
db_name = os.path.join( addon_path, "requests.db" )
c = db.connect(database=db_name)
cu = c.cursor()

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

def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))


def showMessage(heading, message, times = 3000, pics = addon_icon):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
	except Exception, e:
		xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )

MAX_DELAY=99999999999
			
def add_to_db(n, item):
	err=0
	m = hashlib.md5()
	m.update(str(n))
	req=m.hexdigest()
	#print req
	data=quote(item)	
	litm=str(len(data))
	try:
		old=[]
		for row in cu.execute('SELECT time FROM cache ORDER BY time'):
			tout = row[0]
			#print tout
			delay=int(time.time())-int(tout)
			#print delay
			if int(delay)>MAX_DELAY:
				old.append(tout)
				#print 'запись удалена %s'%str(tout)
				#cu.execute("DELETE FROM cache WHERE link = '%s'" % req)
				#c.commit()
		for dels in old:
			print 'запись удалена %s'%str(dels)
			cu.execute("DELETE FROM cache WHERE time = '%s'" % dels)
			c.commit()
	except: pass
	#try:
	#	cu.execute("SELECT time FROM cache WHERE link = '%s'" % req)
	#	c.commit()
	#	tout = cu.fetchone()[0]
	#	if int(tout)>0:
	#		delay=int(time.time())-int(tout)
	#		if int(delay)>MAX_DELAY:
	#			print 'запись удалена %s'%str(tout)
	#			cu.execute("DELETE FROM cache WHERE link = '%s'" % req)
	#			c.commit()
	#			info=''
	#except:pass
	try:
		cu.execute("INSERT INTO cache VALUES ('%s','%s','%s')"%(req,data,int(time.time())))
		c.commit()
	except:
		cu.execute("CREATE TABLE cache (link, data, time int)")
		c.commit()
		cu.execute("INSERT INTO cache VALUES ('%s','%s','%s')"%(req,data,int(time.time())))
		c.commit()


def get_inf_db(n):
	m = hashlib.md5()
	m.update(str(n))
	req=m.hexdigest()
	cu.execute("SELECT time FROM cache WHERE link = '%s'" % req)
	c.commit()
	tout = cu.fetchone()[0]
	if int(tout)>0:
		delay=int(time.time())-int(tout)
		#print 'delay=%s'%str(delay)
		if int(delay)>MAX_DELAY:
			#print 'запись удалена %s'%str(tout)
			cu.execute("DELETE FROM cache WHERE link = '%s'" % req)
			c.commit()
			info=''
			#print 'запись удалена %s'%tout
		else:
			cu.execute("SELECT data FROM cache WHERE link = '%s'" % req)
			c.commit()
			info = cu.fetchone()
			
			info= unquote(str(info))
			info=info[3:(len(info)-3)].decode()
			#print info
		return info
	else: return ''

def GET(target, post=None):
	#print target
	try:
		req = urllib2.Request(url = target, data = post)
		req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
		#req.add_header('Host',	'online.stepashka.com')
		req.add_header('Accept', '*/*')
		req.add_header('Accept-Language', 'ru-RU')
		req.add_header('Accept-Charset', 'utf-8')
		req.add_header('Referer',	'http://serialonline.net/')
		resp = urllib2.urlopen(req)
		#CE = resp.headers.get('content-encoding')
		http = resp.read()
		#resp.close()
		return http
	except Exception, e:
		xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
		showMessage('HTTP ERROR', e, 5000)

def mainScreen(params):
	#print 'start main'
	#li = xbmcgui.ListItem('[Поиск]', addon_fanart, addon_icon)
	#li.setProperty('IsPlayable', 'false')
	#uri = construct_request({
	#	'func': 'doSearch'
	#	})
	#xbmcplugin.addDirectoryItem(hos, uri, li, True)

	http = GET(httpSiteUrl)
	#print http
	if http == None: return False
	
	beautifulSoup = BeautifulSoup(http)
	
			
	content = beautifulSoup.findAll('div', attrs={'class': 'head-bl bl-title'})
	ind=0
	for line in content:
		li = xbmcgui.ListItem(line.string, addon_fanart, addon_icon)
		li.setProperty('IsPlayable', 'false')
		#href = line['href']
		uri = construct_request({
			'href': line.string.encode('utf-8'),
			'ind':ind,
			'func': 'readCategory'
		})
		xbmcplugin.addDirectoryItem(hos, uri, li, True)
		ind=ind+1
	list= beautifulSoup.findAll('tr', attrs={'id': 'listraw'})
	cnt= len(list)
	news = beautifulSoup.findAll('div', attrs={'class': 'full_movie'})
	for new in news:
		title= '[COLOR FFFF0000]Обновления %s[/COLOR]'%new.find('h2').string.encode('utf-8')
		li = xbmcgui.ListItem(title, addon_icon, addon_icon)
		xbmcplugin.addDirectoryItem(hos, '', li)
		list= new.findAll('tr', attrs={'id': 'listraw'})
		for t in list: 
			add= t.find('td', attrs={'id': 'rightlist'}).string.encode('utf-8')
			title= '[COLOR FF00FF00]%s:[/COLOR] %s'%(t.find('a').string.encode('utf-8'),add)
			link=t.find('a')['href']
			try:
				img=get_inf_db(link)
			except:
				htt=GET(link)
				bs = BeautifulSoup(htt)
				content = bs.findAll('img', attrs={'align': 'left'})
				try:
					img=content[0]['src']
					add_to_db(link,img)
				except: pass
			li = xbmcgui.ListItem(title, img, img)
			uri = construct_request({
				'href': link,
				'func': 'readFolder'
			})
			xbmcplugin.addDirectoryItem(hos, uri, li, True,totalItems=int(cnt))
	xbmcplugin.endOfDirectory(hos)

def readCategory(params):
	#params['href']=params['href'].encode('utf-8')
	http = GET(httpSiteUrl)
	#print http
	if http == None: return False
	beautifulSoup = BeautifulSoup(http)
	content = beautifulSoup.findAll('div', attrs={'class': 'top-bl'})
	#print content
	
	pist=content[int(params['ind'])]
	dist=pist.findAll('a')
	print len(dist)
	for n in dist:
		try:
			img=get_inf_db(n['href'])
		except:
			htt=GET(n['href'])
			bs = BeautifulSoup(htt)
			content = bs.findAll('img', attrs={'align': 'left'})
			try:
				img=content[0]['src']
				add_to_db(n['href'],img)
			except: pass
		li = xbmcgui.ListItem(str(n.string), img, img)
		uri = construct_request({
			'href': n['href'],
			'img':img,
			'func': 'readFolder'
		})
		xbmcplugin.addDirectoryItem(hos, uri, li, True,totalItems=int(len(dist)))

	xbmcplugin.endOfDirectory(hos)

def readFolder(params):
	print params
	http = GET(params['href'])
	beautifulSoup = BeautifulSoup(http)
	content = beautifulSoup.findAll('div', attrs={'class': 'quote'})
	try:
		pist=content[0]
	except: pist=None
	z=None
	if pist:
		dist=pist.findAll('a')
		for n in dist:
		#print n
		#print str(n.find('b')).replace('<b>','').replace('</b>','')
			li = xbmcgui.ListItem(str(n.find('b')).replace('<b>','').replace('</b>',''), addon_fanart, addon_icon)
			uri = construct_request({
				'href': n['href'],
				'func': 'readFolder'
			})
			#print n['href']
			xbmcplugin.addDirectoryItem(hos, uri, li, True)
			z=True
	header=re.findall('<h1>[^/]+</h1>',http)[0].replace('</h1>','').replace('<h1>','').decode('cp1251').encode('utf-8')
	header='[COLOR FF00FF00]%s:[/COLOR]'%header
	
	if z:
		li = xbmcgui.ListItem(' ', addon_fanart, addon_icon)
		uri = construct_request({
			'filr': None
		})
		xbmcplugin.addDirectoryItem(hos, uri, li, False)
	
	li = xbmcgui.ListItem(header, addon_fanart, addon_icon)
	uri = construct_request({
		'filr': None
	})
	xbmcplugin.addDirectoryItem(hos, uri, li, False)

		# need to find flashvars="pl=http://serialonline.net/pl/810f6cc0b9e3e3cdd9c8557d09ac0ac2/beskontrolnye_1.txt&config=http://s
	playlist=re.findall('http://serialonline.net/pl/[0-9a-z]+/[^/]+.txt',http)
	print playlist
	fplaylist= playlist[0]
	files= GET(fplaylist)
	#print files
	flist=json.loads(files)
	for index in flist['playlist']:
		li = xbmcgui.ListItem(index['comment'], addon_fanart, addon_icon)
		li.setProperty('IsPlayable', 'true')
		uri = construct_request({
			'url': index['file'],
			'func': 'play'
		})
		
		xbmcplugin.addDirectoryItem(hos, uri, li, False)
	#li = xbmcgui.ListItem(playlist[0].split['='][1], addon_fanart, addon_icon)
	#uri = construct_request({
	#	'func': 'readFolder'
	#})
			#print n['href']
	#xbmcplugin.addDirectoryItem(hos, uri, li, True)
	xbmcplugin.setContent(hos, 'movies')
	xbmcplugin.endOfDirectory(hos)
	
def play(params):
	i = xbmcgui.ListItem(path = params['url'])
	xbmcplugin.setResolvedUrl(hos, True, i)
	
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

print 'ok'


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
