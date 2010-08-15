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
__scriptname__ = "BEE.FM"
import xbmc, xbmcgui, xbmcplugin, urllib2, urllib, re, string, sys, os, traceback
from urllib import urlretrieve, urlcleanup

handle     = int(sys.argv[1])
HEADER     = 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60'
BASE_PLUGIN_THUMBNAIL_PATH = os.path.join( os.getcwd(), "resources" )
play_thumb = os.path.join( BASE_PLUGIN_THUMBNAIL_PATH, "MusicPlay.png" )
path_thumb = os.path.join( BASE_PLUGIN_THUMBNAIL_PATH, "MusicFolder.png" )
url_bee    = "http://online.bee.fm"

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

def get_page(url):
	url = url_bee + url
	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		xbmc.output('Except on request!')
		return

	raw1 = re.compile("<div class=\"nav c\">(.*?)</div>\t<br/><br/>").findall(a)
	if len(raw1) != 0:
		raw2 = re.compile('<a href="(.*?)">(.*?)</a>').findall(raw1[0])
		if len(raw2) != 0:
			for pg_url, pg_num in raw2:
				pg_title = 'To page ' + str(pg_num)
				listitem = xbmcgui.ListItem(pg_title, iconImage = path_thumb, thumbnailImage = path_thumb)
				listitem.setInfo(type="Music", infoLabels = {
				"Title": 	pg_title,
				"Album":	url_bee } )
				url = sys.argv[0] + "?url=" + urllib.quote_plus(pg_url)
				xbmcplugin.addDirectoryItem(handle, url, listitem, True)

	rbw1 = re.compile("<div class='fillcontent'>(.*?)</span>\n\t\t\t\t", re.DOTALL).findall(a)
	if len(rbw1) != 0:
		rbw2 = re.compile("<a href='(.*?)'>(.*?)</a>").findall(rbw1[0])
		if len(rbw2) != 0:
			for pg_url, pg_num in rbw2:
				pg_title = str(pg_num)
				listitem = xbmcgui.ListItem(pg_title, iconImage = path_thumb, thumbnailImage = path_thumb)
				listitem.setInfo(type="Music", infoLabels = {
				"Title": 	pg_title,
				"Album":	url_bee } )
				url = sys.argv[0] + "?url=" + urllib.quote_plus(pg_url)
				xbmcplugin.addDirectoryItem(handle, url, listitem, True)

	data1 = re.compile("<div class='block'>(.*?)</div>\s\s\s\t\t\t\t\t\t\t", re.DOTALL).findall(a)
	if len(data1) != 0:
		for data1a in data1:
			data1_s = re.compile("class='light'>(.+?)</a>").findall(data1a)
			data1_f = re.compile("<div class='ics'>.*<img src='.*' class='.*' width='.*' alt='.*'/><a href='.*'>(.+?)</a>", re.DOTALL).findall(data1a)
			data1_m = re.compile("<a href='.*' class='tit'>(.*?)</a><a href='(.*?)'>").findall(data1a)
			data1_i = re.compile("<img class='preview' width=.* src='(.+?)' alt='' />", re.DOTALL).findall(data1a)
			thumb_img = play_thumb
			if len(data1_i) != 0:
				thumb_img = str(data1_i[0])
			online = 'Unknown'
			if len(data1_s) != 0:
				online = str(data1_s[0])
			inbookmark = 'Unknown'
			if len(data1_f) != 0:
				inbookmark = str(data1_f[0])
			if len(data1_m) != 0:
				(track_name, m3ufile) = data1_m[0]
				plot = online + ' users online, bookmark in ' + inbookmark + ' users'
				listitem = xbmcgui.ListItem(track_name, iconImage = thumb_img, thumbnailImage = thumb_img)
				listitem.setInfo(type="Music", infoLabels = {
					"title": 	track_name,
					"genre":	plot,
					"album":	url_bee} )
				xbmcplugin.addDirectoryItem(handle, m3ufile, listitem, False)

params = get_params()
url  = '/'

try:
	url = urllib.unquote_plus(params["url"])
except:
	pass

get_page(url)

xbmcplugin.setPluginCategory(handle, __scriptname__)
xbmcplugin.endOfDirectory(handle)
