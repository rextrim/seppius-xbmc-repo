#!/usr/bin/python

import httplib
import urllib
import urllib2
import re, cookielib, base64
import sys
import os
import socket

import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
import xbmcaddon

import threading
import time
import random
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from ASCore import TSengine,_TSPlayer
from urllib import unquote, quote



    
__addon__ = xbmcaddon.Addon( id = 'plugin.video.kinozal.tv' )

where=['названии','имени актера']
show=['везде','фильмы','мультфильмы','сериалы','шоу','музыку']
cshow=['0','1002','1003','1001','1006','1004']
form=['Все','DVDRip','HDRip','HD Blu-Ray и Remux', 'TVRip']
cform=['0','1','3','4','5']
filter=['Все','Золото','Серебро']
cfilter=['0','11','12']

try:
    iwhere=int(__addon__.getSetting('where'))
    ishow=int(__addon__.getSetting('show'))
    iform=int(__addon__.getSetting('form'))
    ifilter=int(__addon__.getSetting('filter'))
    querry=__addon__.getSetting('querry')
except:
    __addon__.setSetting('where','0')
    __addon__.setSetting('show','0')
    __addon__.setSetting('form','0')
    __addon__.setSetting('filter','1')
    __addon__.setSetting('querry','')


hos = int(sys.argv[1])

            

__language__ = __addon__.getLocalizedString

addon_icon    = __addon__.getAddonInfo('icon')
addon_fanart  = __addon__.getAddonInfo('fanart')
addon_path    = __addon__.getAddonInfo('path')
addon_type    = __addon__.getAddonInfo('type')
addon_id      = __addon__.getAddonInfo('id')
addon_author  = __addon__.getAddonInfo('author')
addon_name    = __addon__.getAddonInfo('name')
addon_version = __addon__.getAddonInfo('version')


def showMessage(heading, message, times = 3000, pics = addon_icon):
    try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
    except Exception, e:
        xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
        except Exception, e:
            xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )

ktv_login=__addon__.getSetting('login')
ktv_password=__addon__.getSetting('password')
ktv_folder=__addon__.getSetting('download_path')
ktv_cookies_uid=__addon__.getSetting('cookies_uid')
ktv_cookies_pass=__addon__.getSetting('cookies_pass')

if not ktv_login or not ktv_password: __addon__.openSettings()

if not ktv_cookies_uid or not ktv_cookies_pass:
    cookiejar = cookielib.CookieJar()
    urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    values = {'username': ktv_login, 'password':ktv_password}
    data = urllib.urlencode(values)
    request = urllib2.Request("http://kinozal.tv/takelogin.php", data)
    url = urlOpener.open(request)
    getted=None
    for cook in cookiejar:
        if cook.name=='uid': ktv_cookies_uid=cook.value
        if cook.name=='pass': ktv_cookies_pass=cook.value
        if cook.name=='pass': getted=True
    if getted:
        __addon__.setSetting('cookies_pass',ktv_cookies_pass)
        __addon__.setSetting('cookies_uid',ktv_cookies_uid)
    else: 
        showMessage('Ошибка','Не верен логин или пароль', 5000)   
        __addon__.openSettings()
# JSON понадобится, когда будет несколько файлов в торренте
try:
    import json
except ImportError:
    try:
        import simplejson as json
        xbmc.log( '[%s]: Error import json. Uses module simplejson' % addon_id, 2 )
    except ImportError:
        try:
            import demjson3 as json
            xbmc.log( '[%s]: Error import simplejson. Uses module demjson3' % addon_id, 3 )
        except ImportError:
            xbmc.log( '[%s]: Error import demjson3. Sorry.' % addon_id, 4 )

def construct_request(params):
    return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

def GE3T(target, post=None):
    target=target.replace(' ','+')
    print target
    result = cache.cacheFunction(GET2, target, post)
    return result
    
def GET(target, post=None):
    #print target
    try:
        req = urllib2.Request(url = target, data = post)
        req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
        req.add_header('Accept', '*/*')
        req.add_header('Accept-Language', 'ru-RU')
        resp = urllib2.urlopen(req)
        CE = resp.headers.get('content-encoding')
        http = resp.read()
        resp.close()
        return http
    except Exception, e:
        xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
        showMessage('HTTP ERROR', e, 5000)

        
def mainScreen(params):

    PlaceFolder('Главная',{'func': 'get_main', 'link':'http://kinozal.tv/'})
    PlaceFolder('Топ раздач',{'func': 'get_top'})
    PlaceFolder('Раздачи',{'func': 'get_search'})
    PlaceFolder('Поиск раздач',{'func': 'get_customsearch'})
    xbmcplugin.endOfDirectory(hos)

def PlaceLink(title,params):
    li = xbmcgui.ListItem(title)
    uri = construct_request(params)
    xbmcplugin.addDirectoryItem(hos, uri, li, False)
    
def get_custom(params):
    try:
        par=int(params['par'])
    except:
        par=None

    iwhere=int(__addon__.getSetting('where'))
    ishow=int(__addon__.getSetting('show'))
    iform=int(__addon__.getSetting('form'))
    ifilter=int(__addon__.getSetting('filter'))
    dialog = xbmcgui.Dialog()
    if par==1:
        iwhere=dialog.select('Фильтр', where)
    if par==2:
        ishow=dialog.select('Фильтр', show)
    if par==3:
        iform=dialog.select('Фильтр', form)
    if par==4:
        ifilter=dialog.select('Фильтр', filter)
    __addon__.setSetting('where',str(iwhere))
    __addon__.setSetting('show',str(ishow))
    __addon__.setSetting('form',str(iform))
    __addon__.setSetting('filter',str(ifilter))
    xbmc.executebuiltin('Container.Refresh(%s?func=get_customsearch)' % sys.argv[0])
def get_customsearch(params):
    
    try:
        par=int(params['par'])
    except:
        par=None
        

    PlaceLink('Искать в %s'%where[iwhere],{'func': 'get_custom', 'par':'1'})
    PlaceLink('Искать %s'%show[ishow],{'func': 'get_custom', 'par':'2'})
    PlaceLink('Формат: %s'%form[iform],{'func': 'get_custom', 'par':'3'})
    PlaceLink('Фильтр: %s'%filter[ifilter],{'func': 'get_custom', 'par':'4'})
    PlaceLink('Искать: %s'%querry,{'func': 'get_querry'})
    PlaceFolder('Поиск',{'func': 'get_search','s':'1'})
    xbmcplugin.endOfDirectory(hos)

    

def get_querry(params):
    skbd = xbmc.Keyboard()
    skbd.setHeading('Поиск:')
    skbd.doModal()
    if skbd.isConfirmed():
        SearchStr = skbd.getText()
        params['search']=SearchStr.replace(' ','+').decode('utf-8').encode('cp1251')
        #print params['search']
    else:
        params['search']=''
    __addon__.setSetting('querry',str(SearchStr))
    xbmc.executebuiltin('Container.Refresh(%s?func=get_customsearch)' % sys.argv[0])
def PlaceFolder(title,params):
    li = xbmcgui.ListItem(title)
    uri = construct_request(params)
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    
def get_main(params):
    http = GET(params['link'])
    beautifulSoup = BeautifulSoup(http)
    all= beautifulSoup.find('div',attrs={'class':'tp1_border'})
    cont= all.findAll('div',attrs={'class':'tp1_body'})
    for film in cont: 
        title= film.find('a')['title']
        img= film.find('a').find('img')['src']
        if 'http' not in img: img='http://kinozal.tv%s'%img
        lik=  str(film.find('a')['href']).split('=')
        torrlink= 'http://kinozal.tv/download.php/%s/[kinozal.tv]id%s.torrent'%(lik[1],lik[1])
        print torrlink
        li = xbmcgui.ListItem(title,addon_icon,img)
        uri = construct_request({
            'func': 'play',
            'torr_url':torrlink,
            'filename':'[kinozal.tv]id%s.torrent'%lik[1],
            'img':img,
            'title':title.encode('utf-8')
        })
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
    xbmcplugin.endOfDirectory(hos)
    
def get_search(params):

    try:
        g=int(__addon__.getSetting('where'))
        c=cshow[ishow]
        v=cform[iform]
        w=cfilter[ifilter]
        qu= querry.decode('utf-8').encode('cp1251')
        s=params['s']
        link='http://kinozal.tv/browse.php?s=%s&g=%s&c=%s&v=%s&d=0&w=%s&t=1&f=0'%(qu,g,c,v,w)
    except:
        link='http://kinozal.tv/browse.php?s=&g=0&c=0&v=0&d=0&w=11&t=1&f=0'
    print link
    http = GET(link)
    beautifulSoup = BeautifulSoup(http)
    cat= beautifulSoup.findAll('tr')
#	print cat
    leng=len(cat)
    for film in cat:
        try:
            
            size= film.findAll('td', attrs={'class':'s'})[1].string
            seeds= film.findAll('td', attrs={'class':'sl_s'})[0].string
            title= film.find('td', attrs={'class':'nam'}).find('a').string
            link=film.find('td', attrs={'class':'nam'}).find('a')['href']
            lik=  link.split('=')
            glink='http://kinozal.tv%s'%link
            data= GET(glink)
            dataSoup = BeautifulSoup(data)
            img= dataSoup.find('li', attrs={'class':'img'}).find('img')['src']
            if 'http' not in img: img='http://kinozal.tv%s'%img
            torrlink= 'http://kinozal.tv/download.php/%s/[kinozal.tv]id%s.torrent'%(lik[1],lik[1])
            li = xbmcgui.ListItem('%s\r\n[COLOR=22FFFFFF](seeds:%s size%s)[/COLOR]'%(title,seeds, size),addon_icon,img)
            uri = construct_request({
                'func': 'play',
                'torr_url':torrlink,
                'filename':'[kinozal.tv]id%s.torrent'%lik[1],
                'img':addon_icon,
                'title':title
            })
            xbmcplugin.addDirectoryItem(hos, uri, li, True, totalItems=leng)
    
        except: pass
    xbmcplugin.endOfDirectory(hos)

def get_top(params):

    http=GET('http://kinozal.tv/top.php')
    beautifulSoup = BeautifulSoup(http)
    cat= beautifulSoup.find('select',attrs={"class":"w100p styled"})
    cat=cat.findAll('option')
    for n in cat:
        if int(n['value']) not in [5,6,7,8,4,41,42,43,44]:
            li = xbmcgui.ListItem(n.string.encode('utf-8'),addon_icon,addon_icon)
            uri = construct_request({
                'func': 'get_top1',
                'link':'http://kinozal.tv/top.php?w=0&t=%s&d=0&f=0&s=0'%n['value']
            })
            xbmcplugin.addDirectoryItem(hos, uri, li, True)
    
   
    xbmcplugin.endOfDirectory(hos)
    
def get_top1(params):
    http = GET(params['link'])
    beautifulSoup = BeautifulSoup(http)
    content = beautifulSoup.find('div', attrs={'class': 'bx1 stable'})
    cats=content.findAll('a')
    #print cats
    for m in cats: 
        tit= m['title']
        lik=  str(m['href']).split('=')
        img=m.find('img')['src']
        if 'http' not in img: img='http://kinozal.tv%s'%img
        torrlink= 'http://kinozal.tv/download.php/%s/[kinozal.tv]id%s.torrent'%(lik[1],lik[1])
        li = xbmcgui.ListItem(tit,addon_icon,img)
        uri = construct_request({
            'func': 'play',
            'torr_url':torrlink,
            'filename':'[kinozal.tv]id%s.torrent'%lik[1],
            'img':img,
            'title':tit.encode('utf-8')
        })
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
        #print tit
    xbmcplugin.endOfDirectory(hos)
    
def get_folder(params):
    path=ktv_folder
    dirList=os.listdir(path)
    for fname in dirList:
        if re.search('[^/]+.torrent', fname):
            tit=fname
            torrlink='a'
            li = xbmcgui.ListItem(fname)
            uri = construct_request({
                'func': 'play',
                'file':fname,
                'img':None,
                'title':tit
            })
            xbmcplugin.addDirectoryItem(hos, uri, li, True)
    xbmcplugin.endOfDirectory(hos)

def play(params):
    print 'palyyy'
    filename=xbmc.translatePath(ktv_folder + params['filename'])
    ''' if os.path.isfile(filename): 
        try: 
            #f = open(filename, 'rb').read()
            yel=base64.b64encode(open(filename, 'rb').read())
            #red=f.read
            #f.close
            #print red.encode('utf-8')
        except: pass
    else:	'''
    
    cookiejar = cookielib.CookieJar()
    urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    values = {'username': ktv_login, 'password':ktv_password}
    data = urllib.urlencode(values)
    request = urllib2.Request("http://kinozal.tv/takelogin.php", data)
    url = urlOpener.open(request)
    torr_link=params['torr_url']
    urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    request = urllib2.Request(torr_link)
    print torr_link
    url = urlOpener.open(request)
    red = url.read()
    if '<!DOCTYPE HTML>' in red:
        showMessage('Ошибка','Проблема при скачивании (превышен лимит?)')
        return False
    filename=xbmc.translatePath(ktv_folder + params['filename'])
    #f = open(filename, 'wb')
    #f.write(red)
    #f.close
    yel=base64.b64encode(red)
    torr_link=yel
    start_torr(torr_link, params['img'])
    
def start_torr(torr_link,img):

    TSplayer=TSengine()
    out=TSplayer.load_torrent(torr_link,'RAW')
    if out=='Ok':
        for k,v in TSplayer.files.iteritems():
            li = xbmcgui.ListItem(urllib.unquote(k))
            
            uri = construct_request({
                't': urllib.quote(torr_link),
                'tt': k.encode('utf-8'),
                'i':v,
                'ii':urllib.quote(img),
                'func': 'addplist'
            })
            li.setProperty('IsPlayable', 'true')
            
            li.addContextMenuItems([('Добавить в плейлист', 'XBMC.RunPlugin(%s)' % uri),])
            uri = construct_request({
                'torr_url': urllib.quote(torr_link),
                'title': k,
                'ind':v,
                'img':img,
                'func': 'play_url2'
            })
            #li.addContextMenuItems([('Добавить в плейлист', 'XBMC.RunPlugin(%s?func=addplist&torr_url=%s&title=%s&ind=%s&img=%s&func=play_url2)' % (sys.argv[0],urllib.quote(torr_link),k,v,img  )),])
            xbmcplugin.addDirectoryItem(hos, uri, li)
    xbmcplugin.addSortMethod(hos, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(hos)
    TSplayer.end()

def addplist(params):

    li = xbmcgui.ListItem(params['tt'])
    uri = construct_request({
        'torr_url': params['t'],
        'title': params['tt'].decode('utf-8'),
        'ind':urllib.unquote_plus(params['i']),
        'img':urllib.unquote_plus(params['ii']),
        'func': 'play_url2'
    })
    xbmc.PlayList(xbmc.PLAYLIST_VIDEO).add(uri,li)
def play_url2(params):
    print 'play'
    torr_link=urllib.unquote(params["torr_url"])
    img=urllib.unquote_plus(params["img"])
    title=urllib.unquote_plus(params["title"])
    #showMessage('heading', torr_link, 10000)
    TSplayer=TSengine()
    out=TSplayer.load_torrent(torr_link,'RAW')
    if out=='Ok':
        lnk=TSplayer.get_link(int(params['ind']),title, img, img)
        if lnk:
           
            item = xbmcgui.ListItem(path=lnk)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)  

            while not xbmc.Player().isPlaying:
                xbmc.sleep(300)
            while TSplayer.player.active and not TSplayer.local: 
                TSplayer.loop()
                xbmc.sleep(300)
                if xbmc.abortRequested:
                    TSplayer.log.out("XBMC is shutting down")
                    break
            if TSplayer.local and xbmc.Player().isPlaying: 
                try: time1=TSplayer.player.getTime()
                except: time1=0
                
                i = xbmcgui.ListItem("***%s"%title)
                i.setProperty('StartOffset', str(time1))
                xbmc.Player().play(TSplayer.filename.decode('utf-8'),i)

        else:
            item = xbmcgui.ListItem(path='')
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, item) 
    TSplayer.end()
    xbmc.Player().stop
def get_params(paramstring):
    param=[]
    if len(paramstring)>=2:
        params=paramstring
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
    if len(param) > 0:
        for cur in param:
            param[cur] = urllib.unquote_plus(param[cur])
    return param

params = get_params(sys.argv[2])
try:
    func = params['func']
    del params['func']
except:
    func = None
    xbmc.log( '[%s]: Primary input' % addon_id, 1 )
    mainScreen(params)
if func != None:
    try: pfunc = globals()[func]
    except:
        pfunc = None
        xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
        showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
    if pfunc: pfunc(params)