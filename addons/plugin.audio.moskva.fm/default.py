#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib,urllib2,re,sys,os,random
import xbmcplugin,xbmcgui
import time
from datetime import datetime, timedelta

pluginhandle = int(sys.argv[1])
thumb = os.path.join(os.getcwd().replace(';', ''), "icon.png" )


def showMessage(heading, message, times = 3000):
	heading = heading.encode('utf-8')
	message = message.encode('utf-8')
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, thumb))


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



def getURL(url,Referer = 'http://www.moskva.fm/'):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60')
	req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
	req.add_header('Accept-Language', 'ru,en;q=0.9')
	req.add_header('Referer', Referer)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link


def get_root():

	uri = sys.argv[0] + '?mode=OpenArtists'
	uri += '&url='  + urllib.quote_plus('http://www.moskva.fm/artists')
	item = xbmcgui.ListItem('Исполнители', iconImage = thumb, thumbnailImage = thumb)
	xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

	uri = sys.argv[0] + '?mode=OpenStations'
	uri += '&url='  + urllib.quote_plus('http://www.moskva.fm/rss/onair.xml')
	item = xbmcgui.ListItem('Станции', iconImage = thumb, thumbnailImage = thumb)
	xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

#	uri = sys.argv[0] + '?mode=OpenPrograms'
#	uri += '&url='  + urllib.quote_plus('http://www.moskva.fm/programs')
#	item = xbmcgui.ListItem('Передачи', iconImage = thumb, thumbnailImage = thumb)
#	xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

#	uri = sys.argv[0] + '?mode=OpenCharts'
#	uri += '&url='  + urllib.quote_plus('http://www.moskva.fm/charts')
#	item = xbmcgui.ListItem('Хит-парады', iconImage = thumb, thumbnailImage = thumb)
#	xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

#	uri = sys.argv[0] + '?mode=OpenEvents'
#	uri += '&url='  + urllib.quote_plus('http://www.moskva.fm/events')
#	item = xbmcgui.ListItem('Концерты', iconImage = thumb, thumbnailImage = thumb)
#	xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

	xbmcplugin.endOfDirectory(pluginhandle)



def mfindal(http, ss, es):
	L=[]
	while http.find(es)>0:
		s=http.find(ss)
		e=http.find(es)
		i=http[s:e]
		L.append(i)
		http=http[e+2:]
	return L

def OpenStations2(url):
	http = getURL(url)
	ss = '<item>'
	es = '</item>'
	L1=mfindal(http, ss, es)
	for i in L1:
			ss = "<guid isPermaLink='true'>"
			es = '</guid>'
			url=mfindal(i, ss, es)[0].replace(ss,"")
			ss = '<enclosure type="image/gif" url="'
			es = '" />'
			img=""#mfindal(i, ss, es)[0].replace(ss,"")
			ss = '<title>'
			es = '</title>'
			title=mfindal(i, ss, es)[0].replace(ss,"")

			uri = sys.argv[0] + '?mode=OpenStation'
			uri += '&url='  + urllib.quote_plus(url)
			item = xbmcgui.ListItem(title, iconImage = img, thumbnailImage = img)
			xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
	xbmcplugin.endOfDirectory(pluginhandle)



playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)

def OpenStations(ci):
	playlist.clear()
	url="http://www.moskva.fm/stations/order:name"
	http = getURL(url)
	ss = '<div class="thumbnail msk-thumbnail-station msk-thumbnail-big msk-thumbnail-mount'
	es = 'onclick="return openPlr(this)"'
	L1=mfindal(http, ss, es)
	j=0
	
	for i in L1:
			i=i.replace(chr(10),"").replace(chr(13),"").replace('	',"").replace('<div class="thumbnail msk-thumbnail-station msk-thumbnail-big msk-thumbnail-mount',"['").replace('" class="logo" style="display:block;" title="',"','").replace('"><img src="',"','").replace('" title="',"','").replace('class="station"><b>',"','").replace('</b></a><small class="meta">',"','").replace('&nbsp;FM</small></h4><!--p><span class="button_item"><a href="http://www.moskva.fm/play/',"','").replace('/translation"',"']")
			#print i
			try:
				Li=eval(i)
				url = Li[6]
				img = Li[2]
				if len(Li[5])<5: dbr="  "
				else:dbr=""
				title=dbr+Li[5]+" FM"+"  -  [B]"+Li[4] +"[/B]"
				uri = sys.argv[0] + '?mode=OpenStation'
				uri += '&url='  + urllib.quote_plus(str(j))
				item = xbmcgui.ListItem(title, iconImage = img, thumbnailImage = img)
				item.setInfo(type="Music", infoLabels={"Title": title})
				so=False
				if ci==j: 
					so=True
					item.select(True)
				xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
				Station(url,img,title,so)
				j+=1
			except:
				print "err: "+str(j)+" : " +i
	xbmcplugin.endOfDirectory(pluginhandle)

def Station(st,thumb="",title="",so=False):
	link='http://92.241.163.22/stream/'+st+'/0?format=flv'#mp3'
	item = xbmcgui.ListItem(title, iconImage = thumb, thumbnailImage = thumb)
	item.setInfo(type="Music", infoLabels={"Title": title})
	item.select(so)
	playlist.add(url=link, listitem=item, index=-1)

def OpenStation(j):
	i=int(j)
	#OpenStations(i)
	xbmc.Player(xbmc.PLAYER_CORE_AUTO).playselected(i)
	#xbmc.executebuiltin('Container.Refresh')
	
	#try:#.play(playlist.__getitem__(i).getfilename(),playlist.__getitem__(i))
	#except:pass#xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(playlist)

def OpenStation2(url):
	http = getURL(url)
	ss = "swfobject.embedSWF( 'http://css.moskva.fm/f/MoskvaPlayer"
	es = "playerxml: 'player_xml.html"
	W1=mfindal(http, ss, es)[0]
	ss = "station:"
	es = "servertime:"
	W2 = mfindal(W1, ss, es)[0].replace(chr(10),"").replace(chr(13),"").replace('	',"").replace('station',"'station'").replace('time',"'time'")
	W3 = eval("{"+W2[:-1]+"}")
	st=W3["station"]
	tm=W3["time"]
	link='http://92.241.163.22/stream/'+st+'/'+tm+'?format=flv'#mp3'
	p = xbmc.Player()
	p.play(link)



params = get_params()
url  =	'http://www.moskva.fm/rss/onair.xml'
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
	OpenStations(url)

elif mode == 'OpenArtists':
	OpenArtists(url)

elif mode == 'OpenArtist':
	OpenArtist(url)

elif mode == 'PlayTrack':
	PlayTrack(url)

elif mode == 'OpenStations':
	OpenStations(url)
	
elif mode == 'OpenStation':
	OpenStation(url)
	
elif mode == 'OpenPrograms':
	OpenPrograms(url)

elif mode == 'OpenCharts':
	OpenCharts(url)

elif mode == 'OpenEvents':
	OpenEvents(url)

