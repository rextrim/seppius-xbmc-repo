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

import urllib2,os
import xbmcplugin,xbmcgui
import demjson

pluginhandle = int(sys.argv[1])
thumb = os.path.join(os.getcwd().replace(';', ''), "icon.png" )

def getURL(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.9.2.12) Gecko/20101026 SUSE/3.6.12-0.7.1 Firefox/3.6.12')
	req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
	req.add_header('Accept-Language', 'ru,en;q=0.9')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link

djson = demjson.decode(getURL('http://online.fm/ext/config.json'))
for channel in djson['channels']:
	name = djson['channels'][channel]['name']
	uris = djson['channels'][channel]['uris']
	item = xbmcgui.ListItem(name, iconImage = thumb, thumbnailImage = thumb)
	item.setInfo(type='music', infoLabels = {'title': name})
	xbmcplugin.addDirectoryItem(pluginhandle, uris[0]+'/'+channel+' , '+uris[1]+'/'+channel, item, False)
xbmcplugin.endOfDirectory(pluginhandle)
