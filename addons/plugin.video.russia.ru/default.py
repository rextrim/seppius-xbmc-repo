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
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import urllib2, urllib, urlparse, re, os
import base64

handle = int(sys.argv[1])
api_URL = 'http://russia.ru/xbmc/menu/list.xml'
fnd_URL = 'http://russia.ru/xbmc/search/videolist.xml?q='
russia_url = 'http://www.russia.ru/'
PLUGIN_NAME = 'RUSSIA.RU'

thumb  = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))
fanart = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'fanart.jpg'))
xbmcplugin.setPluginFanart(handle, fanart)

__settings__ = xbmcaddon.Addon(id='plugin.video.russia.ru')
__language__ = __settings__.getLocalizedString

vqual = int(__settings__.getSetting('quality'))+1
lsize = (int(__settings__.getSetting('size'))+1)*10
ppup = 'pagesize=%s&quality=%s'%(lsize,vqual)

def showMessage(heading, message, times = 3000):
	heading = heading.encode('utf-8')
	message = message.encode('utf-8')
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, thumb))

def clean(name):
	remove = [('mdash;',''),('&ndash;',''),('hellip;','\n'),('&amp;',''),('&quot;','"'),
		  ('&#39;','\''),('&nbsp;',' '),('&laquo;','"'),('&raquo;','"'),('&#151;','-'),
		  ('<![CDATA[',''),(']]>','')]
	for trash, crap in remove:
		name = name.replace(trash, crap)
	return name

def CleanURL(name):
	remove = [('amp;', ''),('\n', ''),(' ',''),('\t','')]
	for trash, crap in remove:
		name = name.replace(trash, crap)
	return name


def GetRegion(data, region, modeall=False, defval=None):
	try:
		ret_val = re.compile('<%s>(.*?)</%s>'%(region,region),re.DOTALL|re.IGNORECASE).findall(data)
		if modeall: return ret_val
		else: return ret_val[0]
	except: return defval

def GET(target_url, postdata = None):
	#xbmc.output('* * * GET URL='+target_url)

	try:
		req = urllib2.Request(target_url, postdata)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
		#a = a.encode('utf-8')
		return a
	except:
		return None

def MakeItem(url, addfnd = True):
	#xbmc.output('******* MakeItem(%s, %s)'%(url, addfnd))
	http = GET(url)
	if http == None:
		showMessage(__language__(30030),__language__(30031))
		return False

	#print http


	item_blocks = GetRegion(http, 'item', True)

	if (item_blocks==None) or (len(item_blocks)==0):
		showMessage(__language__(30030),__language__(30032))
		return False

	for item_block in item_blocks:
		item_label    = clean(GetRegion(item_block, 'label',          False, ''))
		item_isFolder = GetRegion(item_block, 'isFolder',       False, '0')
		item_Image    = GetRegion(item_block, 'thumbnailImage', False, thumb)
		item_url      = GetRegion(item_block, 'url',            False, api_URL)

		item_url = CleanURL(item_url)
		item_Image = CleanURL(item_Image)

		isFolder = (item_isFolder == '1')
		uri = item_url
		if isFolder:
			uri = sys.argv[0] + '?mode=OpenItem' + '&url='+item_url.encode("hex")

		#print 'ADD item_url =' + item_url
		#print 'ADD URI =' + uri

		item = xbmcgui.ListItem(item_label, iconImage = item_Image, thumbnailImage = item_Image)
		item_type = GetRegion(item_block, 'type')
		if (item_type != None):
			item.setInfo(type = item_type, infoLabels = {
				'title':       clean(GetRegion(item_block, 'title',      False, '')),
				'director':          GetRegion(item_block, 'director',   False, ''),
				'writer':            GetRegion(item_block, 'writer',     False, ''),
				'studio':            GetRegion(item_block, 'studio',     False, 'RUSSIA.RU'),
				'genre':             GetRegion(item_block, 'genre',      False, ''),
				'year':          int(GetRegion(item_block, 'year',       False, '1970')),
				'duration':          GetRegion(item_block, 'duration',   False, ''),
				'tagline':           GetRegion(item_block, 'tagline',    False, ''),
				'plotoutline': clean(GetRegion(item_block, 'plotoutline',False, '')),
				'plot':        clean(GetRegion(item_block, 'plot',       False, '')),
				'playcount':     int(GetRegion(item_block, 'playcount',  False, '0')),
				'rating':      float(GetRegion(item_block, 'rating',     False, '0')),
				'date':              GetRegion(item_block, 'date',       False, ''),
			})
		item.setProperty('fanart_image', GetRegion(item_block, 'fanart',     False, fanart))
		xbmcplugin.addDirectoryItem(handle,uri,item,isFolder)

	if addfnd:
		uris = sys.argv[0] + '?mode=Search'
		items = xbmcgui.ListItem(__language__(30020), iconImage = thumb, thumbnailImage = thumb)
		item.setProperty('fanart_image', fanart)
		xbmcplugin.addDirectoryItem(handle,uris,items,True)

	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_UNSORTED)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_DATE)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_DURATION)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_GENRE)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_VIDEO_TITLE)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)

	xbmcplugin.endOfDirectory(handle)

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


params = get_params()
mode   = None
url    = api_URL + '?' + ppup

try:    mode  = params['mode']
except: pass
try:    url   = params['url'].decode("hex")
	#url   = params['url']
except: pass

#print 'start mode=%s' % mode
#print 'start  url=%s' % url
#print 'start  url=' + url

if mode == 'Search':
	pass_keyboard = xbmc.Keyboard()
	pass_keyboard.setHeading(__language__(30021))
	pass_keyboard.doModal()
	if (pass_keyboard.isConfirmed()):
		MakeItem(fnd_URL + pass_keyboard.getText() + '&' + ppup, False)
		# urllib.unquote_plus(
	else:
		exit
else:
	MakeItem(url)

try:
	import adanalytics
	adanalytics.adIO(sys.argv[0], sys.argv[1], sys.argv[2])
except:
	xbmc.output(' === unhandled exception in adIO === ')
	pass
