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
__addon__ = xbmcaddon.Addon( id = 'plugin.video.raketa.tv' )
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
PLUGIN_DATA_PATH = xbmc.translatePath( os.path.join( "special://profile/addon_data", 'plugin.video.raketa.tv') )
if (sys.platform == 'win32') or (sys.platform == 'win64'):
	PLUGIN_DATA_PATH = PLUGIN_DATA_PATH.decode('utf-8')

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

# JSON понадобится, когда будет несколько файлов в торренте
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

def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))
	
def GET(target, post=None):
	try:
		req = urllib2.Request(url = target, data = post)
		req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
		resp = urllib2.urlopen(req)

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
		
def play_ch(params):
	try:
		m=params['file'].find('http:')
		if m == 0:
			TSplayer=tsengine()
			out=TSplayer.load_torrent(params['file'],'TORRENT',port=aceport)
			if out=='Ok':
				TSplayer.play_url_ind(0,params['title'],addon_icon,params['img'])
			TSplayer.end()
			showMessage('Torrent', 'Stop', 2000)
		else:
			ID = params['file']
			try:
				TSplayer=tsengine()
				out=TSplayer.load_torrent(ID,'PID',port=aceport)
				if out=='Ok':
					TSplayer.play_url_ind(0,params['title'],addon_icon,params['img'])
				TSplayer.end()
			except Exception, e:
				showMessage('Torrent', e)
			showMessage('Torrent', 'Stop', 2000)
	except Exception, e:
			showMessage('Raketa TV', e)

def GetJsonChannels(params, new = False):
	data = ''
	try:
		if not new:
			if os.path.exists(PLUGIN_DATA_PATH + '/channels_list.json'):
				output = open(PLUGIN_DATA_PATH + '/channels_list.json', 'r')
				data = json.loads(output.read())
				output.close()
				return data
		
		output = open('%s/channels_list.json' % PLUGIN_DATA_PATH, 'w')
		data = GET('http://raketa-tv.com/player/JSON/channels_list.json');
		output.write(data)
		output.close()
		data = json.loads(data)
		
	except Exception, e:
		showMessage('Error', e, 10000)
	return data

def GetProgram(param):
	if param['id'] == '':
		return
	curDay = datetime.date.today().strftime("%d");
	if not os.path.exists(PLUGIN_DATA_PATH + '/%s_program_list.json' % curDay):
		import glob
		filelist = glob.glob(PLUGIN_DATA_PATH + "/*_program_list.json")
		for f in filelist:
			os.remove(f)
		output = open(PLUGIN_DATA_PATH + '/%s_program_list.json' % curDay, 'w')
		output.write(GET('http://raketa-tv.com/player/JSON/program_list.json'))
		output.close()

	try:
		import time
		xbmc.executebuiltin( "ActivateWindow(%d)" % ( 10147 ) ) 
		window = xbmcgui.Window( 10147 )
		input = open(PLUGIN_DATA_PATH + '/program_list.json', 'r')
		data = input.read().encode('utf-8')
		data = json.loads(data)
		txtProgram = ''
		program = filter(lambda x: x['channel_number'] == param['id'], data)[0]
		for chanel in program['program']:
			startTime = time.localtime(float(chanel['ut_start']))
			endTime = time.localtime(float(chanel['ut_stop']))
			curTime = time.localtime()
			if (endTime > curTime):
				txtProgram = txtProgram + '%.2d:%.2d - %.2d:%.2d: %s\n' % (startTime.tm_hour, startTime.tm_min, endTime.tm_hour, endTime.tm_min, chanel['title'])
		window.getControl(5).setText(txtProgram)
		window.getControl(1).setLabel(param['title'])
	except Exception, e:
		showMessage('Error', e, 5000)

def GetChanels (params):
	data = GetJsonChannels('', False)
	if params['id'] != '203':
		data = filter(lambda x: x['category_id'] == params['id'], data['channels'])
		for chanel in data:
			li = xbmcgui.ListItem('%s' % chanel['title'], chanel['title'], chanel['icon'])
			uri = construct_request({
				'func': 'play_ch',
				'img': chanel['icon'].encode('utf-8'),
				'title': chanel['title'].encode('utf-8'),
				'file': base64.urlsafe_b64decode(chanel['id'].replace('?', 'L').replace('|', 'M').encode('utf-8'))
			})
			li.addContextMenuItems([('Телепрограмма', 'XBMC.RunPlugin(%s?func=GetProgram&id=%s&title=%s)' % (sys.argv[0], chanel['number'], chanel['title']),)])
			xbmcplugin.addDirectoryItem(hos, uri, li, False)
	else:
		data = filter(lambda x: x['hd'] == "1", data['channels'])
		for chanel in data:
			li = xbmcgui.ListItem('%s' % chanel['title'], chanel['title'], chanel['icon'])
			uri = construct_request({
				'func': 'play_ch',
				'img': chanel['icon'].encode('utf-8'),
				'title': chanel['title'].encode('utf-8'),
				'file': base64.urlsafe_b64decode(chanel['id'].replace('?', 'L').replace('|', 'M').encode('utf-8'))
			})
			li.addContextMenuItems([('Телепрограмма', 'XBMC.RunPlugin(%s?func=GetProgram&id=%s)' % (sys.argv[0], chanel['number']),)])
			xbmcplugin.addDirectoryItem(hos, uri, li, False)
			
			
	xbmcplugin.endOfDirectory(hos)

def mainScreen(params):
	try:
		data = GetJsonChannels('', True)
		for group in data['types']:
			pass
			li = xbmcgui.ListItem('%s' % group['title'], group['title'])
			uri = construct_request({
				'func' : 'GetChanels',
				'title' : group['title'].encode('utf-8'),
				'id' : group['id']
			})
			xbmcplugin.addDirectoryItem(hos, uri, li, True)
		xbmcplugin.endOfDirectory(hos)
	except Exception, e:
		showMessage('Raketa-TV', e)
	
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
