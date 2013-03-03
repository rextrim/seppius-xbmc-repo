#!/usr/bin/python
# -*- coding: utf-8 -*-

# *      Copyright (C) 2013 TDW
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
import time
import httplib
import urllib
import urllib2
import re
import sys
import os
import Cookie

import string, xbmc, xbmcgui, xbmcplugin, os, urllib, cookielib, xbmcaddon, time, codecs

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import socket
socket.setdefaulttimeout(50)

icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'icon.png'))
siteUrl = 'www.fast-torrent.org'
httpSiteUrl = 'http://' + siteUrl
sid_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin.video.fasttorrent.org.cookies.sid')

h = int(sys.argv[1])

try:
	from ftkat import*
except:
	pass
#from ftkat import*


def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

def htmlEntitiesDecode(string):
	return BeautifulStoneSoup(string, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents[0]

def showMessage(heading, message, times = 3000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

headers  = {
	'User-Agent' : 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00',
	'Accept'     :' text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*',
	'Accept-Language':'ru-RU,ru;q=0.9,en;q=0.8',
	'Accept-Charset' :'utf-8, utf-16, *;q=0.1',
	'Accept-Encoding':'identity, *;q=0'
}

def GET(target, referer, post_params = None, accept_redirect = True, get_redirect_url = False):
	try:
		connection = httplib.HTTPConnection(siteUrl)

		if post_params == None:
			method = 'GET'
			post = None
		else:
			method = 'POST'
			post = urllib.urlencode(post_params)
			headers['Content-Type'] = 'application/x-www-form-urlencoded'

		if os.path.isfile(sid_file):
			fh = open(sid_file, 'r')
			csid = fh.read()
			fh.close()
			headers['Cookie'] = 'session=%s' % csid

		headers['Referer'] = referer
		connection.request(method, target, post, headers = headers)
		response = connection.getresponse()

		if response.status == 403:
			raise Exception("Forbidden, check credentials")
		if response.status == 404:
			raise Exception("File not found")
		if accept_redirect and response.status in (301, 302):
			target = response.getheader('location', '')
			if target.find("://") < 0:
				target = httpSiteUrl + target
			if get_redirect_url:
				return target
			else:
				return GET(target, referer, post_params, False)

		try:
			sc = Cookie.SimpleCookie()
			sc.load(response.msg.getheader('Set-Cookie'))
			fh = open(sid_file, 'w')
			fh.write(sc['session'].value)
			fh.close()
		except: pass

		if get_redirect_url:
			return False
		else:
			http = response.read()
			return http

	except Exception, e:
		showMessage('Error', e, 5000)
		return None


def GET3(target, referer, post=None):
	#print target
	try:
		req = urllib2.Request(url = target, data = post)
		req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
		resp = urllib2.urlopen(req)
		http = resp.read()
		resp.close()
		return http
	except Exception, e:
		xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
		showMessage('HTTP ERROR', e, 5000)




def ru(x):return unicode(x,'utf8', 'ignore')
def xt(x):return xbmc.translatePath(x)
p = re.compile(r'<.*?>')
#p.sub('', html)

	
handle = int(sys.argv[1])

PLUGIN_NAME   = 'fasttorrent'

addon = xbmcaddon.Addon(id='plugin.video.fasttorrent.org')
__settings__ = xbmcaddon.Addon(id='plugin.video.fasttorrent.org')
xbmcplugin.setContent(int(sys.argv[1]), 'movies')

dc={"1 канал" : "001", "1+1" : "002"}
#try:
#	from canal_list import*
#except:
#	pass

thumb = os.path.join( addon.getAddonInfo('path'), "icon.png" )
fanart = os.path.join( addon.getAddonInfo('path'), "fanart.jpg" )
LstDir = os.path.join( addon.getAddonInfo('path'), "playlists" )
dbDir = os.path.join( addon.getAddonInfo('path'), "db" )
ImgPath = os.path.join( addon.getAddonInfo('path'), "logo" )
playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

#siteUrl = '109.95.47.77/BP-TV.m3u'
#httpSiteUrl = 'http://' + siteUrl
#httpSiteUrl = 'http://opensharing.org/download/43651'
#httpSiteUrl ='http://d.rutor.org/download/175775'
ru_film='5'
en_film='most-films'
nauka='12'
serial='last-tv'
tv_video='6'
mult='7'
anime='10'
all_cat='0'

sort_data='0'
sort_sid='0'
sort_name='0'



#---------tsengine----by-nuismons-----

from TSCore import TSengine as tsengine
prt_file= __settings__.getSetting('port_path')
aceport=62062
try:
	if prt_file: 
		gf = open(prt_file, 'r')
		aceport=int(gf.read())
		gf.close()
except: prt_file=None

if not prt_file:
	try:
		fpath= os.path.expanduser("~")
		pfile= os.path.join(fpath,'AppData\Roaming\TorrentStream\engine' ,'acestream.port')
		gf = open(pfile, 'r')
		aceport=int(gf.read())
		gf.close()
		__settings__.setSetting('port_path',pfile)
		#print aceport
	except: aceport=62062



def play_url(params):
	torr_link=params['file']
	img=urllib.unquote_plus(params["img"])
	#showMessage('heading', torr_link, 10000)
	TSplayer=tsengine()
	out=TSplayer.load_torrent(torr_link,'TORRENT',port=aceport)
	if out=='Ok':
		for k,v in TSplayer.files.iteritems():
			li = xbmcgui.ListItem(urllib.unquote(k))
			uri = construct_request({
				'torr_url': torr_link,
				'title': k,
				'ind':v,
				'img':img,
				'mode': 'play_url2'
			})
			xbmcplugin.addDirectoryItem(handle, uri, li, False)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(handle)
	TSplayer.end()
	
def play_url2(params):
	#torr_link=params['torr_url']
	torr_link=urllib.unquote_plus(params["torr_url"])
	img=urllib.unquote_plus(params["img"])
	title=urllib.unquote_plus(params["title"])
	#showMessage('heading', torr_link, 10000)
	TSplayer=tsengine()
	out=TSplayer.load_torrent(torr_link,'TORRENT',port=aceport)
	if out=='Ok':
		TSplayer.play_url_ind(int(params['ind']),title, icon, img)
	TSplayer.end()

#===================old=========================

def sva(s):
	fl = open(os.path.join( ru(addon.getAddonInfo('path')),"cast.py"), "w")
	fl.write("da="+str(s))
	fl.close()

try:from cast import*
except:da={}

def svd(s):
	fl = open(os.path.join( ru(addon.getAddonInfo('path')),"director.py"), "w")
	fl.write("dr="+str(s))
	fl.close()

try:from director import*
except:dr={}

def debug(s):
	fl = open(os.path.join( ru(addon.getAddonInfo('path')),"test.txt"), "w")
	fl.write(s)
	fl.close()

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

def showMessage(heading, message, times = 50000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, thumb))



def GET2(url):
	try:
		urllib.urlretrieve(url,os.path.join(LstDir, "move4.torrent"))
		#print 'def GET(%s):'%url
		req = urllib2.Request(url)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
		return a
	except:
		showMessage('Не могу открыть URL def GET', url)
		return None

def mfindal(http, ss, es):
	L=[]
	while http.find(es)>0:
		s=http.find(ss)
		e=http.find(es)
		i=http[s:e]
		L.append(i)
		http=http[e+2:]
	return L


def formtext_n(http):
	n=http.find('end Пустой баннер')
	http=http[n:]
	http=http.replace(chr(13),chr(10))
	http=http.replace(chr(10)+chr(10),chr(10))
	http=http.replace(chr(10)+chr(10),chr(10))
	http=http.replace("\t","")
	http=http.replace("'",'"')
	#print http
	ss='<tr valign="top" height="10px" class='
	es='<em class="download-button">'#'<tr><td colspan="4"'
	
	L=mfindal(http, ss, es)
	
	RL=[]
	for i in L:
		dict={}
	#------------------- ищем страну ----------------
		ss='<em class="cn-icon'
		es='<em class="qa-icon'
		if i.find(es)<0:es='</em><em class="fo-icon'
		L2=mfindal(i, ss, es)
		nm=""
		for i2 in L2:
			ss2='title="'
			es2='">'
			L3=mfindal(i2, ss2, es2)
			nm=""
			for i3 in L3:
				nm=nm+i3[len(ss2):]+"; "
		#print("СТРАНА: "+nm)#[5]))
		if nm!="":dict['studio']=nm[:-2]
	#------------------- ищем режисера ----------------
	#for i in L:
		ss='<span style="header">Режиссеры</span>'
		es='style="text-align:left'
		if i.find(ss)<0:ss='<span style="header">Режиссер</span>'
		L2=mfindal(i, ss, es)
		nm=""
		L4=[]
		for i2 in L2:
			ss2='span itemprop="name">'
			es2='</span></a>'
			L3=mfindal(i2, ss2, es2)
			nm=""
			for i3 in L3:
				nm=nm+i3[len(ss2):]+"; "
				L4.append(i3[len(ss2):])
		#print("РЕЖИСЕР: "+nm)
		if nm!="":dict['director']=nm[:-2]
		try:dict['director3']=L4
		except: pass
		
#	#------------------- ищем режисера2 ----------------
#	#for i in L:
#		ss='<span style="header">Режиссеры</span>'
#		es='style="text-align:left'
#		if i.find(ss)<0:ss='<span style="header">Режиссер</span>'
#		L2=mfindal(i, ss, es)
#		L4=[]
#		for i2 in L2:
#			ss2='<a href="/video/actor/'
#			es2='/1.html" itemprop="actor'
#			L3=mfindal(i2, ss2, es2)
#			nm=""
#			L4=[]
#			for i3 in L3:
#				#nm=nm+" "+i3[len(ss2):]
#				L4.append(i3[len(ss2):])
#		#print("АКТЕРЫ: "+nm)
#		dict['director2']=L4


	#------------------- ищем актеров ----------------
	#for i in L:
		ss='>В ролях</span>'
		es='<p class="justify clear'
		#if i.find(ss)<0:ss='<span style="header">Режиссер</span>'
		L2=mfindal(i, ss, es)
		
		for i2 in L2:
			ss2='itemprop="name">'
			es2='</span></a>'
			L3=mfindal(i2, ss2, es2)
			nm=""
			L4=[]
			for i3 in L3:
				#nm=nm+" "+i3[len(ss2):]
				L4.append(i3[len(ss2):])
		#print("АКТЕРЫ: "+nm)
		dict['cast']=L4
		
	#------------------- ищем актеров2 ----------------
#	#for i in L:
#		ss='>В ролях</span>'
#		es='<p class="justify clear'
#		#if i.find(ss)<0:ss='<span style="header">Режиссер</span>'
#		L2=mfindal(i, ss, es)
#		
#		for i2 in L2:
#			ss2='<a href="/video/actor/'
#			es2='/1.html" itemprop="actor'
#			L3=mfindal(i2, ss2, es2)
#			nm=""
#			L4=[]
#			for i3 in L3:
#				#nm=nm+" "+i3[len(ss2):]
#				L4.append(i3[len(ss2):])
#		#print("АКТЕРЫ: "+nm)
#		dict['cast2']=L4

	#------------------- ищем описание ----------------
	#for i in L:
		ss='<p class="justify clear">'
		es='</p></td></tr><tr height=1%><td class="bottom">'
		#if i.find(ss)<0:ss='<span style="header">Режиссер</span>'
		L2=mfindal(i, ss, es)
		nm=L2[0][len(ss):]
		#print("ОПИСАНИЕ: "+nm)
		dict['plot']=nm
	#------------------- ищем ссылку ----------------
	#for i in L:
		ss='td rowspan="2" nowrap="nowrap"><a href="'
		es='" target="_blank">'
		#if i.find(ss)<0:ss='<span style="header">Режиссер</span>'
		L2=mfindal(i, ss, es)
		nm=L2[0][len(ss):]
		#print("URL: "+nm)
		dict['url']=nm
	#------------------- ищем обложку ----------------
	#for i in L:
		ss='target="_blank"><img src="'
		es='" alt="'
		#if i.find(ss)<0:ss='<span style="header">Режиссер</span>'
		L2=mfindal(i, ss, es)
		nm=L2[0][len(ss):]
		#print("IMG: "+nm)
		dict['cover']=nm
	#------------------- ищем название ----------------
	#for i in L:</li></ul></span></div><h2>
		ss='</div><h2>'#</ul></span>
		es='</h2><div class="genre_list'
		#if i.find(ss)<0:ss='</h2><div class="genre_list'
		L2=mfindal(i, ss, es)
		try:nm=L2[0][len(ss):].replace("<br/>",'').strip()
		except: nm="НАЗВАНИЕ"
		#print("НАЗВАНИЕ: "+nm)
		dict['title']=nm
		try:dict['year']=int(mfindal(nm, "(", ")")[0][1:])
		except:
			try:dict['year']=int(mfindal(nm, "(", ")")[1][1:])
			except:pass
	#------------------- ищем жанры ----------------
	#for i in L:
		ss='class="genre_list"><a href='
		es='<div class="tag_list'
		if i.find(es)<0:es='</div><p style="text-align:left'
		L2=mfindal(i, ss, es)
		nm=""
		for i2 in L2:
			ss2='" >'
			if i2.find(ss2)<0:ss2='"  >'
			es2='</a>'
			L3=mfindal(i2, ss2, es2)
			nm=""
			for i3 in L3:
				nm=nm+i3[len(ss2):]+"; "
		#print("ЖАНРЫ: "+nm)
		if nm!="":dict['genre']=nm
	#------------------- ищем рейтинг ----------------
	#for i in L:
		ss='inline-rating" title="'
		es='из 5, голосов'
		#if i.find(ss)<0:ss='</h2><div class="genre_list'
		L2=mfindal(i, ss, es)
		try:
			nm=L2[0][len(ss):]
			#print("РЕЙТИНГ: "+nm)
			dict['rating']=float(nm)
		except: pass
		RL.append(dict)
	return RL


def formtext(http):
	formtext_n(http)
	n=http.find('end Пустой баннер')
	http=http[n:]
	http=http.replace(chr(13),chr(10))#.replace(chr(13),"")
	http=http.replace(chr(10)+chr(10),chr(10))
	http=http.replace("'",'"')
	http=http.replace(' nowrap="nowrap">'+chr(10)+'\t\t<a href="',chr(10)+'flag11:')
	http=http.replace('" target="_blank"><img src="',chr(10)+'flag22:')
	http=http.replace('inline-rating" title="',chr(10)+'flag33:')
	http=http.replace('\t\t<h2>',chr(10)+'flag44:')
	http=http.replace('<p class="justify clear">'+chr(10)+'\t\t\t',chr(10)+'flag55:')
	http=http.replace('<p class="justify clear"><p>',chr(10)+'flag55:')
	http=http.replace('" alt="',chr(10)+'none:')
	http=http.replace(')<br/></h2>',chr(10))
	http=http.replace(' <br/>('," ")
	http=http.replace('</h2>',"")
	http=http.replace('из 5, голосов',chr(10)+'none2:')
	http=http.replace("</li></ul></span></div><h2>",chr(10)+'flag66:')
	http=http.replace('<div class="genre_list"><',chr(10))
	http=http.replace('</td><td class="bottom"><a href="',chr(10)+'flag77:')
	http=http.replace('" target="_blank" class="float_right"><em class="download-button',chr(10))
	
	http=p.sub('', http)
	
	return http
	
def inputbox():
	skbd = xbmc.Keyboard()
	skbd.setHeading('Поиск:')
	skbd.doModal()
	if skbd.isConfirmed():
		SearchStr = skbd.getText()
		return SearchStr
	else:
		return ""

def upd(category, sort, text, n=1):
	if text=='0':
		stext=""
	else:
		stext=inputbox()
		n=1
	stext=stext.replace("%", "%20").replace(" ", "%20").replace("?", "%20").replace("#", "%20")
	if stext=="":
		categoryUrl = xt('http://www.fast-torrent.org/'+category+'/'+str(n)+'.html')
	else:
		categoryUrl = 'http://www.fast-torrent.org/'+category+'/'+stext+'/'+str(n)+'.html'#search/
	#print categoryUrl
	http = GET(categoryUrl, httpSiteUrl, None)
	
	if http == None:
		showMessage('fast-torrent:', 'Сервер не отвечает', 1000)
		return None
	else:
		LL=formtext_n(http)
		#LL=http.splitlines()
		return LL


def format(L):
	if L==None: 
		return ["","","","","","","","",""]
	else:
		Li=[]
		Ln=[]
		i=0
		
		for itm in L:
			i+=1
			if len(itm)>6:
				if itm[:4]=="flag":
					if itm[:5]=="flag2":
						Ln.append(Li)
						Li=[]
					Li.append(itm[7:])
					
		#fl = open(os.path.join( ru(LstDir),"test.txt"), "w")
		#fl.write(str(Ln))
		#fl.close()
		
		return Ln



def ShowRoot():
	
			Title = "[COLOR FFFFFF00][Поиск][/COLOR]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('search')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('2')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[COLOR FFFFFF00][Категории][/COLOR]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=ShowC'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[Все]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('popular//all')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[Фильмы]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('most-films')\
				+ '&sort=' + urllib.quote_plus('2')\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[Сериалы]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('popular-tv')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
			
			Title = "[Анимация]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('popular-multfilm')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[Телепередачи]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('popular//documentary')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[Музыка]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('popular//music')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
			
def ShowC():
			Title = "[COLOR FFFFFF00][Теги][/COLOR]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=ShowT'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[COLOR FFFFFF00][Актеры][/COLOR]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=ShowA'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[COLOR FFFFFF00][Режисcеры][/COLOR]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=ShowD'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[COLOR FFFFFF00][Жанры][/COLOR] > фильмы"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=ShowG'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[COLOR FFFFFF00][Жанры][/COLOR] > сериалы"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=ShowG'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('1')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
			
			Title = "[COLOR FFFFFF00][Жанры][/COLOR] > анимация"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=ShowG'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('2')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
			
			Title = "[COLOR FFFFFF00][Жанры][/COLOR] > телепередачи"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=ShowG'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('3')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[COLOR FFFFFF00][Жанры][/COLOR] > музыка"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=ShowG'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('4')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)



def ShowG(k):
	
			Title = "[COLOR FFFFFF00][Поиск][/COLOR]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('popular//all')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			#xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[COLOR FF00FF00][Все категории][/COLOR]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('popular//all')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			#xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[COLOR FF00FF00][Фильмы][/COLOR]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(en_film)\
				+ '&sort=' + urllib.quote_plus('2')\
				+ '&text=' + urllib.quote_plus('0')
			#xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
			if k=="0":
				for SL in KList:
					Title = ' |- '+SL[1]
					row_url = Title
					listitem = xbmcgui.ListItem(Title)
					listitem.setInfo(type = "Video", infoLabels = {"Title": Title})
					purl = sys.argv[0] + '?mode=Search'\
						+ '&url=' + urllib.quote_plus(row_url)\
						+ '&title=' + urllib.quote_plus(Title)\
						+ '&category=' + urllib.quote_plus(SL[0])\
						+ '&sort=' + urllib.quote_plus('2')\
						+ '&text=' + urllib.quote_plus('0')
					xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[COLOR FF00FF00][Сериалы][/COLOR]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('popular-tv')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			#xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
			if k=="1":
				for SL in SList:
					Title = ' |- '+SL[1]
					row_url = Title
					listitem = xbmcgui.ListItem(Title)
					listitem.setInfo(type = "Video", infoLabels = {"Title": Title})
					purl = sys.argv[0] + '?mode=Search'\
						+ '&url=' + urllib.quote_plus(row_url)\
						+ '&title=' + urllib.quote_plus(Title)\
						+ '&category=' + urllib.quote_plus(SL[0])\
						+ '&sort=' + urllib.quote_plus('2')\
						+ '&text=' + urllib.quote_plus('0')
					xbmcplugin.addDirectoryItem(handle, purl, listitem, True)


			Title = "[COLOR FF00FF00][Анимация][/COLOR]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('popular-multfilm')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			#xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			if k=="2":
				for SL in AList:
					Title = ' |- '+SL[1]
					row_url = Title
					listitem = xbmcgui.ListItem(Title)
					listitem.setInfo(type = "Video", infoLabels = {"Title": Title})
					purl = sys.argv[0] + '?mode=Search'\
						+ '&url=' + urllib.quote_plus(row_url)\
						+ '&title=' + urllib.quote_plus(Title)\
						+ '&category=' + urllib.quote_plus(SL[0])\
						+ '&sort=' + urllib.quote_plus('2')\
						+ '&text=' + urllib.quote_plus('0')
					xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[COLOR FF00FF00][Телепередачи][/COLOR]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('popular//documentary')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			#xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
			if k=="3":
				for SL in TList:
					Title = ' |- '+SL[1]
					row_url = Title
					listitem = xbmcgui.ListItem(Title)
					listitem.setInfo(type = "Video", infoLabels = {"Title": Title})
					purl = sys.argv[0] + '?mode=Search'\
						+ '&url=' + urllib.quote_plus(row_url)\
						+ '&title=' + urllib.quote_plus(Title)\
						+ '&category=' + urllib.quote_plus(SL[0])\
						+ '&sort=' + urllib.quote_plus('2')\
						+ '&text=' + urllib.quote_plus('0')
					xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[COLOR FF00FF00][Музыка][/COLOR]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('popular//music')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			#xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
			if k=="4":
				for SL in MList:
					Title = ' |- '+SL[1]
					row_url = Title
					listitem = xbmcgui.ListItem(Title)
					listitem.setInfo(type = "Video", infoLabels = {"Title": Title})
					purl = sys.argv[0] + '?mode=Search'\
						+ '&url=' + urllib.quote_plus(row_url)\
						+ '&title=' + urllib.quote_plus(Title)\
						+ '&category=' + urllib.quote_plus(SL[0])\
						+ '&sort=' + urllib.quote_plus('2')\
						+ '&text=' + urllib.quote_plus('0')
					xbmcplugin.addDirectoryItem(handle, purl, listitem, True)


def ShowT():
	
			Title = "[COLOR FFFFFF00][Поиск][/COLOR]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('popular//all')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			#xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[COLOR FF00FF00][Все категории][/COLOR]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('popular//all')\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			for SL in TgList:
					Title = ' |- '+SL[1]
					row_url = Title
					listitem = xbmcgui.ListItem(Title)
					listitem.setInfo(type = "Video", infoLabels = {"Title": Title})
					purl = sys.argv[0] + '?mode=Search'\
						+ '&url=' + urllib.quote_plus(row_url)\
						+ '&title=' + urllib.quote_plus(Title)\
						+ '&category=' + urllib.quote_plus(SL[0])\
						+ '&sort=' + urllib.quote_plus('2')\
						+ '&text=' + urllib.quote_plus('0')
					xbmcplugin.addDirectoryItem(handle, purl, listitem, True)


def ShowA():
			for SL in da:
					Title = xt(SL)
					row_url = Title
					listitem = xbmcgui.ListItem(Title)
					listitem.setInfo(type = "Video", infoLabels = {"Title": Title})
					purl = sys.argv[0] + '?mode=Search'\
						+ '&url=' + urllib.quote_plus("row_url")\
						+ '&title=' + urllib.quote_plus("Title")\
						+ '&category=' + urllib.quote_plus("video/actor/"+da[SL])\
						+ '&sort=' + urllib.quote_plus('2')\
						+ '&text=' + urllib.quote_plus('0')
					xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

def ShowD():
			for SL in dr:
					
					NameMode = __settings__.getSetting("Name Mode")
					if NameMode == '1': 
						k1=SL.rfind(' ')
						Title=SL[k1:]+" "+SL[:k1+1]
					else: Title = SL

					row_url = Title
					listitem = xbmcgui.ListItem(Title)
					listitem.setInfo(type = "Video", infoLabels = {"Title": Title})
					purl = sys.argv[0] + '?mode=Search'\
						+ '&url=' + urllib.quote_plus("row_url")\
						+ '&title=' + urllib.quote_plus("Title")\
						+ '&category=' + urllib.quote_plus("video/actor/"+dr[SL])\
						+ '&sort=' + urllib.quote_plus('2')\
						+ '&text=' + urllib.quote_plus('0')
					xbmcplugin.addDirectoryItem(handle, purl, listitem, True)




def clearinfo2(str):
	str=str.replace(chr(13)+chr(10),chr(10))
	str=str.replace(chr(10)+chr(13),chr(10))
	
	str=str.replace('<b>',"").replace('</b>',"")
	str=str.replace('<i>',"").replace('</i>',"")
	str=str.replace('<u>',"").replace('</u>',"")
	str=str.replace('<tr>',"").replace('</tr>',"")
	str=str.replace('<td>',"").replace('</td>',"")
	str=str.replace('<table>',"").replace('</table>',"")
	str=str.replace('<a',"").replace('</a>',"")
	str=str.replace('<br />',"")
	str=str.replace('<hr />',"")
	str=str.replace('<li> ',"")
	str=str.replace('</span>',"")
	str=str.replace('<font size="3">',"").replace('</font>',"")
	str=str.replace('<font size="4">',"")
	str=str.replace('<font size="5">',"")
	
	str=str.replace('<span style="color:chocolate;">',"")
	str=str.replace('<span style="color:green;">',"")
	str=str.replace('<span style="color:indigo;">',"")
	str=str.replace('<span style="color:blue;">',"")
	str=str.replace('<span style="color:maroon;">',"")
	str=str.replace('<span style="color:brown;">',"")
	str=str.replace('<span style="color:darkgreen;">',"")
	
	str=str.replace("<td class='header'>","")
	
	#str=str.replace('<img src="',chr(10)+'Обложка: "')
	#str=str.replace('<td style="vertical-align:top;"><img src="', 'Обложка: "')
	str=str.replace(' style="float:right;" />',"")
	str=str.replace('" />','"')
	
	str=str.replace('О фильме:'+chr(10), chr(10)+'О фильме: ')
	str=str.replace('О фильме: '+chr(10), chr(10)+'О фильме: ')
	str=str.replace('О фильме:  '+chr(10), chr(10)+'О фильме: ')
	str=str.replace('О фильме:   '+chr(10), chr(10)+'О фильме: ')
	
	str=str.replace('<div class="hidewrap"><div class="hidehead" onclick="hideshow($(this))">',"")
	str=str.replace('</div><div class="hidebody"></div><textarea class="hidearea"> href="',': ["')
	str=str.replace('<td class="header">',"")
	str=str.replace(' /></textarea></div>',"]")
	str=str.replace('</textarea></div>',"]")
	str=str.replace(' target="_blank"><img src=',",")
	str=str.replace('"'+chr(10)+'<img src="', "','")
	str=str.replace(' />  href=',",")
	str=str.replace('"  href="',",")
	str=str.replace('href="/tag/7/" target="_blank">',"")
	str=str.replace('href="/tag/6/" target="_blank">',"")
	str=str.replace('href="/tag/5/" target="_blank">',"")
	str=str.replace('href="/tag/4/" target="_blank">',"")
	str=str.replace('href="/tag/3/" target="_blank">',"")
	str=str.replace('href="/tag/2/" target="_blank">',"")
	str=str.replace('href="/tag/1/" target="_blank">',"")
	
	str=str.replace('О фильме:',chr(10)+"О фильме:")
	str=str.replace('Год выхода:',chr(10)+"Год выхода:")
	str=str.replace('Описание:',chr(10)+"Описание:")
	str=str.replace('Название:',chr(10)+"Название:")
	str=str.replace('Жанр:',chr(10)+"Жанр:")
	str=str.replace('Режиссер:',chr(10)+"Режиссер:")
	#n=str.find("http://mediaget.com/torrent")
	n=str.find('<table id="details">')
	k=str.rfind("Сидер замечен")
	str=str[n:k]
	try:
		i=str.find('Информация о фильме')
		j=str.find('.jpg')
		k=str.find('.png')
		if i>0: 
			tmp=str[:i]
			i2=tmp.rfind('.')+4
			i1=tmp.rfind('http:')
			tmp=tmp[i1:i2]
			ext=tmp[-3:]
			if ext=="jpe":tmp=tmp+"g"
			str=str.replace('Информация о фильме', chr(10)+'Обложка: "'+tmp+'"')
		elif j>0:
			tmp=str[:j+4]
			i1=tmp.rfind('http:')
			tmp=tmp[i1:]
			str=chr(10)+'Обложка: "'+tmp+'"'+chr(10)+str
		elif k>0:
			tmp=str[:k+4]
			i1=tmp.rfind('http:')
			tmp=tmp[i1:]
			str=chr(10)+'Обложка: "'+tmp+'"'+chr(10)+str
		else:
			str=str.replace('<img src="', chr(10)+'Обложка: "',1)
	except:
		str=str.replace('<img src="', chr(10)+'Обложка: "',1)
	str=p.sub('', str)
	return str


def clearinfo(str):
	n=str.find('<table id="details">')
	k=str.rfind("Сидер замечен")
	str=str[n:k]
	str=str.replace(chr(13)+chr(10),chr(10))
	str=str.replace(chr(10)+chr(13),chr(10))
	str=str.replace(chr(13),chr(10))
	
	str=str.replace('Год выхода:',chr(10)+"Год выхода:")
	str=str.replace('Год выпуска',chr(10)+"Год выхода:")
	str=str.replace('Описание:',chr(10)+"Описание:")
	str=str.replace('Краткое описание:',chr(10)+"Описание:")
	str=str.replace('О фильме:',chr(10)+"Описание:")
	str=str.replace('Название:',chr(10)+"Название:")
	str=str.replace('Жанр:',chr(10)+"Жанр:")
	str=str.replace('Режиссер:',chr(10)+"Режиссер:")

	try:
		i=str.find('Информация о фильме')
		if i<0:
			m=str.find('Год выхода')
			if m>0:
				s=str[:m]
				j=s.find('.jpg')
				k=s.find('.png')
				n=s.find('jpeg')
			else:
				j=str.find('.jpg')
				k=str.find('.png')
				n=str.find('jpeg')
		if i>0:
			tmp=str[:i]
			i2=tmp.rfind('.')+4
			i1=tmp.rfind('http:')
			tmp=tmp[i1:i2]
			ext=tmp[-3:]
			if ext=="jpe":tmp=tmp+"g"
			str=str.replace('Информация о фильме', chr(10)+'Обложка: '+tmp+chr(10))
		elif j>0:
			tmp=str[:j+4]
			i1=tmp.rfind('http:')
			tmp=tmp[i1:]
			str=chr(10)+'Обложка: '+tmp+chr(10)+str
		elif k>0:
			tmp=str[:k+4]
			i1=tmp.rfind('http:')
			tmp=tmp[i1:]
			str=chr(10)+'Обложка: '+tmp+chr(10)+str
		elif n>0:
			tmp=str[:n+4]
			i1=tmp.rfind('http:')
			tmp=tmp[i1:]
			str=chr(10)+'Обложка: '+tmp+chr(10)+str
		else:
			str=str.replace('<img src="', chr(10)+'Обложка: ',1)
	except:
		str=str.replace('<img src="', chr(10)+'Обложка: ',1)

	str=p.sub('', str)
	
	str=str.replace(chr(10)+chr(10)+chr(10),chr(10))
	str=str.replace(chr(10)+chr(10),chr(10))
	str=str.replace('   ',' ')
	str=str.replace('  ',' ')
	str=str.replace('О фильме:'+chr(10), chr(10)+'О фильме: ')
	str=str.replace('О фильме: '+chr(10), chr(10)+'О фильме: ')
	str=str.replace('Описание:'+chr(10), chr(10)+'Описание: ')
	str=str.replace('Описание: '+chr(10), chr(10)+'Описание: ')
	str=str.replace('Оценка',chr(10)+"Оценка: ")
	str=str.replace('.jpg', ".jpg"+chr(10))
	str=str.replace('.jpeg', ".jpeg"+chr(10))
	str=str.replace('.png', ".png"+chr(10))
	
	return str




def add_to_db(n, item):
		err=0
		tor_id="n"+n
		litm=str(len(item))
		try:
			cu.execute("CREATE TABLE "+tor_id+" (db_item VARCHAR("+litm+"), i VARCHAR(1));")
			c.commit()
		except: err=1
			#print "Ошибка БД"
		if err==0:
			cu.execute('INSERT INTO '+tor_id+' (db_item, i) VALUES ("'+item+'", "1");')
			c.commit()
			#c.close()

def get_inf_db(n):
		#import sqlite3 as db
		#db_name = os.path.join( addon.getAddonInfo('path'), "move_info.db" )
		#c = db.connect(database=db_name)
		#cu = c.cursor()
		tor_id="n"+n
		cu.execute(str('SELECT db_item FROM '+tor_id+';'))
		c.commit()
		info = cu.fetchall()
		#c.close()
		return info




def get_minfo(ntor):
			
			try: dict=eval(xt(get_inf_db(ntor)[0][0]))#dbi = move_info_db[ntor]
			except: #dbi = None
			
			#if dbi == None:
				hp = GET('http://www.rutor.org/torrent/'+ntor, httpSiteUrl, None)
				hp=clearinfo(hp)
				LI=hp.splitlines()
				dict={}
				cover=''
				for itm in LI:
					nc=itm.find(':')
					flag=itm[:nc]
					if flag=='Обложка': 
						cvr=itm.strip()
						dict['cover']=itm[nc+1:].strip()
					elif flag=='Название': dict['title']=itm[nc+1:].strip()
					elif flag=='Оценка': 
						nr=itm.find('из')
						try:
							dict['rating']=float(itm[nc+2:nr])
							#dict['votes']=str(int(int(itm[nc+2:nr])/2))
						except: pass
					elif flag=='Год выхода':
						try:dict['year']=int(itm.strip()[nc+1:])
						except: 
							try:dict['year']=int(itm.strip()[nc+1:nc+6])
							except: pass
					elif flag=='Жанр': dict['genre']=itm[nc+1:].strip()
					elif flag=='Режиссер': dict['director']=itm[nc+1:].strip()
					elif flag=='В ролях': 
						dict['cast']=itm[nc+1:].split(",")[:6]
					elif flag=='О фильме' or flag=='Описание': 
						dict['plot']=formating(itm[nc+1:].strip())[:1000]
						
				#move_info_db[ntor]=dict
				try:add_to_db(ntor, epr(dict))
				except:
					try:add_to_db(ntor, repr(dict).replace('"',"'"))
					except: pass

				if 1==0:
					
					fl = open(os.path.join( ru(dbDir), ntor+".py"), "w")
					fl.write('move_info_db['+ntor+']='+str(dict))
					fl.close()
				
			#else:
				#dict=move_info_db[ntor]
			#print eval(get_inf_db(ntor)[0][0])
			return dict



def Search(category, sort, text):
	HideScr = __settings__.getSetting("Hide Scr")
	HideTSnd = __settings__.getSetting("Hide TSound")
	TitleMode = __settings__.getSetting("Title Mode")
	LEnd=[]
	NP=int(sort)
	if NP<1:NP=1
	if NP==2:NP=1
	if text=='0': IT=10+NP
	else: IT=2
	#IT=1+NP 
	for n in range (NP,IT):
		RootList=upd(category, sort, text, n)
		print RootList
		#RootList=formtext_n(RL)
		#debug(str(RootList))
		if text == '000':
			Title = "[Поиск]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(category)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
			
			Title = "[Новые]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus('new-films')\
				+ '&sort=' + urllib.quote_plus(sort_data)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
		k=0
		for tTitle in RootList:
			dict=tTitle
			if 0 == 0:
			#if len(tTitle)==5:
				sids="0"
				#------------------------------------------------
				#http://media9.fast-torrent.ru/media/files/s3/dk/zx/cache/mstiteli-1_video_list.jpg
				#http://media9.fast-torrent.ru/media/files/s3/dk/zx/mstiteli-1.jpg
				try:cover=tTitle['cover']#.replace('/cache','').replace('_video_list','')
				except:cover=""
				#-------------------------------------------------
				try:
					cast2=tTitle['cast2']
					cast=tTitle['cast']
					n=len(cast)
					for i in range (0,n):
						da[str(cast[i])]=cast2[i]
					sva(da)
				except:pass
					

				try:
					director2=tTitle['director2']
					director=tTitle['director3']
					n=len(director)
					for i in range (0,n):
						dr[str(director[i])]=director2[i]
					svd(dr)
				except:pass
					

				
				try:rating=tTitle['rating']
				except:rating=""
				if rating=="":Title = "|  ----  |  "+tTitle['title']
				else:         
					if len(str(rating)[:4])>3: Title = "| "+str(rating)[:4]+" |  "+tTitle['title']
					else: Title = "| "+str(rating)[:4]+"0 |  "+tTitle['title']
				
				if TitleMode == '1': 
					k1=Title.rfind(')')
					Title=Title[:k1+1]
				elif TitleMode == '2':
					k1=Title.find('(')
					Title=Title[:k1]

				
				row_url = tTitle['url']
				if row_url in LEnd: return
				if 1==1:
					LEnd.append(row_url)
					listitem = xbmcgui.ListItem(Title, thumbnailImage=cover, iconImage=cover)
					try:listitem.setInfo(type = "Video", infoLabels = dict)
					except: pass
					#listitem.setProperty('fanart_image', cover)
					purl = sys.argv[0] + '?mode=OpenList'\
						+ '&url=' + urllib.quote_plus(row_url)\
						+ '&title=' + urllib.quote_plus(Title)\
						+ '&info=' + urllib.quote_plus(repr(dict))
					xbmcplugin.addDirectoryItem(handle, purl, listitem, True,140)

	Title = "[Далее> "+str(NP+10)+"-"+str(IT+9)+"]"
	row_url = Title
	listitem = xbmcgui.ListItem(Title)
	#listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
	purl = sys.argv[0] + '?mode=Search'\
		+ '&url=' + urllib.quote_plus(row_url)\
		+ '&title=' + urllib.quote_plus(Title)\
		+ '&category=' + urllib.quote_plus(category)\
		+ '&sort=' + urllib.quote_plus(str(IT))\
		+ '&text=' + urllib.quote_plus('0')
	if text=='0':xbmcplugin.addDirectoryItem(handle, purl, listitem, True)


def open_pl(pl_name):
	line=""
	Lurl=[]
	Ltitle=[]
	Lnum=[]
	tvlist = os.path.join(LstDir, pl_name+'.txt')
	fl = open(tvlist, "r")
	n=0
	for line in fl.xreadlines():
		n+=1
		if len(line)>5:
			pref=line[:5]
			Lurl.append(ru(line).replace(u'\n','').replace(u'\r',''))
			Lurl.append(ru(line).replace(u'\n','').replace(u'\r',''))
			Lnum.append(len(Lurl)-1)
	fl.close()
	return (Ltitle, Lurl, Lnum)

def formating(str):
	
	str=str.replace('а','a')
	str=str.replace('е','e')
	str=str.replace('ё','e')
	str=str.replace('о','o')
	str=str.replace('р','p')
	str=str.replace('с','c')
	str=str.replace('х','x')
	
	str=str.replace('А','A')
	str=str.replace('Е','E')
	str=str.replace('К','K')
	str=str.replace('М','M')
	str=str.replace('Н','H')
	str=str.replace('О','O')
	str=str.replace('Р','P')
	str=str.replace('С','C')
	str=str.replace('Т','T')
	str=str.replace('Х','X')

	return str

def format2(L):
	if L==None: 
		return ["","","","","","","","",""]
	else:
		Li=[]
		Ln=[]
		L1=[]
		qual=""
		i=0
		for itm in L:
			i+=1
			if len(itm)>6:
				if itm[:4]=="flag":
					if itm[:5]=="flag2":
						qual=itm[6:]
					if itm[:5]=="flag1":
						try:
							L1=eval(itm[6:])
							L1.append(qual)
							qual=""
							Ln.append(L1)
						except: 
							qual=""
					
		#fl = open(os.path.join( ru(LstDir),"test.txt"), "w")
		#fl.write(str(Ln))
		#fl.close()

		return Ln


def gettorlist_n(http):
	pass
	
	
	
def gettorlist(str):
	gettorlist_n(str)
	str=str.replace(chr(13)+chr(10),chr(10))
	str=str.replace(chr(10)+chr(13),chr(10))
	str=str.replace(chr(10),"")
	str=str.replace("\t","")
	str=str.replace("&nbsp;"," ")
	
	n=str.find('<div class="ordering">')
	if n<100: n=str.find('>Как скачать фильм?<')
	if n<1000:n=1000
	k=str.rfind('Сообщить о появлении в хорошем качестве')
	str=str[n:k]
	
	str=str.replace("'",'"')
	#str=str.replace("[",'(')
	#str=str.replace("]",')')
	
	str=str.replace('use_tooltip" title="',chr(10)+"flag2:")
	str=str.replace('::',chr(10))

	str=str.replace('Подробнее</a></td><td ><b>',chr(10)+"flag1:['")
	str=str.replace('Подробнее</a></td><td > ',chr(10)+"flag1:['")
	str=str.replace('Подробнее</a>',chr(10)+"flag1:['")
	str=str.replace('</div><div class="c2">',"")
	str=str.replace('</div><div class="c3">',"', '")
	str=str.replace('</div><div class="c4">',"', '")
	str=str.replace('</div><div class="c5">',"', '")
	str=str.replace('</div><div class="c6">',"', '")
	str=str.replace('</div><div class="c7">',"', '")
	str=str.replace('<font color="green" nowrap="nowrap" title="Раздают">', '')
	str=str.replace('</font><br/><font color="red" title="Качают" nowrap="nowrap">', "', '")
	
	str=str.replace('</td><td title="Открыть подробное описание торрента">',"', '")
	str=str.replace('<font color="green" nowrap="nowrap" title="Раздают">',"")
	str=str.replace('</font><br/><font color="red" title="Качают" nowrap="nowrap">',"', '")
	str=str.replace('</font></td><td class="right"><a href="',"', '")
	str=str.replace('.torrent"><img alt="Скачать"',".torrent']"+chr(10))
	str=str.replace('.torrent"><em class="download-button">',".torrent']"+chr(10))
	#debug(str)
	str=p.sub('', str)
	
	#fl = open(os.path.join( ru(LstDir),"test.txt"), "w")
	#fl.write(str)
	#fl.close()
	
	L=str.splitlines()
	Ln=format2(L)
	return Ln

def normlen(st, max):
	st=st.strip()
	if len(st) > max:
		st=st[:max]
	else:
		n=max-len(st)
		n1=int(n/2)
		n2=n-n1
		if n<4:
			pr="    "*n1
			sf="    "*n2
		elif n<5:
			pr="   "*n1
			sf="  "*n2
		elif n<6:
			pr="  "*n1
			sf=" "*n2
		else:
			pr=" "*n1
			sf=" "*n2
		st=pr+st+sf
	return st
		
		
def OpenList(url, name, dict):
	hp = GET('http://www.fast-torrent.org'+url, httpSiteUrl, None)
	
	L=gettorlist(hp)
	#L=[["","","","","","","","",""],["","","","","","","","",""]]
	#dict={}
	#cover=''
	
	if 1==1:
		
		Qual="Качество"
		Size="  Размер  "
		Lang="              Перевод              "
		SL="  Разд. / Кач.  "
		Down=" Скачан "
		Data="Дата релиза"
		n=int(name)+1
		if n>4: n=0
		if n==1: row_name =   chr(1)+"[COLOR FFFFFF00]"+Qual+"|"+Size+"|"+Lang+"|"+SL+"|"+Down+"| "+Data+"[/COLOR]"
		elif n==2: row_name = chr(1)+"[COLOR FFFFFF00]"+Size+"|"+Qual+"|"+Lang+"|"+SL+"|"+Down+"| "+Data+"[/COLOR]"
		elif n==3: row_name = chr(1)+"[COLOR FFFFFF00]"+Lang+"|"+Qual+"|"+Size+"|"+SL+"|"+Down+"| "+Data+"[/COLOR]"
		elif n==4: row_name = chr(1)+"[COLOR FFFFFF00]"+SL+  "|"+Qual+"|"+Size+"|"+Lang+"|"+Down+"| "+Data+"[/COLOR]"
		elif n==0: row_name = chr(1)+"[COLOR FFFFFF00]"+Down+"|"+Qual+"|"+Size+"|"+Lang+"|"+SL+"| "+Data+"[/COLOR]"


		
		cover=""
		listitem = xbmcgui.ListItem(ru(row_name), thumbnailImage=cover, iconImage=cover )
		#try:listitem.setInfo(type = "Video", infoLabels = dict)
		#except: pass
		#listitem.setProperty('fanart_image',cover)
		purl = sys.argv[0] + '?mode=OpenList2'\
			+ '&url=' + urllib.quote_plus(url)\
			+ '&fanart_image=' + urllib.quote_plus(cover)\
			+ '&title=' + urllib.quote_plus(str(n))\
			+ '&info=' + urllib.quote_plus('')
		xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

	
	for Li in L:
		if len(Li)!=8: Li=["","","","","","","","",""]
		if Li[0]!="": 
			Title = ""#Li[0].strip()
			Title =Title[:20]
			if len(Title)==10:   Title="          "+Title+"          "
			elif len(Title)==11: Title="         "+Title+"         "
			elif len(Title)==12: Title="        "+Title+"        "
			elif len(Title)==13: Title="       "+Title+"       "
			elif len(Title)==14: Title="      "+Title+"      "
			elif len(Title)==15: Title="     "+Title+"     "
			elif len(Title)==16: Title="    "+Title+"    "
			elif len(Title)==17: Title="   "+Title+"  "
			elif len(Title)==18: Title="  "+Title+"  "
			elif len(Title)==19: Title=" "+Title+" "
			elif len(Title)==20: Title=""+Title+""
		else: Title = ""
			
		Lang = Li[0].strip()
		Lang=Lang.replace(' (',"(")
		Lang=Lang.replace('многоголосный',"мн-гол")
		Lang=Lang.replace('двухголосный',"2-гол.")
		Lang=Lang.replace('одноголосный',"1-гол.")
		Lang=Lang.replace('дублирование',"дубл.")
		Lang=Lang.replace('закадровый',"закадр.")
		Lang=Lang.replace('полное',"полн.")
		nl=str(len(Lang))
		Lang=Lang[:40]
		if len(Lang)==3:    Lang="                   "+Lang+"                   "
		#elif len(Lang)==4:  Lang="                  "+Lang+"                   "
		#elif len(Lang)==5:  Lang="                  "+Lang+"                  "
		#elif len(Lang)==6:  Lang="                 "+Lang+"                  "
		#elif len(Lang)==7:  Lang="                 "+Lang+"                 "
		#elif len(Lang)==8:  Lang="                "+Lang+"                 "
		elif len(Lang)==9:  Lang="                "+Lang+"                 "
		elif len(Lang)==10: Lang="               "+Lang+"                 "
		elif len(Lang)==11: Lang="               "+Lang+"                "
		elif len(Lang)==12: Lang="              "+Lang+"                "
		elif len(Lang)==13: Lang="              "+Lang+"               "
		elif len(Lang)==14: Lang="             "+Lang+"               "
		elif len(Lang)==15: Lang="             "+Lang+"              "
		elif len(Lang)==16: Lang="             "+Lang+"             "
		elif len(Lang)==17: Lang="            "+Lang+"            "
		elif len(Lang)==18: Lang="           "+Lang+"            "
		elif len(Lang)==19: Lang="           "+Lang+"           "
		elif len(Lang)==20: Lang="          "+Lang+"           "
		elif len(Lang)==21: Lang="          "+Lang+"          "
		elif len(Lang)==22: Lang="         "+Lang+"          "
		elif len(Lang)==23: Lang="         "+Lang+"         "
		elif len(Lang)==24: Lang="        "+Lang+"         "
		elif len(Lang)==25: Lang="        "+Lang+"        "
		elif len(Lang)==26: Lang="       "+Lang+"        "
		elif len(Lang)==27: Lang="       "+Lang+"       "
		elif len(Lang)==28: Lang="      "+Lang+"       "
		elif len(Lang)==29: Lang="      "+Lang+"      "
		elif len(Lang)==30: Lang="     "+Lang+"      "
		elif len(Lang)==31: Lang="     "+Lang+"     "
		elif len(Lang)==32: Lang="    "+Lang+"     "
		elif len(Lang)==33: Lang="    "+Lang+"    "
		elif len(Lang)==34: Lang="   "+Lang+"    "
		elif len(Lang)==35: Lang="   "+Lang+"   "
		elif len(Lang)==36: Lang="  "+Lang+"   "
		elif len(Lang)==37: Lang="  "+Lang+"  "
		elif len(Lang)==38: Lang=" "+Lang+"  "
		elif len(Lang)==39: Lang=" "+Lang+" "
		elif len(Lang)==40: Lang=""+Lang+" "
		#Lang=nl+Lang
		Size = Li[1]
		Size=Size[:10]
		if Size.find("М")>0: Size=chr(2)+"  "+Size[:Size.find(".")]+" MБ [COLOR 00FFF000].[/COLOR]"
		#if len(Size)==4: Size="   "+Size+"    "
		#if len(Size)==5: Size="   "+Size+"   "
		#if len(Size)==6: Size="    "+Size+"   "
		#if len(Size)==7: Size="   "+Size+"    "
		if len(Size)==8: Size="  "+Size+"   "
		if len(Size)==9: Size="  "+Size+"  "
		if len(Size)==10: Size=" "+Size+" "
		if len(Size)==11: Size=" "+Size+" "


		Data = Li[2]
		Down = Li[3]
		if len(Down)==1: Down="      "+Down+"      "
		if len(Down)==2: Down="     "+Down+"     "
		if len(Down)==3: Down="    "+Down+"    "
		if len(Down)==4: Down="   "+Down+"   "
		if len(Down)==5: Down="  "+Down+"  "
		if len(Down)==6: Down=" "+Down+" "

		Sids = Li[4]
		Lich = Li[5]
		SL=Sids+Lich
		#if len(SL)==9:  SL=" "+Sids+"       "+Lich+" "
		if len(SL)==10: SL=" "+Sids+"          "+Lich+" "
		if len(SL)==11: SL=" "+Sids+"        "+Lich+" "
		if len(SL)==12: SL=" "+Sids+"      "+Lich+" "
		if len(SL)==13: SL=" "+Sids+"    "+Lich+" "
		if len(SL)==14: SL=" "+Sids+"  "+Lich+" "
		if len(SL)==15: SL=" "+Sids+""+Lich+" "
		if len(SL)==16: SL=""+Sids+""+Lich+""
			
		Urlt = Li[6].replace('<a href="', httpSiteUrl)
		Qual = Li[7].strip()
		Qual=Qual.replace('КПК',"    КПК     ")
		Qual=Qual.replace('Blu-Ray',  " Blu-Ray  ")
		Qual=Qual.replace('WebRip HD',"  WR HD   ")
		
		if len(Qual)==3:    Qual="    "+Qual+"    "
		elif len(Qual)==4:  Qual="    "+Qual+"   "
		elif len(Qual)==5:  Qual="   "+Qual+"   "
		elif len(Qual)==6:  Qual="  "+Qual+"  "
		elif len(Qual)==7:  Qual=" "+Qual+" "
		elif len(Qual)==8:  Qual=" "+Qual+" "
		elif len(Qual)==9:  Qual=""+Qual+" "
		elif len(Qual)==10: Qual=""+Qual+""
		#Qual=str(len(Li[8].strip()))+Qual
		#row_name = Qual+"|"+Size+"|"+Lang+"|"+SL+"|"+Down+"| "+Data
		if Title=="": row_name = Qual+"|"+Size+"|"+Lang+"|"+SL+"|"+Down+"| "+Data
		else: row_name = Qual+"|"+Size+"|"+Title+"|"+Lang+"|"+SL+"|"+Down+"| "+Data
			
		if n==1: row_name =   Qual+"|"+Size+"|"+Lang+"|"+SL+"|"+Down+"| "+Data
		elif n==2: row_name = Size+"|"+Qual+"|"+Lang+"|"+SL+"|"+Down+"| "+Data
		elif n==3: row_name = Lang+"|"+Qual+"|"+Size+"|"+SL+"|"+Down+"| "+Data
		elif n==4: row_name = SL+  "|"+Qual+"|"+Size+"|"+Lang+"|"+Down+"| "+Data
		elif n==0: row_name = Down+"|"+Qual+"|"+Size+"|"+Lang+"|"+SL+"| "+Data

		row_url = Urlt
		#try:cover=dict["cover"]
		#except:cover=""
		cover=""
		listitem = xbmcgui.ListItem(ru(row_name), thumbnailImage=cover, iconImage=cover )
		try:listitem.setInfo(type = "Video", infoLabels = dict)
		except: pass
		#listitem.setProperty('fanart_image',cover)
		purl = sys.argv[0] + '?mode=OpenCat'\
			+ '&url=' + urllib.quote_plus(row_url)\
			+ '&fanart_image=' + urllib.quote_plus(cover)\
			+ '&title=' + urllib.quote_plus(Title)\
			+ '&info=' + urllib.quote_plus(repr(dict))
		xbmcplugin.addDirectoryItem(handle, purl, listitem, True)


def OpenCat(url, name, dict):
	nnn=url.rfind("/")
	kurl=url[:nnn]
	kkk=kurl.rfind("/")+1
	ntor=xt(kurl[kkk:]+".torrent")
	rtpath=ru(os.path.join(LstDir, ntor))
	xtpath=xt(os.path.join(LstDir, ntor))
	try:
		urllib.urlretrieve(xt('http://www.fast-torrent.org'+kurl+'/'+ntor),rtpath)
	except:
		urllib.urlretrieve(xt('http://www.fast-torrent.org'+kurl+'/'+ntor),xtpath)
	playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	playlist.load(xtpath)
	Ltitle, Lurl, Lnum = [],[],[]
	n=0
	
	for i in range (len(playlist)):
		p=playlist[i]
		n+=1
		Ltitle.append(p.getdescription())
		Lurl.append(p.getfilename())
		Lnum.append(n-1)
		
	lgl=(Ltitle, Lurl, Lnum)
	for i in range (len(Ltitle)):
		#Title = formating(Ltitle[i])
		row_name = Ltitle[i]
		row_url = Lurl[i]
		try:cover=dict["cover"]
		except:cover=""
		listitem = xbmcgui.ListItem(row_name, thumbnailImage=cover, iconImage=cover )
		try:listitem.setInfo(type = "Video", infoLabels = dict)
		except: pass
		listitem.setProperty('fanart_image',cover)
		purl = sys.argv[0] + '?mode=OpenPage'\
			+ '&url=' + urllib.quote_plus(row_url)\
			+ '&fanart_image=' + urllib.quote_plus(cover)\
			+ '&num=' + urllib.quote_plus(str(Lnum[i]))\
			+ '&lgl=' + urllib.quote_plus(repr(lgl))\
			+ '&title=' + urllib.quote_plus(Ltitle[i])\
			+ '&info=' + urllib.quote_plus(repr(dict))
		xbmcplugin.addDirectoryItem(handle, purl, listitem, False)



#xplayer=xbmc.Player(xbmc.PLAYER_CORE_AUTO)
#if os.path.isdir("d:\\TorrentStream")==1: TSpath="d:\\TorrentStream\\"
#elif os.path.isdir("c:\\TorrentStream")==1: TSpath="c:\\TorrentStream\\"
#elif os.path.isdir("e:\\TorrentStream")==1: TSpath="e:\\TorrentStream\\"
#elif os.path.isdir("f:\\TorrentStream")==1: TSpath="f:\\TorrentStream\\"
#elif os.path.isdir("g:\\TorrentStream")==1: TSpath="g:\\TorrentStream\\"
#elif os.path.isdir("h:\\TorrentStream")==1: TSpath="h:\\TorrentStream\\"
#else: TSpath="C:\\"
	
	
def OpenPage(url, name, num, Lgl, dict):
	Ltitle, Lurl, Lnum = Lgl
	playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	playlist.clear()
	try:thumb2=dict["cover"]
	except:thumb2=""
	for i in range(num,len(Lnum)):
		item = xbmcgui.ListItem(Ltitle[i], iconImage = thumb2, thumbnailImage = thumb2)
		item.setInfo(type="Video", infoLabels=dict)
		playlist.add(url=Lurl[i], listitem=item, index=-1)
	xplayer.play(playlist)
	showMessage('RuTor:', "Соединение...", 100)
	time.sleep(0.3)
	
	for i in range(0,num):
		item = xbmcgui.ListItem(Ltitle[i], iconImage = thumb2, thumbnailImage = thumb2)
		item.setInfo(type="Video", infoLabels=dict)
		playlist.add(url=Lurl[i], listitem=item, index=-1)
	p = xplayer.isPlayingVideo()
	ttl=0
	bsz=0
	while xplayer.isPlayingVideo() == 0 and ttl<20 :
	#for i in range(0,30):
		p = xplayer.isPlayingVideo()
		d = os.path.isfile(TSpath+name)
		
		if d==0:
			showMessage('RuTor:', "[COLOR FFFFF000]Поиск пиров...[/COLOR]", 100)
			ttl+=1
		elif p==0:
			sz=os.path.getsize(TSpath+name)
			pbr="I"*int(sz/(1048576*1.5))
			showMessage("[COLOR FF00FF00]Буферизация: "+str(int(sz/1048576))+" Mb[/COLOR]", "[COLOR FF00FFFF]"+pbr[:51]+"[/COLOR]",100)
			if bsz==sz: ttl+=1
			else: ttl=0
			bsz=sz
		elif p==1:
			return 0
		time.sleep(1)
		


params = get_params()
mode     = None
url      = ''
title    = ''
ref      = ''
img      = ''
num      = 0
category = '0'
sort     = '2'
text     = '0'
Lgl      = ()
info  = {}
move_info_db={}


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
try:
	num  = int(urllib.unquote_plus(params["num"]))
except:
	pass
	
try:
	category  = urllib.unquote_plus(params["category"])
except:
	pass
try:
	sort  = urllib.unquote_plus(params["sort"])
except:
	pass

try:
	text  = urllib.unquote_plus(params["text"])
except:
	pass

try:
	Lgl  = eval(urllib.unquote_plus(params["lgl"]))
except:
	pass

try:
	info  = eval(urllib.unquote_plus(params["info"]))
except:
	pass






#xplayer.play("torrentstream:")#C:\Users\Diman\AppData\Roaming\XBMC\addons\plugin.video.RuTor\playlists\179278.torrent 0")
#xplayer.stop()


if mode == None:
	ShowRoot()
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)
	
elif mode == 'Search':
	#xbmcplugin.setContent(int(sys.argv[1]), 'musicvideos')
	#try: from moveinfo_db import*
	#except:pass
	Search(category, sort, text)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)
	
	#fl = codecs.open(os.path.join( ru(addon.getAddonInfo('path')), "moveinfo_db.py"), "w",'utf8','ignore')
	#fl.write('# -*- coding: utf-8 -*-'+chr(10))
	#elm=str(move_info_db).encode('utf8','ignore')
	#fl.write('move_info_db='+elm)
	#fl.close()
	
elif mode == 'OpenList':
	OpenList(url, "0", info)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)#, True, False)
	xbmc.sleep(1)
	xbmc.executebuiltin("Container.SetViewMode(51)")

elif mode == 'OpenList2':
	OpenList(url, title, info)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(handle, True, True)
	xbmc.sleep(1)
	xbmc.executebuiltin("Container.SetViewMode(51)")

elif mode == 'ShowC':
	ShowC()
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'ShowG':
	ShowG(text)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'ShowT':
	ShowT()
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)
	
elif mode == 'ShowA':
	ShowA()
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'ShowD':
	ShowD()
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(handle)


elif mode == 'OpenCat':
	try:img=info["cover"]
	except: img=icon
	play_url({'file':url,'img':img})
	#OpenCat(url, title, info)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'OpenPage':
	OpenPage(url, title, num, Lgl, info)

elif mode == 'play_url2':
	play_url2(params)

#c.close()