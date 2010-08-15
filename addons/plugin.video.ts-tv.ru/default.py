#!/usr/bin/python
# -*- coding: utf-8 -*-
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
import xbmcaddon, xbmc, xbmcgui, xbmcplugin, os, urllib

handle = int(sys.argv[1])
thumb  = os.path.join( os.getcwd(), "icon.png" )

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
	def addItem(itemnum, name):
		listitem = xbmcgui.ListItem('%s. %s' % (itemnum, name), iconImage = thumb, thumbnailImage = thumb)
		xbmcplugin.addDirectoryItem(handle, sys.argv[0] + '?mode='+str(itemnum)+'&title=' + urllib.quote_plus(name), listitem, False)
	addItem(1, 'Концепция')
	addItem(2, 'Русский крест')
	addItem(3, 'Телепередачи')
	addItem(4, 'Научный')
	addItem(5, 'Здоровье')
	addItem(6, 'Документальный')
	addItem(7, 'Тематический')
	addItem(8, 'Художественный')
	addItem(9, 'Музыкальный')
	addItem(10, 'Анимационный')
	addItem(11, 'Новости')
	addItem(12, 'Анонсы')

def MakePL(title, src1, src2):
	playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	playList.clear()
	listitem1=xbmcgui.ListItem(title, iconImage=thumb, thumbnailImage=thumb)
	listitem2=xbmcgui.ListItem(title + ' (резервный)', iconImage=thumb, thumbnailImage=thumb)
	playList.add(src1, listitem1)
	playList.add(src2, listitem2)
	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	player.play(playList)

params = get_params()
mode  = None
title = ''

try:
	mode  = urllib.unquote_plus(params["mode"])
except:
	pass
try:
	title  = urllib.unquote_plus(params["title"])
except:
	pass
if mode == None:
	ShowRoot()
	xbmcplugin.setPluginCategory(handle, 'TS-TV')
	xbmcplugin.endOfDirectory(handle)
elif mode == '1':
	MakePL(title, 'mms://212.1.238.70/ts_tv', 'mms://85.21.245.129/ts_tv')
elif mode == '2':
	MakePL(title, 'mms://212.1.238.70/ts_tv2', 'mms://85.21.245.129/ts_tv2')
elif mode == '3':
	MakePL(title, 'mms://212.1.238.70/ts_tv3', 'mms://85.21.245.129/ts_tv3')
elif mode == '4':
	MakePL(title, 'mms://212.1.238.70/ts_tv4', 'mms://85.21.245.129/ts_tv4')
elif mode == '5':
	MakePL(title, 'mms://212.1.238.70/ts_tv5', 'mms://85.21.245.129/ts_tv5')
elif mode == '6':
	MakePL(title, 'mms://212.1.238.70/ts_tv6', 'mms://85.21.245.129/ts_tv6')
elif mode == '7':
	MakePL(title, 'mms://212.1.238.70/ts_tv7', 'mms://85.21.245.129/ts_tv7')
elif mode == '8':
	MakePL(title, 'mms://212.1.238.70/ts_tv8', 'mms://85.21.245.129/ts_tv8')
elif mode == '9':
	MakePL(title, 'mms://212.1.238.70/ts_tv9', 'mms://85.21.245.129/ts_tv9')
elif mode == '10':
	MakePL(title, 'mms://212.1.238.70/ts_tv10', 'mms://85.21.245.129/ts_tv10')
elif mode == '11':
	MakePL(title, 'mms://212.1.238.70/ts_tv11', 'mms://85.21.245.129/ts_tv11')
elif mode == '12':
	MakePL(title, 'mms://212.1.238.70/ts_tv1', 'mms://85.21.245.129/ts_tv1')

