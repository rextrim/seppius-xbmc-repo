#!/usr/bin/python
#/*
# *      Copyright (C) 2010-2011 Eugene Bond <eugene.bond@gmail.com>
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

PLUGIN_ID = 'plugin.video.rodnoe.tv'

__settings__ = xbmcaddon.Addon(id=PLUGIN_ID)

import iptv
import datetime, time

__language__ = __settings__.getLocalizedString
USERNAME = __settings__.getSetting('username')
USERPASS = __settings__.getSetting('password')
handle = int(sys.argv[1])

PLUGIN_NAME = 'Rodnoe.TV'
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
	
	if 'dt' in params:
		dt = datetime.datetime.fromordinal(int(params['dt']))
		in_arch = True
	else:
		dt = None
		in_arch = False
	
	if not dt:
		dt = datetime.datetime.today()
	
	epg = plugin.getEPG(id, dt.strftime('%Y%m%d'))
	
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
		timeLabel = datetime.datetime.fromtimestamp(progStart).strftime('%H:%M')
		
		title = '%s %s %s' % (timeLabel, prog['title'], prog['info'])
		uri = ''
		can_play = params['can_play']
		
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
		
		if can_play:
			if progStart > time.time():
				can_play = False
		
		if can_play:
			item.setProperty('IsPlayable', 'true')
			item.setIconImage(os.path.join(os.getcwd(), 'resources', 'icons', 'play.png'))
			uri = sys.argv[0] + '?mode=WatchTV&channel=%s&title=%s&ts=%s' % (id, prog['title'], prog['source']['begin']) 
		else:
			item.setIconImage(os.path.join(os.getcwd(), 'resources', 'icons', 'play-stop.png'))
			item.setProperty('IsPlayable', 'false')
		
		if currentProg and currentProg == counter:
			item.select(True)
		
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
	#xbmc.executebuiltin( "Container.SetViewMode(51)")
	if currentProg:
		try:
			win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
			win.getControl(win.getFocusId()).selectItem(currentProg+1)
		except:
			xbmc.output('[%s] cannot to select %s item', PLUGIN_NAME, currentProg)


def resetAlarms(plugin, mode):
	refreshAlarmId = '%s_refresh_list' % PLUGIN_ID
	xbmc.executebuiltin("XBMC.CancelAlarm(%s,True)" % refreshAlarmId)


def ShowChannelsList(plugin):
	refreshAlarmId = '%s_refresh_list' % PLUGIN_ID

	channels = plugin.getChannelsList()
	total_items = len(channels)
	counter = 0
	for channel in channels:
		if __settings__.getSetting('show_protected') == 'false':
			if channel['is_protected']:
				continue
		if channel['is_video']:
			counter = counter + 1
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
			
			if __settings__.getSetting('show_played') != 'false' and channel['duration']:
				played = ' [%s%%]' % channel['percent']
			else:
				played = ''
			
			timeFieldSetting = int(__settings__.getSetting('show_time_field'))
			if timeFieldSetting == 1:
				if channel['epg_start']:
					channel['duration'] = int(datetime.datetime.fromtimestamp(channel['epg_start']).strftime('%H')) * 60 + int(datetime.datetime.fromtimestamp(channel['epg_start']).strftime('%M'))
				else:
					channel['duration'] = 0
			elif timeFieldSetting == 2:
				if channel['epg_end']:
					channel['duration'] = int(datetime.datetime.fromtimestamp(channel['epg_end']).strftime('%H')) * 60 + int(datetime.datetime.fromtimestamp(channel['epg_end']).strftime('%M'))
				else:
					channel['duration'] = 0
			elif timeFieldSetting == 3:
				pass
			elif timeFieldSetting == 4:
				if channel['epg_end']:
					channel['duration'] = (channel['epg_end'] - channel['servertime']) / 60
				else:
					channel['duration'] = 0
			else:
				channel['duration'] = 0
			
			if __settings__.getSetting('colorize_groups') == 'false':
				channel_title = channel['title']
			else:
				channel_title = '[COLOR %s]%s[/COLOR]' % (color, channel['title'])
			
			label = '[B] %s.%s[/B] %s %s' % (channel_title, played, channel['subtitle'], channel['info'])
			
			item.setLabel(label)
			#item.setLabel2('xxxx')
 			item.setIconImage(channel['icon'])
			item.setInfo( type='video', infoLabels={'title': channel['subtitle'], 'plot': channel['info'], 'genre': channel['genre'], 'duration': str(channel['duration']),  'overlay': overlay})
			#, 'ChannelNumber': str(counter), 'ChannelName': channel['title'], 'StartTime': datetime.datetime.fromtimestamp(channel['epg_start']).strftime('%H:%M'), 'EndTime': datetime.datetime.fromtimestamp(channel['epg_end']).strftime('%H:%M'), 'tvshowtitle': channel['title']
			item.setProperty('IsPlayable', 'true')
			
			if 'aspect_ratio' in channel and channel['aspect_ratio']:
				item.setProperty('AspectRatio', channel['aspect_ratio'])
			
			popup = []
			
			if channel['have_epg']:
				archive_text = __language__(30006)
				if channel['have_archive']:
					archive_text = __language__(30011)
				
				uri2 = sys.argv[0] + '?mode=Archive&channel=%s&can_play=%s' % (channel['id'], channel['have_archive'])
				popup.append((archive_text, 'XBMC.Container.Update(%s)'%uri2,))
			
			popup.append((__language__(30021), 'Container.Refresh',))
			if __settings__.getSetting('start_with_tv') == 'true':
				uriP = 'XBMC.Container.Update(%s)' % (sys.argv[0] + '?mode=%s')
				popup.append((__language__(30004), uriP % 'Settings',))
			
			item.addContextMenuItems(popup, True)
			
			xbmcplugin.addDirectoryItem(handle,uri,item, False, total_items)
	
	#xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_TRACKNUM)
	#xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_GENRE)
	
	refresh_rate = int(__settings__.getSetting('autorefresh_rate'))
	
	xbmcplugin.endOfDirectory(handle, cacheToDisc=(__settings__.getSetting('always_refresh') == 'false'))
	
	if refresh_rate > 0:
		xbmc.executebuiltin("XBMC.AlarmClock(%s,XBMC.Container.Refresh,%s,True)" % (refreshAlarmId, refresh_rate))
	#xbmc.executebuiltin( "Container.SetViewMode(51)")
	#xbmcplugin.setContent(handle, 'TVShows')
	#xbmcplugin.setContent(handle=handle, content='episodes')

def WatchTV(plugin, id, title, params):
	if 'ts' in params:
		gmt = params['ts']
	else:
		gmt = None
	
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
		item=xbmcgui.ListItem(title, path=url)
		item.setInfo( type='video', infoLabels={'title': title})
		
		uri2 = sys.argv[0] + '?mode=TV'
		
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
		

def ShowNowNextHint(plugin, chid):
	current = plugin.getCurrentInfo(chid)
	hint = ''
	first = 1
	nextAlarmId = '%s_next' % PLUGIN_ID
	xbmc.executebuiltin("XBMC.CancelAlarm(%s,True)" % nextAlarmId)
	for prog in current:
		if first:
			first = 0
			if 'title' in prog and prog['title'] != None:
				titl =  __language__(30013)
				text = prog['title'].encode('utf8')
				xbmc.executebuiltin("XBMC.Notification(" + titl.encode('utf8') + ", " + text + ", 8000)")
				xbmc.sleep(8000)
		else:
			if 'title' in prog and prog['title'] != None:
				when = datetime.datetime.fromtimestamp(int(prog['time']))
				titl = __language__(30014) % (when.strftime('%H:%M'))
				text = prog['title'].encode('utf8')
				xbmc.executebuiltin("XBMC.Notification(" + titl.encode('utf8') + ", " + text + ", 12000)")
			

def ShowRoot(plugin):
	uri = sys.argv[0] + '?mode=%s'
	
	tv_title = ' [  %s  ] ' % __language__(30012)
	tv=xbmcgui.ListItem(tv_title)
	tv.setLabel(tv_title)
	tv.setProperty('IsPlayable', 'false')
	tv.setInfo( type='video', infoLabels={'title': tv_title, 'plot': __language__(30012)})
	xbmcplugin.addDirectoryItem(handle,uri % 'TV',tv,True)
	
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


xbmc.output('[%s] Loaded' % (PLUGIN_NAME))

params = get_params()
if '_s' in params and '_sn' in params:
	SID = params['_s']
	SID_NAME = params['_sn']
else:
	SID = None
	SID_NAME = None

PLUGIN_CORE = iptv.rodnoe(USERNAME, USERPASS, PLUGIN_ID, SID, SID_NAME)

if PLUGIN_CORE.testAuth() == False:
	dialog = xbmcgui.Dialog()
	dialog.ok( __language__(30023), __language__(30024))
	__settings__.openSettings()
else:
	
	#xbmc.executebuiltin( "Container.SetViewMode(51)")
	#TRANSSID = '&_s=%s&_sn=%s' % (PLUGIN_CORE.SID, PLUGIN_CORE.SID_NAME)
	
	if 'mode' in params:
		mode = params['mode']
	else:
		if __settings__.getSetting('start_with_tv') == 'true':
			mode = 'TV'
		else:
			mode = None
	
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
		WatchTV(PLUGIN_CORE, channel, title, params)
	
	elif mode == 'Archive':
		Archive(PLUGIN_CORE, channel, params)
	
	elif mode == 'ShowNowNextHint':
		ShowNowNextHint(PLUGIN_CORE, channel)
	
	elif mode == 'TV':
		ShowChannelsList(PLUGIN_CORE)
	
	elif mode == 'Settings':
		ProcessSettings(PLUGIN_CORE, params)
	
	elif mode == 'openSettings':
		__settings__.openSettings()

	elif mode == 'ExecURL':
		Get(url)
		xbmc.sleep(50)
		xbmc.executebuiltin('Container.Refresh')
	else:
		ShowRoot(PLUGIN_CORE)

