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
addon_icon    = __addon__.getAddonInfo('icon')
addon_fanart  = __addon__.getAddonInfo('fanart')
addon_path    = __addon__.getAddonInfo('path')
addon_type    = __addon__.getAddonInfo('type')
addon_id      = __addon__.getAddonInfo('id')
addon_author  = __addon__.getAddonInfo('author')
addon_name    = __addon__.getAddonInfo('name')
addon_version = __addon__.getAddonInfo('version')
ktv_folder=unicode(__addon__.getSetting('download_path'),'utf-8')
prt_file=__addon__.getSetting('port_path')
aceport=62062
cookie = ""
PLUGIN_DATA_PATH = xbmc.translatePath( os.path.join( "special://profile/addon_data", 'plugin.video.torrent.tv') )
if (sys.platform == 'win32') or (sys.platform == 'win64'):
	PLUGIN_DATA_PATH = PLUGIN_DATA_PATH.decode('utf-8')
PROGRAM_SOURCE_PATH = os.path.join( PLUGIN_DATA_PATH , "%s_inter-tv.zip"  % datetime.date.today().strftime("%W") )
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

while not __addon__.getSetting('download_path'): __addon__.openSettings()
ktv_folder=unicode(__addon__.getSetting('download_path'),'utf-8')
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
		
def showMessage(heading, message, times = 3000, pics = addon_icon):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
	except Exception, e:
		xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )

def Log(str):
	import datetime
	output = open(PLUGIN_DATA_PATH + '/log.txt', 'a')
	output.write('%s: %s\r\n' % (datetime.datetime.now(), str))
	output.close()
	
def GetScript(params):
	try:
		xbmc.executebuiltin( "ActivateWindow(%d)" % ( 10147 ) ) 
		window = xbmcgui.Window( 10147 )
		if not os.path.exists(PROGRAM_SOURCE_PATH):
			gzip = GET('http://www.teleguide.info/download/new3/inter-tv.zip')
			output = open(PROGRAM_SOURCE_PATH, 'wb')
			output.write(gzip)
			output.close()
		import zipfile
		gzipFile = zipfile.ZipFile(PROGRAM_SOURCE_PATH)
		PROGRAM_FILE = gzipFile.read('inter-tv.txt').decode('windows-1251', 'strict')
		import datetime
		today = datetime.date.today()
		strToDay = ''
		if (today.weekday() == 0):
			strToDay = strToDay + 'ПОНЕДЕЛЬНИК. '
		elif (today.weekday() == 1):
			strToDay = strToDay + 'ВТОРНИК. '
		elif (today.weekday() == 2):
			strToDay = strToDay + 'СРЕДА. '
		elif (today.weekday() == 3):
			strToDay = strToDay + 'ЧЕТВЕРГ. '
		elif (today.weekday() == 4):
			strToDay = strToDay + 'ПЯТНИЦА. '
		elif (today.weekday() == 5):
			strToDay = strToDay + 'СУББОТА. '
		elif (today.weekday() == 6):
			strToDay = strToDay + 'ВОСКРЕСЕНЬЕ. '

		strToDay = strToDay + '%.2d ' % today.day
		if today.month == 1:
			strToDay = strToDay + 'Январь. '
		elif today.month == 2:
			strToDay = strToDay + 'Февраль. '
		elif today.month == 3:
			strToDay = strToDay + 'Март. '
		elif today.month == 4:
			strToDay = strToDay + 'Апрель. '
		elif today.month == 5:
			strToDay = strToDay + 'Май. '
		elif today.month == 6:
			strToDay = strToDay + 'Июнь. '
		elif today.month == 7:
			strToDay = strToDay + 'Июль. '
		elif today.month == 8:
			strToDay = strToDay + 'Август. '
		elif today.month == 9:
			strToDay = strToDay + 'Сентябрь. '
		elif today.month == 10:
			strToDay = strToDay + 'Октябрь. '
		elif today.month == 11:
			strToDay = strToDay + 'Ноябрь. '
		elif today.month == 12:
			strToDay = strToDay + 'Декабрь. '
		
		txtProgram = ''
		i = 0
		j = 0
		isProgram = -1
		header = ''
		selTime = False
		lastTime = 0
		import time
		locTime = time.localtime()
		curTime = time.strptime('%.2d:%.2d' % (locTime.tm_hour, locTime.tm_min), '%H:%M')
		strs = []
		lines = PROGRAM_FILE.expandtabs().splitlines()
		txtProgram = ''
		isProgram = -1
		for line in lines[2:]:
			if line.encode('utf-8').find(strToDay + params['title']) == 0:
				isProgram = 1
				header = line
				continue
		
			if len(line) < 3 and isProgram > 0:
				isProgram -= 1
				continue
			elif len(line) < 3 and isProgram == 0:
				break
			elif isProgram != -1:
				strs.append(line)
				if not selTime:
					i += 1
					try:
						stime = line[0:5].replace(' ', '')
						j += 1
						bufj = j
						if (stime <> ''):
							ptime = time.strptime(stime, '%H:%M')
							j = 0
							if ptime <= curTime:
								lastTime = i
							else:
								selTime = True
								j = bufj
							
					except Exception, e:
						xbmc.log( 'Error [GetScript] %s : %s' % (e, stime))
						showMessage('Error', 'Ошибка конвертации времени')
		for line in strs[i-j-1:]:
			txtProgram = txtProgram + line + '\r\n'
		if txtProgram == '':
			header = params['title']
			txtProgram = '[COLOR FFFF0000]Нет программы[/COLOR]'.decode('utf-8')
		window.getControl(1).setLabel(header)
		text = '%s' % txtProgram
		window.getControl(5).setText(text)
		gzipFile.close()
	except Exception, e:
		xbmc.log( 'Error [GetScript] %s' % (e))
		showMessage('Error', e, 6000)
		
def GetChanels (params):
	http = GET('http://torrent-tv.ru/' + params['file'])
	beautifulSoup = BeautifulSoup(http)
	channels=beautifulSoup.findAll('div', attrs={'class': 'best-channels-content'})
	for ch in channels:
		link =ch.find('a')['href']
		title= ch.find('strong').string.encode('utf-8').replace('\n', '')
		img='http://torrent-tv.ru/'+ch.find('img')['src']
		li = li = xbmcgui.ListItem(title,title,img,img)
		uri = construct_request({
				'func': 'play_ch',
				'img':img,
				'title':title,
				'file':link
			})
		try:
			li.addContextMenuItems([('Телепрограмма', 'XBMC.RunPlugin(%s?func=GetScript&title=%s)' % (sys.argv[0], title),)])
		except Exception, e:
			xbmc.log( 'Error [GetChanels] %s' % (e))
			showMessage('Erorr', e)
			break
			
		xbmcplugin.addDirectoryItem(hos, uri, li)
	xbmcplugin.endOfDirectory(hos)
	
def play_ch(params):
	http = GET('http://torrent-tv.ru/'+params['file'])
	print 'http://torrent-tv.ru/'+params['file']
	beautifulSoup = BeautifulSoup(http)
	tget= beautifulSoup.find('div', attrs={'class':'tv-player-wrapper'})
	print tget
	
	m=re.search('http:(.+)"', str(tget))
	if m:
		torr_link= m.group(0).split('"')[0]
		m=re.search('http://[0-9]+.[0-9]+.[0-9]+.[0-9]+:[0-9]+', torr_link)
		try:
			pre_link= m.group(0)
			http = GET(pre_link)
			beautifulSoup = BeautifulSoup(http)
			lnk=pre_link+beautifulSoup.find('a')['href']
			torr_link=lnk
		except: pass
		TSplayer=tsengine()
		out=TSplayer.load_torrent(torr_link,'TORRENT',port=aceport)
		if out=='Ok':
			TSplayer.play_url_ind(0,params['title'],addon_icon,params['img'])
		TSplayer.end()
		showMessage('Torrent', 'Stop', 2000)
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
			showMessage('Torrent', e)
		showMessage('Torrent', 'Stop', 2000)
	
def GetParts() :
	http = GET('http://torrent-tv.ru/channels.php')
	beautifulSoup = BeautifulSoup(http)
	parts = beautifulSoup.findAll('a', attrs={'class': 'simple-link'})
	i = 0
	for ch in parts:
		link = ch['href'].find('category')
		if link > -1:
			li = xbmcgui.ListItem(ch.string)
			uri = construct_request({
			'func' : 'GetChanels',
			'title' : ch.string,
			'file' : ch['href']
			})
			xbmcplugin.addDirectoryItem(hos, uri, li, True)
			
def mainScreen(params):
	li = xbmcgui.ListItem('[COLOR FF00FF00]Все каналы[/COLOR]')
	uri = construct_request({
		'func': 'GetChanels',
		'title': 'Все каналы',
		'file': 'channels.php'
	})
	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	li = xbmcgui.ListItem('[COLOR FF00FF00]На модерации[/COLOR]')
	uri = construct_request({
		'func': 'GetChanels',
		'title': 'На модерации',
		'file': 'on_moderation.php'
	})
	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	li = xbmcgui.ListItem('[COLOR FF00FF00]Трансляции[/COLOR]')
	uri = construct_request({
		'func': 'GetChanels',
		'title': 'Трансляции',
		'file': 'translations.php'
	})
	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	li = xbmcgui.ListItem('[COLOR FF00FF00]HD Каналы[/COLOR]')
	uri = construct_request({
		'func': 'GetChanels',
		'title': 'HD Каналы',
		'file': 'hd_channels.php'
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

login = __addon__.getSetting("login")
passw = __addon__.getSetting("password")
data = urllib.urlencode({
	'email' : login,
	'password' : passw,
	'remember' : 1,
	'enter' : 'enter'
})

def addon_main():
	page = GET('http://torrent-tv.ru/auth.php', data)
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
