#!/usr/bin/python
#/*
# *      Copyright (C) 2011 TDW
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
import urllib2, re, string, xbmc, xbmcgui, xbmcplugin, os, urllib, cookielib
def ru(x):return unicode(x,'utf8', 'ignore')
def xt(x):return xbmc.translatePath(x)
	
handle = int(sys.argv[1])

PLUGIN_NAME   = 'IPTV'

thumb = os.path.join( os.getcwd(), "icon.png" )
fanart = os.path.join( os.getcwd(), "fanart.jpg" )
LstDir = os.path.join( os.getcwd(), "playlists" )
ImgPath = os.path.join( os.getcwd(), "logo" )
playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

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

def ShowRoot():
	RootList=os.listdir(LstDir)
	for tTitle in RootList:
		row_url = "row_url"
		Title = os.path.splitext(tTitle)[0]#' Title '
		listitem = xbmcgui.ListItem(Title)
		listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
		if 1 == 1:
			purl = sys.argv[0] + '?mode=OpenCat'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

def open_pl(pl_name):
	line=""
	Lurl=[]
	Ltitle=[]
	tvlist = os.path.join(LstDir, pl_name+'.m3u')
	fl = open(tvlist, "r")
	n=0
	for line in fl.xreadlines():
		n+=1
		if len(line)>5:
			pref=line[:5]
			if pref=="#EXTI":
				lpr=line.find(',')+1
				tmp=line[lpr:]
				if tmp[:1]==" ":Ltitle.append(line[lpr+1:])
				else: Ltitle.append(line[lpr:])
			#if pref=="MMS:" or pref=="HTTP:" or pref=="http:" or pref=="mms:/" : Lurl.append(line)
			if pref[0]<> "#"and n>1: Lurl.append(line[:-1]) #EXTI" and pref<>"#EXTV" and pref<>"#EXTM" 
	fl.close()
	return (Ltitle, Lurl)

def OpenCat(url, name):
	Ltitle, Lurl=open_pl(name)
	for i in range (len(Ltitle)):
		Title = Ltitle[i]#xbmc.translatePath(
		thumb2 = xbmc.translatePath(os.path.join(ImgPath, Title[:-2]+'.png'))
		if os.path.isfile(thumb2)==0:
			thumb2 = os.path.join(ImgPath, Title[:-1]+'.png')
			if os.path.isfile(thumb2)==0:thumb2=thumb
			thumb3 = ru(os.path.join(ImgPath, Title[:-1]+'.png'))
			if os.path.isfile(thumb3)==1:thumb2=thumb3
		row_name = Ltitle[i]
		row_url = Lurl[i]
		Plot  = ' Plot: '
		Genre = ' Genre: '
		listitem = xbmcgui.ListItem(row_name, thumbnailImage=thumb2 )
		listitem.setInfo(type = "Video", infoLabels = {
			"Title": 	row_name,
			"Studio": 	row_url,
			"Plot": 	Plot,
			"Genre": 	Genre })
		listitem.setProperty('fanart_image',fanart)
		purl = sys.argv[0] + '?mode=OpenPage'\
			+ '&url=' + urllib.quote_plus(row_url)\
			+ '&fanart_image=' + urllib.quote_plus(fanart)\
			+ '&title=' + urllib.quote_plus(Title)
		xbmcplugin.addDirectoryItem(handle, purl, listitem, False)

def OpenPage(url, name):
	item = xbmcgui.ListItem(name, iconImage = thumb, thumbnailImage = thumb)
	item.setInfo(type="Video", infoLabels={"Title": name})
	xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(url, item) 


params = get_params()
mode  = None
url   = ''
title = ''
ref   = ''
img   = ''

try:
	mode  = urllib.unquote_plus(params["mode"])
except:
	pass

try:
	url  = urllib.unquote_plus(params["url"])
except:
	pass

try:
	title  = urllib.unquote_plus(params["title"])
except:
	pass
try:
	img  = urllib.unquote_plus(params["img"])
except:
	pass

if mode == None:
	ShowRoot()
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'OpenCat':
	OpenCat(url, title)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'OpenPage':
	OpenPage(url, title)


try:
	import adanalytics
	adanalytics.adIO(sys.argv[0], sys.argv[1], sys.argv[2])
except:
	xbmc.output(' === unhandled exception in adIO === ')
	pass
