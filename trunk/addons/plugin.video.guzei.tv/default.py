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

h = int(sys.argv[1])
icon   = os.path.join(os.getcwd(), "play.png")

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

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
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		showMessage('HTTP ERROR','Не могу открыть http://guzei.com/live/tv/')
		return False
	try:
		stage2 = re.compile('<li>(.+?)</li>').findall(re.compile('<ol>(.+?)</ol>', re.DOTALL).findall(a)[0])
	except:
		showMessage('ERROR','Сбой при выборке элементов <ol> или <li>')
		return False
	if len(stage2) == 0:
		showMessage('ERROR','Элементы <li> не найдены')
		return False
	for stage2x in stage2:
		(r_rates, r_name, r_city) = re.compile('(.[0-9]*)\s*:\s*<span class="r">(.*?)</span>\s*:\s*\((.*?)\)\s*:\s').findall(stage2x)[0]
		r_urls = re.compile('<a class="name" href="(.*?)">(.*?)</a>').findall(stage2x)
		GTitle = '%s : %s : (%s) : '%(r_rates, r_name, r_city)
		for URL, SPEED in r_urls:
			t = GTitle + SPEED
			i = xbmcgui.ListItem(t, iconImage=icon, thumbnailImage=icon)
			i.setProperty('IsPlayable', 'true')
			u  = sys.argv[0] + '?mode=PLAY'
			u += '&url=%s'%urllib.quote_plus(URL)
			xbmcplugin.addDirectoryItem(h, u, i)
	xbmcplugin.endOfDirectory(h)

def get_play(url):
	try:
		req = urllib2.Request(url)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		showMessage('HTTP ERROR','Не могу открыть %s'%url)
		return False
	try:
		pblock = re.compile('player\("(.*?)"').findall(a)
	except:
		showMessage('ERROR','Не могу найти player(...)')
		return False
	i = xbmcgui.ListItem(path = pblock[0])
	xbmcplugin.setResolvedUrl(h, True, i)

params = get_params()
mode   = None
url    = ''

try:
	import adanalytics
	adanalytics.main(sys.argv[0], sys.argv[1], sys.argv[2])
except Exception, e:
	print(e)

try: mode    = urllib.unquote_plus(params['mode'])
except: pass
try: url     = urllib.unquote_plus(params['url'])
except: pass
if   mode == None:   get_list()
elif mode == 'PLAY': get_play(url)
