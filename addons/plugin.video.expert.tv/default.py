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
import urllib2, re, xbmcaddon, string, xbmc, xbmcgui, xbmcplugin, os, urllib

__settings__ = xbmcaddon.Addon(id='plugin.video.expert.tv')
__language__ = __settings__.getLocalizedString
__scriptname__ = "TV.EXPERT.RU"

HEADER  = "Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60"
handle  = int(sys.argv[1])

EXPERT_URL     = 'http://tv.expert.ru'

expert_thumb   = os.path.join( os.getcwd(), "icon.png" )
playlist_file  = os.path.join( xbmc.translatePath( "special://temp/" ), "tv.expert.ru.m3u" )
thumbnail_file = os.path.join( xbmc.translatePath( "special://temp/" ), "tv.expert.ru.tbn" )

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
	remove=[('\n',' '),('&amp;','&'),('&quot;','"'),('&#39;','\''),('&nbsp;',' '),('&laquo;','"'),('&raquo;', '"'),('&#151;','-'),('<nobr>',''),('</nobr>',''),('<P>',''),('</P>',''),('<p>',''),('</p>','')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name

def Download(url, dest):
	dp = xbmcgui.DialogProgress()
	dp.create(__language__(30000), url)
	urllib.version = HEADER
	urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))

def _pbhook(numblocks, blocksize, filesize, url=None, dp=None):
	try:
		percent = min((numblocks*blocksize*100)/filesize, 100)
		dp.update(percent, url)
	except:
		percent = 100
		dp.update(percent)
	if dp.iscanceled():
		dp.close()


def playVideo(url, image = None, title = None):

	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
	except:
		dialog = xbmcgui.Dialog()
		ok = dialog.ok(__scriptname__, __language__(30001) + url)
		return
	a = f.read()
	f.close()

	try:
		page_url = re.compile("oVideo.url = '(.+?)';").findall(a)
		mp4url = EXPERT_URL + page_url[0]
	except:
		dialog = xbmcgui.Dialog()
		ok = dialog.ok(__scriptname__, __language__(30002) + url)
		return
	try:
		page_title  = re.compile("oVideo.title = '(.+?)';").findall(a)
		mp4title = clean(page_title[0])
	except:
		mp4title = url

	try:
		if image != None:
			img_urlreq = image
		else:
			page_splash = re.compile("oVideo.splash = '(.+?)';").findall(a)
			img_urlreq = EXPERT_URL + page_splash[0]
			if os.path.isfile(thumbnail_file):
				os.remove(thumbnail_file)
		urllib.version = HEADER
		urllib.urlretrieve(img_urlreq, thumbnail_file)
		mp4image = thumbnail_file
	except:
		mp4image = expert_thumb

	try:
		page_reqtmp = re.compile('</script><p>\s.*\s.*</p><p>(.+?)</p><div class="program-versions">').findall(a)
		page_req = re.compile('(?is)<.*?>').findall(page_reqtmp[0])
		mp4plot  = clean(page_req[0])
	except:
		mp4plot  = mp4title

	if len(mp4plot) < 2:
		mp4plot  = mp4title

	download_flag = __settings__.getSetting('download')
	download_ask  = __settings__.getSetting('download_ask')
	download_path = __settings__.getSetting('download_path')

	play_file     = xbmc.translatePath(os.path.join(download_path, os.path.basename(mp4url)))
	if os.path.isfile(play_file):
		download_flag = 'false'
	if (download_ask == 'true'):
		dia = xbmcgui.Dialog()
		ret = dia.select(__language__(30003), [__language__(30004), __language__(30005), __language__(30006)])
		if (ret == 0):
			download_flag = 'true'
		elif (ret == 1):
			download_flag = 'false'
			play_file = mp4url
		else:
			return
	if ( download_flag == 'true'):
		Download(mp4url, play_file)
	else:
		play_file = mp4url

	if title != None:
		title = title + ' / '

	listitem = xbmcgui.ListItem( label = "Video", thumbnailImage = mp4image )
	listitem.setInfo( type = "Video", infoLabels={
		"Title": 	title + mp4title,
		"Studio": 	EXPERT_URL,
		"Plot": 	mp4plot
	} )

	playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	playList.clear()
	playList.add(play_file, listitem)

	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	player.play(playList)


def show_program(url, title):
	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
	except:
		dialog = xbmcgui.Dialog()
		ok = dialog.ok(__scriptname__, __language__(30016) + url)
		return
	a = f.read()
	f.close()
	previons_url = None
	next_url = None
	previons_dat = re.compile('<ul class="pager"><li class="prev"><i></i><a href="(.+?)">.*</a></li>').findall(a)
	try:
		previons_url = previons_dat[0]
		previons_num = re.compile('/*/page(.+?)/').findall(previons_url)[0]
	except:
		pass
	next_dat = re.compile('<ul class="pager">.*<li class="next"><i></i><a href="(.+?)">.*</a></li></ul>').findall(a)
	try:
		next_url = next_dat[0]
		next_num = re.compile('/*/page(.+?)/').findall(next_url)[0]
	except:
		pass
	earlier_current = re.compile('<div class="subject">\s*<div>\s*<a href="(.*?)" class="play"></a>\s*<a href="(.*?)"><img src="(.*?)" alt="(.*?)" /></a>\s*</div>\s*<p class="date">(.*?)</p>\s*<h3><a href="(.*?)">(.*?)</a></h3>\s*<p>(.*?)</a></p>', re.DOTALL).findall(a)

	earliers_cnt = len(earlier_current)
	if earliers_cnt == 0:
		dialog = xbmcgui.Dialog()
		ok = dialog.ok(__scriptname__, __language__(30021) + url)
		xbmc.output('subject failure')
		xbmc.output('A= %s' % a)
		return
	x = 1
	for vu1, vu2, imgu, cap1, date, vu3, cap2, plot in earlier_current:
		url_video = vu1
		if len(url_video) < len(vu2):
			url_video = vu2
		if len(url_video) < len(vu3):
			url_video = vu3
		title_video = cap1
		if len(title_video) < len(cap2):
			title_video = cap2
		plot_fin = clean(plot)
		image    = EXPERT_URL + imgu
		ptitle    = str(x) + '. "' + clean(title_video) + '"'
		listitem = xbmcgui.ListItem(ptitle, iconImage = image, thumbnailImage = image )
		listitem.setInfo( type = "Video", infoLabels={
			"Title": 	ptitle,
			"Studio": 	EXPERT_URL,
			"Plot": 	plot_fin
		} )
		url = sys.argv[0] + "?mode=playpage&url=" + urllib.quote_plus(EXPERT_URL + url_video) + "&title=" + urllib.quote_plus(title) + "&image=" + urllib.quote_plus(image)
		xbmcplugin.addDirectoryItem( handle, url, listitem, False)
		x = x + 1

	if previons_url != None:
		ptitle    = __language__(30022) + ' ' + str(previons_num)
		listitem = xbmcgui.ListItem(ptitle)
		url = sys.argv[0] + "?mode=program&url=" + urllib.quote_plus(EXPERT_URL + previons_url) + "&title=" + ptitle + "&image=" + urllib.quote_plus(image)
		xbmcplugin.addDirectoryItem( handle, url, listitem, True)
	if next_url != None:
		ptitle    = __language__(30023) + ' ' + str(next_num)
		listitem = xbmcgui.ListItem(ptitle)
		url = sys.argv[0] + "?mode=program&url=" + urllib.quote_plus(EXPERT_URL + next_url) + "&title=" + ptitle + "&image=" + urllib.quote_plus(image)
		xbmcplugin.addDirectoryItem( handle, url, listitem, True)


def show_film():
	try:
		req = urllib2.Request(EXPERT_URL)
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
	except:
		dialog = xbmcgui.Dialog()
		ok = dialog.ok(__scriptname__, __language__(30016) + EXPERT_URL)
		return
	a = f.read()
	f.close()
	match = re.compile('<div class="film">\s*<div>\s*<a href="(.+?)"><img src="(.+?)" alt=".*" /></a>\s*</div>\s*<h3><a href=".*">(.+?)</a></h3></div>').findall(a)
	if len(match) > 0:
		for url, img, caption in match:
			image    = EXPERT_URL + img
			title    = clean(caption)
			listitem = xbmcgui.ListItem(title, iconImage = image, thumbnailImage = image )
			listitem.setInfo( type = "Video", infoLabels={
				"Title": 	title,
				"Studio": 	EXPERT_URL,
				"Plot": 	caption
			} )
			url = sys.argv[0] + "?mode=playpage&url=" + urllib.quote_plus(EXPERT_URL + url) + "&title=" + urllib.quote_plus(title) + "&image=" + urllib.quote_plus(image)
			xbmcplugin.addDirectoryItem( handle, url, listitem, False)
	else:
		dialog = xbmcgui.Dialog()
		ok = dialog.ok(__scriptname__, __language__(30024) + EXPERT_URL)
		return

def show_root():
	titl = __language__(30028)
	listitem = xbmcgui.ListItem( titl, iconImage = expert_thumb, thumbnailImage = expert_thumb )
	url = sys.argv[0] + "?mode=film&title=" + titl
	xbmcplugin.addDirectoryItem( handle, url, listitem, True )

	req_url = EXPERT_URL + '/programs'
	try:
		req = urllib2.Request(req_url)
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
	except:
		dialog = xbmcgui.Dialog()
		ok = dialog.ok(__scriptname__, __language__(30013) + req_url)
		return
	a = f.read()
	f.close()
	match = re.compile('<div class="program">\s*<a href="(.+?)"><img src="(.+?)" alt="*" /></a>\s*<h3><a href="(.+?)">(.+?)</a></h3>\s*<p>(.+?)</p>\s*</div>').findall(a)
	if len(match) > 0:
		x = 1
		for prog_url, img, prog_url2, name, plot in match:
			if len(prog_url2) > (prog_url):
				prog_url = prog_url2
			prog     = EXPERT_URL + prog_url
			image    = EXPERT_URL + img
			name = clean(name)
			title = ('%d. ' % x) + name
			listitem = xbmcgui.ListItem(title, iconImage = image, thumbnailImage = image )
			listitem.setInfo( type = "Video", infoLabels={
				"Title": 	title,
				"Studio": 	prog,
				"Plot": 	clean(plot)
			} )
			url = sys.argv[0] + "?mode=program&url=" + urllib.quote_plus(prog + 'archive/page1') + "&title=" + title + "&image=" + urllib.quote_plus(image)
			xbmcplugin.addDirectoryItem( handle, url, listitem, True)
			x = x + 1
	else:
		dialog = xbmcgui.Dialog()
		ok = dialog.ok(__scriptname__, __language__(30025) + req_url)
		return

params = get_params()

mode  = None
url   = None
index = None
title = __scriptname__

try:
	mode  = urllib.unquote_plus(params["mode"])
except:
	pass
try:
	url   = urllib.unquote_plus(params["url"])
except:
	pass
try:
	title = urllib.unquote_plus(params["title"])
except:
	pass
try:
	image = urllib.unquote_plus(params["image"])
except:
	image = None

handle = int(sys.argv[1])

if mode == None:
	show_root()
	xbmcplugin.setPluginCategory(handle, title)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_DATE)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'program':
	show_program(url, title)
	xbmcplugin.setPluginCategory(handle, title)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_DATE)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'film':
	show_film()
	xbmcplugin.setPluginCategory(handle, title)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_DATE)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'playpage':
	playVideo(url, image, title)


try:
	import adanalytics
	adanalytics.adIO(sys.argv[0], sys.argv[1], sys.argv[2])
except:
	xbmc.output(' === unhandled exception in adIO === ')
	pass
