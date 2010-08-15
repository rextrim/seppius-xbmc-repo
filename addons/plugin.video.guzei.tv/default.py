#!/usr/bin/python
#/*
# *      Copyright (C) 2010 Kostynoy S. aka Seppius
# *
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
import xbmc, xbmcgui, xbmcaddon, xbmcplugin, urllib2, urllib, re, string, sys, os, traceback
from urllib import urlretrieve, urlcleanup

HEADER      = 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60'
GUZEI_TV = 'GUZEI.TV'


handle = int(sys.argv[1])
play_thumb   = os.path.join(os.getcwd(), "play.png")

def get_params():
	param=[]
	paramstring=sys.argv[2]
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

def clean(name):
	remove=[('  ','^|$'),('\n',' '),('^|$',' ')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name

def clean2(name):
	remove=[('(',''),(')',''),(':',''),('  ',' ')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name

def get_list():
	try:
		req = urllib2.Request('http://guzei.com/live/tv/')
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		return
	stage1 = re.compile('<ol>(.+?)</ol>', re.DOTALL).findall(a)[0]
	if len(stage1) == 0:
		return
	stage2 = re.compile('<li>(.+?)</li>').findall(stage1)
	if len(stage2) == 0:
		return
	for stage2x in stage2:
		(r_rates, r_id, r_name, r_speed, r_city, r_plot) = re.compile('<span class="r">(.+?)</span>.*<a class="name" href=".*id=([0-9]*)">(.+?)</a>.*:(.+?):(.+?):(.+)').findall(stage2x + ' ')[0]
		speeds = re.compile('<a class="name" href="(.+?)">(.+?)</a>').findall(stage2x)
		spd_cnt = len(speeds)
		if spd_cnt == 0:
			return
		r_rates = clean2(r_rates)
		#r_id    = clean2(r_id)
		r_name  = clean2(r_name)
		r_speed = clean2(r_speed)
		r_city  = clean2(r_city)
		r_plot  = clean2(r_plot)
		url = sys.argv[0] + "?id=" + str(r_id) + '&rate=' + str(r_rates) + \
			'&name='+urllib.quote_plus(r_name)+'&city='+urllib.quote_plus(r_city)+ \
			'&plot='+urllib.quote_plus(r_plot)+'&speed='+str(r_speed)
		r_name = r_rates +' "'+r_name+'" ['+r_speed+'kbps, '+r_city+']'
		listitem=xbmcgui.ListItem(r_name, iconImage=play_thumb, thumbnailImage=play_thumb)
		listitem.setInfo(type="Video", infoLabels = {
			"Title":	r_name,
			"Studio":	r_city,
			"Plot":		r_plot,
			"Genre":	'speed ' + r_speed } )
		xbmcplugin.addDirectoryItem(handle, url, listitem, False)

def get_play(url, rate, name, city, plot, speed):
	dialog = xbmcgui.Dialog()
	#ok = dialog.ok('Sorry', 'Embed data not found!')

	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		dialog.ok('ERROR', 'Cannot open URL=%s' % url)
		return

	#raw_url = re.compile('<embed type="application/x-shockwave-flash".*file=(.*?)&').findall(a)
	raw_url = re.compile('<embed(.*?)embed>', re.DOTALL).findall(a)
	if len(raw_url) == 0:
		dialog = xbmcgui.Dialog()
		ok = dialog.ok('Sorry', '<embed> data not found!')
		return



	raw1 = re.compile('src="(.*?)"').findall(raw_url[0])
	if len(raw1) == 0:
		raw1 = re.compile('file=(.*?)&').findall(raw_url[0])
		if len(raw1) == 0:
			dialog.ok('ERROR', 'Player data not found. Sorry.' % url)
			return

	play_url = raw1[0]

	playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	playList.clear()
	listitem=xbmcgui.ListItem(name,iconImage=play_thumb,thumbnailImage=play_thumb)
	listitem.setInfo(type="Video", infoLabels = {
		"Title": 	name,
		#"Studio": 	caption + '(City: '+ city + ')',
		#"Plot": 	caption,
		#"Artist":	GUZEI_TV,
		"Genre": 	'TV' } )
	playList.add(play_url, listitem)
	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	player.play(playList)

params = get_params()
chid = None
try:
	chid = params["id"]
except:
	pass

if len(params) == 0:
	get_list()
	xbmcplugin.setPluginCategory(handle, GUZEI_TV)
	xbmcplugin.endOfDirectory(handle)

elif chid != None:
	rate = 0
	name = 'No name of a channel'
	city = 'city is not specified'
	plot = 'No description'
	speed = 0
	try:
		rate = int(params["rate"])
	except:
		pass
	try:
		name = urllib.unquote_plus(params["name"])
	except:
		pass
	try:
		city = urllib.unquote_plus(params["city"])
	except:
		pass
	try:
		plot = urllib.unquote_plus(params["plot"])
	except:
		pass
	try:
		speed = int(params["speed"])
	except:
		pass
	work_url = 'http://guzei.com/online_tv/watch.php?online_tv_id='+str(chid)
	get_play(work_url, rate, name, city, plot, speed)
