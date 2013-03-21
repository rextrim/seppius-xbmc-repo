#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib
import urllib
import urllib2
import re
import sys
import os
import socket
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
import xbmcaddon
import datetime
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from TSCore import TSengine as tsengine
import base64

hos = int(sys.argv[1])
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
__addon__ = xbmcaddon.Addon( id = 'plugin.video.torrent.tv' )
__language__ = __addon__.getLocalizedString
addon_icon	 = __addon__.getAddonInfo('icon')
addon_fanart  = __addon__.getAddonInfo('fanart')
addon_path	 = __addon__.getAddonInfo('path')
addon_type	 = __addon__.getAddonInfo('type')
addon_id		= __addon__.getAddonInfo('id')
addon_author  = __addon__.getAddonInfo('author')
addon_name	 = __addon__.getAddonInfo('name')
addon_version = __addon__.getAddonInfo('version')
prt_file=__addon__.getSetting('port_path')
adult = __addon__.getSetting('adult')
aceport=62062
cookie = ""
PLUGIN_DATA_PATH = xbmc.translatePath( os.path.join( "special://profile/addon_data", 'plugin.video.torrent.tv') )

if (sys.platform == 'win32') or (sys.platform == 'win64'):
	PLUGIN_DATA_PATH = PLUGIN_DATA_PATH.decode('utf-8')
	
PROGRAM_SOURCE_PATH = os.path.join( PLUGIN_DATA_PATH , "%s_inter-tv.zip"  % datetime.date.today().strftime("%W") )
	
xbmcplugin.setContent(int(sys.argv[1]), 'movies')

try:
	if prt_file:  
		gf = open(prt_file, 'r')
		aceport=int(gf.read())
		gf.close()
except: prt_file=None
if not prt_file:
	try:
		fpath= os.path.expanduser("~")
		pfile= os.path.join(fpath,'AppData\Roaming\TorrentStream\engine' ,'acestream.port')
		gf = open(pfile, 'r')
		aceport=int(gf.read())
		gf.close()
		__addon__.setSetting('port_path',pfile)
		print aceport
	except: aceport=62062

def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))
	
def GET(target, post=None):
	try:
		req = urllib2.Request(url = target, data = post)
		req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
		global cookie
		if cookie != "":
			req.add_header('Cookie', cookie)
			
		resp = urllib2.urlopen(req)
		if cookie == "":
			cookie = resp.headers['Set-Cookie'].split(";")[0]
			
		http = resp.read()
		resp.close()
		return http
	except Exception, e:
		xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
		showMessage('HTTP ERROR', e, 5000)
		
def showMessage(heading='Torrent-TV.RU', message = '', times = 3000, pics = addon_icon):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
	except Exception, e:
		xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )

db_name = os.path.join(PLUGIN_DATA_PATH, 'tvbase.db')

def GetScript(params):
	import time
	xbmc.executebuiltin( "ActivateWindow(%d)" % ( 10147 ) )
	window = xbmcgui.Window( 10147 )

	db = DataBase(db_name, cookie)
	sch = None
	if params.has_key('id'):
		try:
			sch = db.GetSchedules(params['id'])
		except:
			showMessage(message = 'Программа загружается')
			xbmc.sleep(2000)
			GetScript(params)
			return
	else:
		del db
		return
	del db
	
	for ch in sch:
		txtProgram = ''
		if not ch.has_key('program'):
			xbmc.sleep(13)
			window.getControl(1).setLabel(params['title'])
			window.getControl(5).setText('Нет программы')
			return
		for item in ch['program']:
			startTime = time.localtime(float(item['start']))
			endTime = time.localtime(float(item['end']))
			txtProgram = txtProgram + '%.2d:%.2d - %.2d:%.2d: %s\n' % (startTime.tm_hour, startTime.tm_min, endTime.tm_hour, endTime.tm_min, item['title'])
		
		xbmc.sleep(13)
		window.getControl(1).setLabel(ch['name'])
		window.getControl(5).setText(txtProgram)
	
	
		
def GetChannelsDB (params):
	db = DataBase(db_name, cookie)
	channels = None
	if not params.has_key('group'):
		return
	elif params['group'] == '0':
		channels = db.GetChannels(adult = adult)
	elif params['group'] == 'hd':
		channels = db.GetChannelsHD(adult = adult)
	elif params['group'] == 'latest':
		channels = db.GetLatestChannels(adult = adult)
	elif params['group'] == 'new':
		channels = db.GetNewChannels(adult = adult)
	else:
		channels = db.GetChannels(params['group'], adult = adult)
	import time
	for ch in channels:
		img = ch['imgurl']
		if __addon__.getSetting('logopack') == 'true':
			logo_path = os.path.join(PLUGIN_DATA_PATH, 'logo')
			logo_src = os.path.join(logo_path, ch['name'].decode('utf-8') + '.png')
			if os.path.exists(logo_src):
				img = logo_src
		try:
			sch = db.GetSchedules(ch['id'], 6, int(time.time()))
		except:
			GetChannelsDB(params)
			return
		if sch[0].has_key('program'):
			startTime = time.localtime(float(sch[0]['program'][0]['start']))
			endTime = time.localtime(float(sch[0]['program'][0]['end']))
			title = '%s [COLOR FF0091E7]%.2d:%.2d - %.2d:%.2d: %s[/COLOR]' % (ch['name'], startTime.tm_hour, startTime.tm_min, endTime.tm_hour, endTime.tm_min, sch[0]['program'][0]['title'].encode('utf-8'))
		else:
			title = ch['name']
		if params['group'] == '0' or params['group'] == 'hd' or params['group'] == 'latest' or params['group'] == 'new':
			title = '[COLOR FF7092BE]%s:[/COLOR] %s' % (ch['group_name'], title)
		li = xbmcgui.ListItem(title, title, img, img)
		if sch[0].has_key('program'):
			prog = ''
			for item in sch[0]['program']:
				startTime = time.localtime(float(item['start']))
				endTime = time.localtime(item['end'])
				prog = prog + '%.2d:%.2d - %.2d:%.2d: %s\n' % (startTime.tm_hour, startTime.tm_min, endTime.tm_hour, endTime.tm_min, item['title'].encode('utf-8'))
				li.setInfo(type = "Video", infoLabels = {"Title": ch['name'], 'year': endTime.tm_year, 'genre': ch['group_name'], 'plot': '%s' % prog} )
		else:
			li.setInfo(type = "Video", infoLabels = {"Title": ch['name'], 'year': time.localtime().tm_year, 'genre': ch['group_name']})
		uri = construct_request({
			'func': 'play_ch_db',
			'img': img.encode('utf-8'),
			'title': ch['name'],
			'file': ch['urlstream'],
			'id': ch['id']
		})
		deluri = construct_request({
			'func': 'DelChannel',
			'id': ch['id']
		})
		commands = []
		commands.append(('Телепрограмма', 'XBMC.RunPlugin(%s?func=GetScript&id=%s&title=%s)' % (sys.argv[0], ch['id'], ch['name']),))
		commands.append(('Удалить канал', 'XBMC.RunPlugin(%s)' % (deluri),))
		li.addContextMenuItems(commands)
		xbmcplugin.addDirectoryItem(hos, uri, li)
	xbmcplugin.endOfDirectory(hos)
	del db
	
def DelChannel(params):
	db = DataBase(db_name, cookie)
	db.DelChannel(params['id'])
	showMessage(message = 'Канал удален')
	xbmc.executebuiltin("Container.Refresh")
	del db
	
def GetChannelsWeb(params):
	http = GET('http://torrent-tv.ru/' + params['file'])
	beautifulSoup = BeautifulSoup(http)
	channels=beautifulSoup.findAll('div', attrs={'class': 'best-channels-content'})
	for ch in channels:
		link =ch.find('a')['href']
		title= ch.find('strong').string.encode('utf-8').replace('\n', '')
		img='http://torrent-tv.ru/'+ch.find('img')['src']
		
		if __addon__.getSetting('logopack'):
			logo_path = os.path.join(PLUGIN_DATA_PATH, 'logo')
			logo_src = os.path.join(logo_path, ch.find('strong').string.replace('\n', '').replace('  ', '') + '.png')
			if os.path.exists(logo_src):
				img = logo_src.encode('utf-8')
				
		li = xbmcgui.ListItem(title,title,img,img)
		uri = construct_request({
				'func': 'play_ch_web',
				'img':img,
				'title':title,
				'file':link
			})
			
		xbmcplugin.addDirectoryItem(hos, uri, li)
	xbmcplugin.endOfDirectory(hos)

def play_ch_db(params):
	url = ''
	if params['file'] == '':
		db = DataBase(db_name, cookie)
		url = db.UpdateUrlsStream([params['id']])
		if url.__len__() == 0:
			return
		url = url[0]['urlstream']
		del db
	else:
		url = params['file']
	if url != '':
		TSPlayer = tsengine()
		out = None
		if url.find('http://') == -1:
			out = TSPlayer.load_torrent(url,'PID',port=aceport)
		else:
			out = TSPlayer.load_torrent(url,'TORRENT',port=aceport)
		if out == 'Ok':
			TSPlayer.play_url_ind(0,params['title'],addon_icon,params['img'])
			db = DataBase(db_name, cookie)
			db.IncChannel(params['id'])
			del db
		TSPlayer.end()
		showMessage('Torrent', 'Stop')
	
def play_ch_web(params):
	http = GET('http://torrent-tv.ru/'+params['file'])
	print 'http://torrent-tv.ru/'+params['file']
	beautifulSoup = BeautifulSoup(http)
	tget= beautifulSoup.find('div', attrs={'class':'tv-player'})
	
	m=re.search('http:(.+)"', str(tget))
	if m:
		torr_link= m.group(0).split('"')[0]
		m=re.search('http://[0-9]+.[0-9]+.[0-9]+.[0-9]+:[0-9]+', torr_link)
		TSplayer=tsengine()
		out=TSplayer.load_torrent(torr_link,'TORRENT',port=aceport)
		if out=='Ok':
			TSplayer.play_url_ind(0,params['title'],addon_icon,params['img'])
		TSplayer.end()
		showMessage(message = 'Stop')
	else:
		m = re.search('load.*', str(tget))
		ID = m.group(0).split('"')[1]
		try:
			TSplayer=tsengine()
			out=TSplayer.load_torrent(ID,'PID',port=aceport)
			if out=='Ok':
				TSplayer.play_url_ind(0,params['title'],addon_icon,params['img'])
			TSplayer.end()
		except Exception, e:
			showMessage(message = e)
		showMessage(message = 'Stop')

def GetParts():
	db = DataBase(db_name, cookie)
	parts = db.GetParts(adult = adult)
		
	for part in parts:
		li = xbmcgui.ListItem(part['name'])
		uri = construct_request({
			'func': 'GetChannelsDB',
			'group': part['id'],
		})
		xbmcplugin.addDirectoryItem(hos, uri, li, True)

def mainScreen(params):
	li = xbmcgui.ListItem('[COLOR FF00FF00]Все каналы[/COLOR]')
	uri = construct_request({
		'func': 'GetChannelsDB',
		'title': 'Все каналы',
		'group': '0'
	})
	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	li = xbmcgui.ListItem('[COLOR FF00FF00]Последние просмотренные[/COLOR]')
	uri = construct_request({
		'func': 'GetChannelsDB',
		'title': 'Последние просмотренные',
		'group': 'latest'
	})
	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	li = xbmcgui.ListItem('[COLOR FF00FF00]HD Каналы[/COLOR]')
	uri = construct_request({
		'func': 'GetChannelsDB',
		'title': 'HD Каналы',
		'group': 'hd'
	})
	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	li = xbmcgui.ListItem('[COLOR FF00FF00]Новые каналы[/COLOR]')
	uri = construct_request({
		'func': 'GetChannelsDB',
		'title': 'Новые каналы',
		'group': 'new'
	})
	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	li = xbmcgui.ListItem('[COLOR FF0099FF]На модерации[/COLOR]')
	uri = construct_request({
		'func': 'GetChannelsWeb',
		'title': 'На модерации',
		'file': 'on_moderation.php'
	})
	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	li = xbmcgui.ListItem('[COLOR FF0099FF]Трансляции[/COLOR]')
	uri = construct_request({
		'func': 'GetChannelsWeb',
		'title': 'Трансляции',
		'file': 'translations.php'
	})

	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	GetParts()
	xbmcplugin.endOfDirectory(hos)
	
from urllib import unquote, quote, quote_plus
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
	
from database import DataBase

cookiefile = os.path.join(PLUGIN_DATA_PATH, 'cookie.txt')
if os.path.exists(cookiefile):
	fgetcook = open(cookiefile, 'r')
	cookie = fgetcook.read()
	del fgetcook

db = DataBase(db_name, cookie)		
dbver = db.GetDBVer()
if db.GetDBVer() <> 5:
	del db
	os.remove(db_name)

db = DataBase(db_name, cookie)
lupd = db.GetLastUpdate()
if lupd == None:
	showMessage('Torrent TV', 'Производится обновление плэйлиста')
	db.UpdateDB()
else:
	nupd = lupd + datetime.timedelta(hours = 7)
	#nupd = lupd
	#showMessage(message = '%s - %s' % (nupd, lupd), times = 5000)
	if nupd < datetime.datetime.now():
		showMessage('Torrent TV', 'Производится обновление плэйлиста')
		db.UpdateDB()
del db

def addon_main():
	params = get_params(sys.argv[2])
	try:
		func = params['func']
		del params['func']
	except:
		login = __addon__.getSetting("login")
		passw = __addon__.getSetting("password")
		data = urllib.urlencode({
			'email' : login,
			'password' : passw,
			'remember' : 1,
			'enter' : 'enter'
		})

		if not os.path.exists(PLUGIN_DATA_PATH):
			os.makedirs(PLUGIN_DATA_PATH)
		if os.path.exists(cookiefile):
			os.remove(cookiefile)
		out = open(cookiefile, 'w')
		GET('http://torrent-tv.ru/auth.php', data)
		out.write(cookie)
		out.close()
		
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
