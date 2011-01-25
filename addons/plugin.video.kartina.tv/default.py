#!/usr/bin/python
#/*
# *      Copyright (C) 2010-2011 Eugene Bond
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# */

import xbmcaddon, string, xbmc, xbmcgui, xbmcplugin, os
sys.path.append(os.path.join(os.getcwd(), 'resources', 'lib'))
import iptv

import datetime, time
import urllib

PLUGIN_ID = 'plugin.video.kartina.tv'
__settings__ = xbmcaddon.Addon(id=PLUGIN_ID)
__language__ = __settings__.getLocalizedString
USERNAME = __settings__.getSetting('username')
USERPASS = __settings__.getSetting('password')
handle = int(sys.argv[1])

PLUGIN_NAME = 'Kartina.TV'
PLUGIN_CORE = None
TRANSSID = ''
thumb = os.path.join( os.getcwd(), "icon.png" )

def get_params():
	param=[]
	paramstring=sys.argv[2]
	xbmc.output('[%s] parsing params from %s' % (PLUGIN_NAME, paramstring))
	if len(paramstring)>=2:
		params=sys.argv[2]
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


def Archive(plugin, id, params):
	
	uri = sys.argv[0]
	
	in_arch = False
	
	dt = None
	if 'dt' in params:
		dt = datetime.datetime.fromordinal(int(params['dt']))
		in_arch = True
	
	if not dt:
		dt = datetime.datetime.today()
	
	epg = plugin.getEPG(id, dt.strftime('%d%m%y'))
	
	xbmc.output('[%s] Archive/EPG: fetching EPG from %s as %s' % (PLUGIN_NAME, id, epg))
	
	day_ago = datetime.datetime.fromordinal(int(dt.toordinal())-1)
	goback_title = '[B][ %s ][/B]' % (day_ago.strftime('%a, %d %B'))
	goback = xbmcgui.ListItem(goback_title)
	goback.setLabel(goback_title)
	goback.setProperty('IsPlayable', 'false')
	goback.setInfo( type='video', infoLabels={'title': goback_title, 'plot': __language__(30007)})
	uri = sys.argv[0] + '?mode=Archive&channel=%s&dt=%s&can_play=%s' % (id, day_ago.toordinal(), params['can_play'])
	xbmc.output(uri) 
	xbmcplugin.addDirectoryItem(handle,uri,goback,True)
	currentProg = False
	
	counter = 0
	for prog in epg:
		counter = counter + 1
		progStart = int(prog['time'])
		timeLabel = datetime.datetime.fromtimestamp(progStart + plugin.timeshift).strftime('%H:%M')
		can_play = params['can_play']
		
		if can_play:
			if progStart > time.time():
				can_play = False
		
		title = '%s %s %s' % (timeLabel, prog['title'], prog['info'])
		
		if progStart < time.time():
			if currentProg == False:
				if len(epg) > counter:
					p = epg[counter]
					if int(p['time']) > time.time():
						title = '[B][COLOR green]%s[/COLOR][/B]' % title
						currentProg = counter
			pass
		else:
			title = '[I]%s[/I]' % title
		
		item=xbmcgui.ListItem(title)
		item.setLabel(title)
		item.setLabel2(prog['info'])
		item.setInfo( type='video', infoLabels={'title': prog['title'], 'plot': prog['info']})
		uri = ''
		
		if can_play:
			item.setProperty('IsPlayable', 'true')
			item.setIconImage(os.path.join(os.getcwd(), 'resources', 'icons', 'play.png'))
			uri = sys.argv[0] + '?mode=WatchTV&channel=%s&title=%s&ts=%s' % (id, prog['title'], prog['source']['ut_start']) 
		else:
			item.setIconImage(os.path.join(os.getcwd(), 'resources', 'icons', 'play-stop.png'))
			item.setProperty('IsPlayable', 'false')
		
		xbmcplugin.addDirectoryItem(handle,uri,item,False)
	
	
	day_forward = datetime.datetime.fromordinal(int(dt.toordinal())+1)
	goahead_title = '[B][ %s ][/B]' % (day_forward.strftime('%a, %d %B'))
	goahead = xbmcgui.ListItem(goahead_title)
	goahead.setLabel(goahead_title)
	goahead.setProperty('IsPlayable', 'false')
	goahead.setInfo( type='video', infoLabels={'title': goahead_title, 'plot': __language__(30008)})
	uri = sys.argv[0] + '?mode=Archive&channel=%s&dt=%s&can_play=%s' % (id, day_forward.toordinal(), params['can_play'])
	xbmc.output(uri) 
	xbmcplugin.addDirectoryItem(handle,uri,goahead,True)
	
	xbmcplugin.endOfDirectory(handle, True, in_arch)
	xbmc.executebuiltin( "Container.SetViewMode(51)")
	

def resetAlarms(plugin, mode):
	refreshAlarmId = '%s_refresh_list' % PLUGIN_ID
	xbmc.executebuiltin("XBMC.CancelAlarm(%s,True)" % refreshAlarmId)
	

def ShowChannelsList(plugin):
	refreshAlarmId = '%s_refresh_list' % PLUGIN_ID
	
	channels = plugin.getChannelsList()
	counter = 0
	for channel in channels:
		if __settings__.getSetting('show_protected') == 'false':
			if channel['is_protected']:
				continue
		 
		if channel['is_video']:
			uri = sys.argv[0] + '?mode=WatchTV&channel=%s&title=%s' % (channel['id'], channel['title'])
			if channel['is_protected']:
				uri = '%s&code=%s' % (uri, __settings__.getSetting('protected_code'))
				overlay = 3
			else:
				if channel['have_archive']:
					overlay = 1
				else:
					overlay = 0
			
			item=xbmcgui.ListItem(channel['subtitle'], channel['title'], iconImage=channel['icon'], thumbnailImage=channel['icon'])
			color = channel['color']
			
			if channel['duration']:
				played = ' [%s%%]' % channel['percent']
			else:
				played = ''
			
			label = '[B] [COLOR %s]%s[/COLOR].%s[/B] %s %s' % (color, channel['title'], played, channel['subtitle'], channel['info'])
			item.setLabel(label)			
 			item.setIconImage(channel['icon'])
			item.setInfo( type='video', infoLabels={'title': channel['subtitle'], 'plot': channel['info'], 'genre': channel['genre'], 'duration': str(channel['duration']),  'overlay': overlay})
			
			item.setProperty('IsPlayable', 'true')
			popup = []
			
			if channel['have_epg'] != False:
				archive_text = __language__(30006)
				if channel['have_archive']:
					archive_text = __language__(30011)
				
				uri2 = sys.argv[0] + '?mode=Archive&channel=%s&can_play=%s' % (channel['id'], channel['have_archive'])
				popup.append((archive_text, 'XBMC.Container.Update(%s)'%uri2,))
			
			popup.append((__language__(30021), 'Container.Refresh',))
			
			if __settings__.getSetting('start_with_tv') == 'true':
				uriP = 'XBMC.Container.Update(%s)' % (sys.argv[0] + '?mode=%s')
				popup.append((__language__(30016), uriP % 'Video',))
				popup.append((__language__(30004), uriP % 'Settings',))
			
			item.addContextMenuItems(popup, True)
			
			xbmcplugin.addDirectoryItem(handle,uri,item, False)
			counter = counter + 1
	
	refresh_rate = int(__settings__.getSetting('autorefresh_rate'))
	
	xbmcplugin.endOfDirectory(handle, cacheToDisc=(__settings__.getSetting('always_refresh') == 'false'))
	
	if refresh_rate > 0:
		xbmc.executebuiltin("XBMC.AlarmClock(%s,XBMC.Container.Refresh,%s,True)" % (refreshAlarmId, refresh_rate))
	xbmc.executebuiltin( "Container.SetViewMode(51)")


def Video(plugin, params):
	if 'mode' in params:
		mode = params['mode']
	else:
		mode = 'last'
	
	if 'page' in params:
		page = int(params['page'])
		if page < 1:
			page = 1
	else:
		page = 1
	
	
	
	if page > 1:
		goback_title = '[ %s ]' % __language__(30019)
		goback = xbmcgui.ListItem(goback_title)
		goback.setLabel(goback_title)
		goback.setProperty('IsPlayable', 'false')
		goback.setInfo( type='video', infoLabels={'title': goback_title})
		uri = sys.argv[0] + '?mode=Video&mode=%s&page=%d' % (mode, page-1)
		xbmc.output(uri) 
		xbmcplugin.addDirectoryItem(handle,uri,goback,True)
	
	
	vlist = plugin.getVideoList(mode, page)
	
	for film in vlist:
		title = film['title']
		item=xbmcgui.ListItem(title, title, iconImage=film['icon'], thumbnailImage=film['icon'])
		item.setLabel(title)
		item.setIconImage(film['icon'])
		item.setLabel2(film['info'])
		item.setInfo( type='video', infoLabels={'title': title, 'plot': film['info']})
		uri = sys.argv[0] + '?mode=VideoInfo&vod=%s' % film['id']
		item.setProperty('IsPlayable', 'true')
		xbmcplugin.addDirectoryItem(handle,uri,item,True)
	
	
	goahead_title = '[ %s ]' % __language__(30018)
	goahead = xbmcgui.ListItem(goahead_title)
	goahead.setLabel(goahead_title)
	goahead.setProperty('IsPlayable', 'false')
	goahead.setInfo( type='video', infoLabels={'title': goahead_title})
	uri = sys.argv[0] + '?mode=Video&mode=%s&page=%d' % (mode, page+1)
	xbmc.output(uri) 
	xbmcplugin.addDirectoryItem(handle,uri,goahead,True)
	
	xbmcplugin.endOfDirectory(handle,True,False)

def VideoInfo(plugin, params):
	vid = params['vod']
	film = plugin.getVideoInfo(vid)
	
	for video in film['videos']:
		xbmc.output('[%s] VODs list item: %s' % (PLUGIN_NAME, video))
		title = video['title']
		if title == '':
			title = __language__(30017)
		
		icon = 'http://iptv.kartina.tv%s' % film['poster']
		item=xbmcgui.ListItem(title, title, iconImage=icon, thumbnailImage=icon)
		item.setLabel(title)
		item.setIconImage(icon)
		item.setLabel2(film['description'])
		item.setInfo( type='video', infoLabels={'title': title, 'plot': film['description']})
		item.setProperty('IsPlayable', 'true')
		uri = sys.argv[0] + '?mode=WatchVOD&vod=%s&title=%s' % (video['id'], film['name'] + '. ' + video['title'])
		xbmcplugin.addDirectoryItem(handle,uri,item,False)
	
	xbmcplugin.endOfDirectory(handle)

def WatchVOD(plugin, params):
	vod = params['vod']
	url = plugin.getVideoUrl(vod)
	xbmc.output('[%s] WatchVOD: Opening video %s as %s' % (PLUGIN_NAME, id, url))
	item=xbmcgui.ListItem(params['title'], path=url)
	item.setInfo( type='video', infoLabels={'title': params['title']})
	if handle == -1:
		xbmc.Player().play(url, item)		
	else:
		xbmcplugin.setResolvedUrl(handle = handle, succeeded=True, listitem=item)

def WatchTV(plugin, id, params):
	if 'ts' in params:
		gmt = params['ts']
	else:
		gmt = None
	xbmc.output('[%s] WatchTV: Timestamp is %s, adjust setting is %s' % (PLUGIN_NAME, gmt, __settings__.getSetting('ask_adjust')))
	if gmt:
		if __settings__.getSetting('ask_adjust') == 'true':
			adjust_text = __language__(30009)
			dialogus = xbmcgui.Dialog()
			adjust = dialogus.numeric(2, adjust_text, "00:00")
			xbmc.output('[%s] WatchTV: Adjusting start for %s' % (PLUGIN_NAME, adjust))
			if adjust:
				xbmc.output('[%s] WatchTV: Old ts: %s' % (PLUGIN_NAME, gmt))
				a_hours, a_mins = adjust.split(':', 1)
				
				gmt = int(gmt) + (int(a_hours) * 3600 + int(a_mins) * 60)
				xbmc.output('[%s] WatchTV: New ts: %s' % (PLUGIN_NAME, gmt))
				
	if 'code' in params:
		code = params['code']
	else:
		code = None
	
	url = plugin.getStreamUrl(id, gmt, code)
	if url:
		xbmc.output('[%s] WatchTV: Opening channel %s as %s' % (PLUGIN_NAME, id, url))
		item=xbmcgui.ListItem(params['title'], path=url)
		item.setInfo( type='video', infoLabels={'title': params['title']})
		if handle == -1:		
			player = xbmc.Player()
			xbmc.output('[%s] WatchTV: handle is -1, starting player' % (PLUGIN_NAME))
			player.play(url, item)
		else:
			xbmc.output('[%s] WatchTV: handle is %s, setting resolved url' % (PLUGIN_NAME, handle))
			xbmcplugin.setResolvedUrl(handle = handle, succeeded=True, listitem=item)
		
		if __settings__.getSetting('showcurrent') == 'true' and not gmt:
			uri = sys.argv[0] + '?mode=ShowNowNextHint&channel=%s' % (id)
			xbmc.output('[%s] WatchTV: Setting callback for hint to %s' % (PLUGIN_NAME, uri))
			xbmc.executebuiltin("RunPlugin("+uri+")")
	else:
		xbmc.executebuiltin("XBMC.Notification(" + __language__(30025).encode('utf8') + ", " + __language__(30025).encode('utf8') + ", 8000)");

def ShowRoot(plugin):
	uri = sys.argv[0] + '?mode=%s'
	
	tv_title = ' [  %s  ] ' % __language__(30012)
	tv=xbmcgui.ListItem(tv_title)
	tv.setLabel(tv_title)
	tv.setProperty('IsPlayable', 'false')
	tv.setInfo( type='video', infoLabels={'title': tv_title, 'plot': __language__(30012)})
	xbmcplugin.addDirectoryItem(handle,uri % 'TV',tv,True)
	
	vod_title = ' [  %s  ] ' % __language__(30016)
	vod = xbmcgui.ListItem(vod_title)
	vod.setLabel(vod_title)
	vod.setProperty('IsPlayable', 'false')
	vod.setInfo( type='video', infoLabels={'title': vod_title, 'plot': __language__(30016)})
	xbmcplugin.addDirectoryItem(handle,uri % 'Video',vod,True)
	
	set_title = ' [  %s  ] ' % __language__(30004)
	set = xbmcgui.ListItem(set_title)
	set.setLabel(set_title)
	set.setProperty('IsPlayable', 'false')
	set.setInfo( type='video', infoLabels={'title': set_title, 'plot': __language__(30004)})
	xbmcplugin.addDirectoryItem(handle,uri % 'Settings',set,True)
	
	set_title = ' [  %s  ] ' % __language__(30005)
	set = xbmcgui.ListItem(set_title)
	set.setLabel(set_title)
	set.setProperty('IsPlayable', 'false')
	set.setInfo( type='video', infoLabels={'title': set_title, 'plot': __language__(30005)})
	xbmcplugin.addDirectoryItem(handle,uri % 'openSettings',set,True)
	
	
	xbmcplugin.endOfDirectory(handle,True,False)

def ProcessSettings(plugin, params):
	if 'name' in params:
		value, options = plugin.getSettingCurrent(params['name'])
		dialog = xbmcgui.Dialog()
		selection = []
		for opval, opname in options:
			selection.append(opname)
  		ret = dialog.select(params['title'], selection)
  		counter = 0
  		for opval, opname in options:
  			if counter == ret:
  				plugin.setSettingCurrent(params['name'], opval)
  			counter = counter + 1
  		xbmc.executebuiltin('Container.Refresh')
  		
	else:
		settings = plugin.getSettingsList()
		
		uri = sys.argv[0] + '?mode=Settings&name=%s&title=%s'
		
		for setting in settings:
			sName = __language__(setting['language_key'])
			
			label = setting['value']
			if 'options' in setting:
				for k,v in setting['options']:
					if k == label:
						label = v
			
			sName = sName + ' (%s)' % label
			
			sItem = xbmcgui.ListItem(sName)
			sItem.setLabel(sName)
			sItem.setProperty('IsPlayable', 'false')
			sItem.setInfo( type='video', infoLabels={'title': sName, 'plot': sName})
			xbmcplugin.addDirectoryItem(handle,uri % (setting['name'], __language__(setting['language_key'])),sItem,True)
		
		xbmcplugin.endOfDirectory(handle,True,False)
	

def ShowNowNextHint(plugin, chid):
	current = plugin.getCurrentInfo(chid)
	hint = ''
	first = 1
	for prog in current:
		if first:
			first = 0
			if 'title' in prog and prog['title'] != None:
				titl =  __language__(30013)
				text = prog['title'].encode('utf8')
				xbmc.executebuiltin("XBMC.Notification(" + titl.encode('utf8') + ", " + text + ", 8000)");
				xbmc.sleep(8000)
		else:
			if 'title' in prog and prog['title'] != None:
				when = datetime.datetime.fromtimestamp(int(prog['time']))
				titl = __language__(30014) % (when.strftime('%H:%M'))
				text = prog['title'].encode('utf8')
				xbmc.executebuiltin("XBMC.Notification(" + titl.encode('utf8') + ", " + text + ", 12000)");


xbmc.output('[%s] Loaded' % (PLUGIN_NAME))

params = get_params()
if '_s' in params and '_sn' in params:
	SID = params['_s']
	SID_NAME = params['_sn']
else:
	SID = None
	SID_NAME = None

PLUGIN_CORE = iptv.kartina(USERNAME, USERPASS, PLUGIN_ID, SID, SID_NAME)

if PLUGIN_CORE.testAuth() == False:
	dialog = xbmcgui.Dialog()
	dialog.ok( __language__(30023), __language__(30024))
	__settings__.openSettings()
else:
	
	xbmc.executebuiltin( "Container.SetViewMode(51)")
	#TRANSSID = '&_s=%s&_sn=%s' % (PLUGIN_CORE.SID, PLUGIN_CORE.SID_NAME)
	
	if 'mode' in params:
		mode = params['mode']
	else:
		if __settings__.getSetting('start_with_tv') == 'false':
			mode = None
		else:
			mode = 'TV'
	
	if 'channel' in params:
		channel = params['channel']
	else:
		channel = None
	
	if 'title' in params:
		title = params['title']
	else:
		title = ''
	
	xbmc.output('[%s] mode: %s' % (PLUGIN_NAME, mode))
	
	resetAlarms(PLUGIN_CORE, mode)
		
	if mode == 'WatchTV':
		WatchTV(PLUGIN_CORE, channel, params)

	elif mode == 'Archive':
		Archive(PLUGIN_CORE, channel, params)

	elif mode == 'Video':
		Video(PLUGIN_CORE, params)

	elif mode == 'VideoInfo':
		VideoInfo(PLUGIN_CORE, params)

	elif mode == 'WatchVOD':
		WatchVOD(PLUGIN_CORE, params)
	
	elif mode == 'ShowNowNextHint':
		ShowNowNextHint(PLUGIN_CORE, channel)
	
	elif mode == 'openSettings':
		__settings__.openSettings()

	elif mode == 'TV':
		ShowChannelsList(PLUGIN_CORE)

	elif mode == 'Settings':
		ProcessSettings(PLUGIN_CORE, params)

	elif mode == 'ExecURL':
		Get(url)
		xbmc.sleep(50)
		xbmc.executebuiltin('Container.Refresh')
	else:
		ShowRoot(PLUGIN_CORE)

