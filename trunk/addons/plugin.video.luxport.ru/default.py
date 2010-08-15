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
__scriptname__ = "LuxPort.RU"
import xbmc, xbmcgui, xbmcplugin, urllib2, urllib, re, string, sys, os, traceback, time, random, xbmcaddon
from urllib import urlretrieve, urlcleanup

HEADER = 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60'

__settings__ = xbmcaddon.Addon(id='plugin.video.luxport.ru')
__language__ = __settings__.getLocalizedString

url_ex_id = __settings__.getSetting('host_url')
rowcnt_id = __settings__.getSetting('count_list')

if url_ex_id == '0':
	url_ex = 'http://www.ex.ua'
elif url_ex_id == '1':
	url_ex = 'http://luxport.ru'
else:
	url_ex = 'http://www.ex.ua'

if rowcnt_id == '0':
	rowcnt = 15
elif rowcnt_id == '1':
	rowcnt = 30
elif rowcnt_id == '2':
	rowcnt = 50
elif rowcnt_id == '3':
	rowcnt = 100
else:
	rowcnt = 20

handle      = int(sys.argv[1])

ex_thumb = os.path.join( os.getcwd(), "icon.png" )

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
	remove=[('<span>',''),('</span>',''),('&amp;','&'),('<strong>',''),('</strong>',''), \
		('&quot;',''),('<b>',''),('</b>',''), ('<p>',''), (', Ctrl &rarr;',''), ('&#39;','`')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name

def get_programs(url):
	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		req.add_header('Cookie', 'uper=' + str(rowcnt))
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		return
	raw_prog = re.compile("<td align=center valign=center><a href='(.*?)'><b>(.*?)</b></a><p><a href='(.*?)' class=info>(.*?)</a>(.*?)</td>").findall(a)
	if len(raw_prog) > 0:
		x = 1
		for row_1, row_2, row_3, row_4, row_5 in raw_prog:
			if len(row_3) > len(row_1):
				row_1 = row_3
			row_2 = clean(row_2)
			row_4 = clean(row_4)
			listitem = xbmcgui.ListItem(str(x) + '. ' + row_2, iconImage = ex_thumb, thumbnailImage = ex_thumb)
			listitem.setInfo(type = "Video", infoLabels = {
				"Title": 	row_2,
				"Plot": 	row_4,
				"Genre": 	row_4 } )
			url = sys.argv[0] + "?mode=openlist&url=" + urllib.quote_plus(url_ex + row_1)
			xbmcplugin.addDirectoryItem(handle, url, listitem, True)
			x = x+1
	pages_raw = re.compile("<p>\s.*<table(.*)<td><form>", re.DOTALL).findall(a)
	if len(pages_raw) > 0:
		pages_rbw = re.compile("<td><a href='(.*?)'>(.*?)</a></td>").findall(pages_raw[0])
		if len(pages_rbw) > 0:
			for row_1, row_2 in pages_rbw:
				row_1 = url_ex + row_1
				check_row = re.compile("alt='(.*?)'").findall(row_2)
				if len(check_row) > 0:
					row_2 = check_row[0]
				else:
					row_2 = 'Page ' + row_2
				row_2 = clean(row_2)
				listitem = xbmcgui.ListItem(row_2)
				listitem.setInfo(type = "Video", infoLabels = {
					"Title": 	row_2,
					"Plot": 	row_2 } )
				url = sys.argv[0] + "?url=" + urllib.quote_plus(row_1)
				xbmcplugin.addDirectoryItem(handle, url, listitem, True)


def get_list(url):
	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		req.add_header('Cookie', 'uper=' + str(rowcnt))
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		return

	pre_raw = re.compile("<td align=center valign=center>(.*?)</td>").findall(a)
	if len(pre_raw) > 0:
		x = 1
		for pre_row in pre_raw:
			raw_prog = re.compile("<a href='(.*?)'><img src='(.*?)' width='(.*?)' height='(.*?)' border='(.*?)' alt='(.*?)'></a>.*<a href='(.*?)'><b>(.*?)</b></a><br><a href='(.*?)'>(.*?)</a>,&nbsp;<small>(.*?)</small><p>(.*?)&nbsp;").findall(pre_row)
			if len(raw_prog) > 0:
				(row_1, row_2, row_3, row_4, row_5, row_6, row_7, row_8, row_9, row_10, row_11, row_12) = raw_prog[0]
				#xbmc.output('row_1  =  %s' %  row_1)  #
				#xbmc.output('row_2  =  %s' %  row_2)  #
				#xbmc.output('row_3  =  %s' %  row_3)  #
				#xbmc.output('row_4  =  %s' %  row_4)  #
				#xbmc.output('row_5  =  %s' %  row_5)  #
				#xbmc.output('row_6  =  %s' %  row_6)  #
				#xbmc.output('row_7  =  %s' %  row_7)  #
				#xbmc.output('row_8  =  %s' %  row_8)  #
				#xbmc.output('row_9  =  %s' %  row_9)  #
				#xbmc.output('row_10 =  %s' % row_10)  #
				#xbmc.output('row_11 =  %s' % row_11)  #
				#xbmc.output('row_12 =  %s' % row_12)  #
				row_4 = clean(row_4)
				row_6 = clean(row_6)
				row_10 = clean(row_10)

				listitem = xbmcgui.ListItem(str(x) + '. ' + row_6, iconImage = row_2, thumbnailImage = row_2)
				listitem.setInfo(type = "Video", infoLabels = {
					"Title": 	row_6,
					"Plot": 	row_10,
					"Genre": 	row_4 } )
				url = sys.argv[0] + "?mode=openpage&url=" + urllib.quote_plus(url_ex + row_1)
				xbmcplugin.addDirectoryItem(handle, url, listitem, False)
				x = x+1
	pages_raw = re.compile("<p>\s.*<table(.*)<td><form>", re.DOTALL).findall(a)
	if len(pages_raw) > 0:
		pages_rbw = re.compile("<td><a href='(.*?)'>(.*?)</a></td>").findall(pages_raw[0])
		if len(pages_rbw) > 0:
			for row_1, row_2 in pages_rbw:
				row_1 = url_ex + row_1

				check_row = re.compile("alt='(.*?)'").findall(row_2)
				if len(check_row) > 0:
					row_2 = check_row[0]
				else:
					row_2 = 'Page ' + row_2
				row_2 = clean(row_2)
				listitem = xbmcgui.ListItem(row_2)
				listitem.setInfo(type = "Video", infoLabels = {
					"Title": 	row_2,
					"Plot": 	row_2 } )
				url = sys.argv[0] + "?mode=openlist&url=" + urllib.quote_plus(row_1) + \
					"&name=" + urllib.quote_plus(row_2)
				xbmcplugin.addDirectoryItem(handle, url, listitem, True)


def get_page(url, name):
	dialog = xbmcgui.Dialog()
	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		req.add_header('Cookie', 'uper=' + str(rowcnt))
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		dialog.ok(__scriptname__, 'Exception on func get_page()')
		return

	raw_prog = re.compile(".*<a href='(.*?).m3u' rel='nofollow'><b>.*</b></a>").findall(a)
	if len(raw_prog) > 0:
		playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		playList.clear()
		row_1 = raw_prog[0]
		listitem = xbmcgui.ListItem(name)
		listitem.setInfo(type = "Video", infoLabels = {
			"Title": 	name,
			"Plot": 	name,
			"Genre": 	name })

		playurl = url_ex + row_1 + '.m3u'
		playList.add(playurl, listitem)
		player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
		player.play(playList)
	else:
		dialog.ok(__scriptname__, 'M3U playlist not found. Sorry...')

params = get_params()
mode   = None
url    = url_ex + '/ru/video'

try:
	mode  = urllib.unquote_plus(params["mode"])
except:
	pass
try:
	url  = urllib.unquote_plus(params["url"])
except:
	pass

if mode == None:
	get_programs(url)
	xbmcplugin.setPluginCategory(handle, __scriptname__)
	xbmcplugin.endOfDirectory(handle)
elif mode == 'openlist':
	get_list(url)
	xbmcplugin.setPluginCategory(handle, __scriptname__)
	xbmcplugin.endOfDirectory(handle)
elif mode == 'openpage':
	name = url
	try:
		name  = urllib.unquote_plus(params["name"])
	except:
		pass
	get_page(url, name)


