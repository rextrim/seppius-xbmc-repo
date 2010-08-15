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





#[13:14:50] ksaware: и прочие атрибуты
#[13:15:14] macodyn: вот плейлист
#http://www.101.ru/new101.php?bit=2&uid=33&bit=2&serv=2&t=5&r=1
#[13:15:32] macodyn: оттуда нужен только где есть nbn
#[13:18:12] ksaware: я пока этим плагином не занимаюсь. потом.
#[13:19:35] macodyn: вот, а нужон сделать так, что об выдрал только то где есть nbn



import xbmc, xbmcgui, xbmcaddon, xbmcplugin, urllib2, urllib, re, string, sys, os, traceback
from urllib import urlretrieve, urlcleanup

__settings__ = xbmcaddon.Addon(id='plugin.audio.101.ru')
__language__ = __settings__.getLocalizedString

HEADER     = 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60'
handle     = int(sys.argv[1])
BASE_PLUGIN_THUMBNAIL_PATH = os.path.join( os.getcwd(), "resources" )
play_thumb = os.path.join( BASE_PLUGIN_THUMBNAIL_PATH, "MusicPlay.png" )
path_thumb = os.path.join( BASE_PLUGIN_THUMBNAIL_PATH, "MusicFolder.png" )
url_101    = 'http://101.ru'
PLUGIN_NAME = '101.RU'

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
	remove=[('  ',''),('\n',' ')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name
def my_clean(cat_url, cat_name, cat_count):
	cat_count = cat_count.replace(' ', '')
	cat_url   = cat_url.replace(' ', '')
	cat_url   = cat_url.replace('&amp;', '&')
	return cat_url, cat_name, cat_count

def get_rootmenu():
	try:
		req = urllib2.Request(url_101+'/?an=port_groupchannels')
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
		s_uni = a.decode('cp1251')
		a = s_uni.encode('utf8')
	except:
		return
	stage1 = re.compile('<div id="radio_menu">\s.*<ul>(.+?)</ul>\s.*</div>', re.DOTALL).findall(a)[0]
	if len(stage1) == 0:
		return
	stage2all = re.compile('<li><a href="(.+?)">(.+?)</a>(.+?)</li>').findall(stage1)
	if len(stage2all) != 0:
		for cat_url, cat_name, cat_count in stage2all:
			(cat_url, cat_name, cat_count) = my_clean(cat_url, cat_name, cat_count)
			listitem = xbmcgui.ListItem(cat_name +' ('+str(cat_count)+')', iconImage=path_thumb, thumbnailImage=path_thumb)
			listitem.setInfo(type="Music", infoLabels = {
			"Title": 	cat_name,
			"Album":	url_101,
			"Genre": 	cat_name } )
			url = sys.argv[0]+"?mode=getall&url="+urllib.quote_plus(url_101+cat_url)+"&name="+urllib.quote_plus(cat_name)
			xbmcplugin.addDirectoryItem(handle, url, listitem, True)

	stage2 = re.compile('<li id="(.+?)"><a href="(.+?)" id="(.+?)">(.+?)</a> <span id="(.+?)">(.+?)</span></li>').findall(stage1)
	if len(stage2) == 0:
		return
	x=1
	for data1, cat_url, data2, cat_name, data3, cat_count in stage2:
		(cat_url, cat_name, cat_count) = my_clean(cat_url, cat_name, cat_count)
		listitem=xbmcgui.ListItem(str(x)+'. '+cat_name +' ('+str(cat_count)+')', iconImage=path_thumb, thumbnailImage=path_thumb)
		listitem.setInfo(type="Music", infoLabels = {
			"Title": 	cat_name,
			"Album":	url_101,
			"Genre": 	cat_name } )
		url = sys.argv[0]+"?mode=getgroup&url="+urllib.quote_plus(url_101+cat_url)+"&name="+urllib.quote_plus(cat_name)
		xbmcplugin.addDirectoryItem(handle, url, listitem, True)
		x=x+1

def get_all(url):
	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
		s_uni = a.decode('cp1251')
		a = s_uni.encode('utf8')
	except:
		return

	stage1 = re.compile('<div class="radio_list">(.+?)<div id="aux">', re.MULTILINE| re.DOTALL).findall(a)
	if len(stage1) == 0:
		return
	stage2 = re.compile('<h2>(.+?)</div></li>\s\n</ul>', re.MULTILINE| re.DOTALL).findall(stage1[0])
	if len(stage2) == 0:
		return
	for stage2x in stage2:
		cat_name = re.compile('<img src=".*" width=".*" height=".*" alt=".*">(.+?)</h2>').findall(stage2x)[0]
		stage3 = re.compile('<li><div class="schan">\s*<div class="play">(.+?)</div>\s*<div class="info">(.+?)</div></div>\s*</div>', re.DOTALL).findall(stage2x)
		for stage3x in stage3:
			ch_id = re.compile('OpenWin\(\'.*channel=(.+?)\'.*title=".*"').findall(stage3x[0])[0]
			(ch_name, ch_plot) = re.compile(';">(.+?)</a></p>\s*<div class="chandescr" id=".*">(.+?)<p>.*</p><div id=".*">', re.DOTALL).findall(stage3x[1])[0]
			listitem=xbmcgui.ListItem(cat_name +' : '+ch_name,iconImage=play_thumb,thumbnailImage=play_thumb)
			listitem.setInfo(type="Music", infoLabels = {
				"Title": 	ch_name,
				"Album":	clean(ch_plot),
				"Genre": 	cat_name } )
			bitrate = __settings__.getSetting('bitrate')
			if bitrate == 'true':
				BitRate = 1
			else:
				BitRate = 2
			url = sys.argv[0] + "?mode=getplay&url=" + urllib.quote_plus(url_101+'/new101.php?bit=' + str(BitRate) + '&uid=' + str(ch_id) + '&serv=')
			xbmcplugin.addDirectoryItem(handle, url, listitem, False)

def get_programs(url, name):
	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
		s_uni = a.decode('cp1251')
		a = s_uni.encode('utf8')
	except:
		return
	stage1 = re.compile('<div class="radio_list">(.+?)<div id="aux">', re.MULTILINE| re.DOTALL).findall(a)[0]
	if len(stage1) == 0:
		return
	stage2 = re.compile('<h2>(.+?)</div></li>\s.*</ul>', re.MULTILINE| re.DOTALL).findall(stage1)
	if len(stage2) == 0:
		return
	for stage2x in stage2:
		cat_name = re.compile('<img src=".*" width=".*" height=".*" alt=".*">(.+?)</h2>').findall(stage2x)[0]
		if len(cat_name) == 0:
			cat_name = name
		stage3 = re.compile('<li><div class="schan">\s*<div class="play">(.+?)</div>\s*<div class="info">(.+?)</div></div>\s*<p>(.+?)</p>\s*</div>', re.DOTALL).findall(stage2x)
		if len(stage3) == 0:
			return
		for stage3x in stage3:
			ch_id = re.compile('OpenWin\(\'.*channel=(.+?)\'.*title=".*"').findall(stage3x[0])[0]
			(ch_url, ch_name) = re.compile('<h3><a href="(.+?)".*onmouseover.*;">(.+?)</a></h3>', re.DOTALL).findall(stage3x[1])[0]
			(ch_url, ch_name, ch_plot) = my_clean(ch_url, ch_name, '')
			ch_plot = clean(stage3x[2])
			listitem=xbmcgui.ListItem(ch_name,iconImage=play_thumb,thumbnailImage=play_thumb)
			listitem.setInfo(type="Music", infoLabels = {
				"Title": 	ch_name,
				"Album":	clean(ch_plot),
				"Genre": 	cat_name } )
			bitrate = __settings__.getSetting('bitrate')
			if bitrate == 'true':
				BitRate = 1
			else:
				BitRate = 2
			url = sys.argv[0] + "?mode=getplay&url=" + urllib.quote_plus(url_101+'/new101.php?bit=' + str(BitRate) + '&uid=' + str(ch_id) + '&serv=')
			xbmcplugin.addDirectoryItem(handle, url, listitem, False)

def get_play(url, name):
	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
		s_uni = a.decode('cp1251')
		a = s_uni.encode('utf8')
	except:
		return
	stage1 = re.compile('<ref href = "(.+?)"/>\s*<title>(.+?)</title>\s.*\s.*<copyright>(.+?)</copyright>').findall(a)
	if len(stage1) == 0:
		return
	firstrack = __settings__.getSetting('firstrack')
	if firstrack == 'true':
		x = 1
	else:
		x=0
	playList = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
	playList.clear()
	for play_url, play_title, copyright in stage1:
		listitem=xbmcgui.ListItem(play_title, iconImage=play_thumb, thumbnailImage=play_thumb)
		listitem.setInfo(type="Music", infoLabels = {
			"Title": 	play_title,
			"Album":	copyright,
			"Genre": 	name } )
		if (x > 0):
			playList.add(play_url, listitem)
		else:
			x = 1
	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	player.play(playList)

params = get_params()
url  =	None
mode =	None
name =	''

try:
	url = urllib.unquote_plus(params["url"])
except:
	pass
try:
	mode = urllib.unquote_plus(params["mode"])
except:
	pass
try:
	name = urllib.unquote_plus(params["name"])
except:
	pass

if   mode == None:
	listonly = __settings__.getSetting('listonly')
	if listonly == 'true':
		get_all(url_101+'/?an=port_allchannels')
	else:
		get_rootmenu()
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)
elif mode == 'getall':
	get_all(url)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)
elif mode == 'getgroup':
	get_programs(url, name)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)
elif mode == 'getplay':
	get_play(url, name)

