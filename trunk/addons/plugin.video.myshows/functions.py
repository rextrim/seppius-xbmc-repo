# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, socket, datetime, time, os, json
import xbmcplugin, xbmcgui, xbmc, xbmcaddon, xbmcvfs
from app import *


try:
    from hashlib import md5
except ImportError:
    from md5 import md5

try:
    from sqlite3 import dbapi2 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite


__version__ = "1.4.1"
__plugin__ = "MyShows.ru " + __version__
__author__ = "DiMartino"
__settings__ = xbmcaddon.Addon(id='plugin.video.myshows')
__language__ = __settings__.getLocalizedString
login=__settings__.getSetting("username")
passwd=__settings__.getSetting("password")
ruName=__settings__.getSetting("ruName")
change_onclick=__settings__.getSetting("change_onclick")
cookie_auth=__settings__.getSetting("cookie_auth")
btchat_auth=__settings__.getSetting("btchat_auth")
socket.setdefaulttimeout(60)
__addonpath__= __settings__.getAddonInfo('path')
icon   = __addonpath__+'/icon.png'
__tmppath__= os.path.join(__addonpath__, 'tmp')
forced_refresh_data=__settings__.getSetting("forced_refresh_data")
refresh_period=int('1|4|12|24'.split('|')[int(__settings__.getSetting("refresh_period"))])
refresh_always=__settings__.getSetting("refresh_always")
striplist=['the', 'tonight', 'show', 'with', '  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ']


def showMessage(heading, message, times = 10000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading.encode('utf-8'), unicode(message).encode('utf-8'), times, icon))

def fdate_bigger_ldate(fdate, ldate):
    if int(fdate.split('.')[2])>int(ldate.split('.')[2]):
        return True
    elif int(fdate.split('.')[2])==int(ldate.split('.')[2]) and int(fdate.split('.')[1])>int(ldate.split('.')[1]):
        return True
    elif int(fdate.split('.')[2])==int(ldate.split('.')[2]) and int(fdate.split('.')[1])==int(ldate.split('.')[1]) and int(fdate.split('.')[0])>int(ldate.split('.')[0]):
        return True
    else: return False

def rev_date(date):
    ldate=date.split('.')
    date2=ldate[2]+'.'+ldate[1]+'.'+ldate[0]
    return date2

def dates_diff(fdate, ldate):
    try:
        if ldate=='today': x=datetime.datetime.now()
        else: x=datetime.datetime.strptime(ldate, '%d.%m.%Y')
        y=datetime.datetime.strptime(fdate, '%d.%m.%Y')
        z=x-y
    except TypeError:
        if ldate=='today': x=datetime.datetime.now()
        else: x=datetime.datetime(*(time.strptime(ldate, '%d.%m.%Y')[0:6]))
        y=datetime.datetime(*(time.strptime(fdate, '%d.%m.%Y')[0:6]))
        z=x-y
    return str(z.days)

def today_str():
    try: x=datetime.datetime.now().strftime('%d.%m.%Y')
    except TypeError:
        x=datetime.datetime(*(time.strptime(datetime.datetime.now().strftime('%d.%m.%Y'), '%d.%m.%Y')[0:6]))
        x=datetime.datetime.strftime(x, '%d.%m.%Y')
    return str(x)

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

def get_apps(paramstring=None):
    if not paramstring: paramstring=sys.argv[2]
    if len(paramstring)>=2:
        cleanapps=str(paramstring).replace('?','', 1)
        apps=json.loads(urllib.unquote_plus(cleanapps))
        return apps

def int_xx(intxx):
    if intxx==None or intxx=='None':
        return ''
    intxx=int(intxx)
    if intxx<10:
        return '0'+str(intxx)
    else:
        return str(intxx)

def StripName(name, list, replace=' '):
    name=name.lower()
    for striper in list:
        name=name.replace(striper, replace)
    return name

def auth():
    url = 'http://api.myshows.ru/profile/login?login='+login+'&password='+md5(passwd).hexdigest()
    headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3', 'Content-Type':'application/x-www-form-urlencoded'}
    try:    conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode({}), headers))
    except urllib2.HTTPError as e:
        if e.code==403 or not login or login=='' or not passwd or passwd=='':
            dialog = xbmcgui.Dialog()
            dialog.ok( __language__(30201), __language__(30201), __language__(30202))
            __settings__.openSettings()
        return False
    cookie_src = conn.info().get('Set-Cookie')
    cookie_str = re.sub(r'(expires=.*?;\s|path=\/;\s|domain=\.myshows\.ru(?:,\s)?)', '', cookie_src)
    session =  cookie_str.split("=")[1].split(";")[0].strip()
    su_pass =  cookie_str.split("=")[-1].split(";")[0].strip()
    cookie='SiteUser[login]='+login+'; SiteUser[password]='+su_pass+'; PHPSESSID='+session
    __settings__.setSetting( "cookie_auth", cookie )
    conn.close()
    return cookie

def makeapp(s):
    return urllib.quote_plus(json.dumps(s))

def get_url(cookie, url):
    headers = { 'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
                'Content-Type':'application/x-www-form-urlencoded',
                'Cookie':cookie}
    try:
        conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode({}), headers))
        array=conn.read()
        conn.close()
        return array
    except urllib2.HTTPError as e:
        if e.code==401:
            cookie=auth()
            headers = { 'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
                        'Content-Type':'application/x-www-form-urlencoded',
                        'Cookie':cookie}
            conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode({}), headers))
            array=conn.read()
            conn.close()
            return array
        else:
            showMessage('HTTP Error', str(e.code))
            xbmc.sleep(2000)

def get_data(cookie, url, refresh=False):
    if refresh==True:
        return get_url(cookie, url)
    else:
        pass

def post_url(cookie, url, post):
    headers = { 'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Connection':'keep-alive',
                'Referer':'http://www.bt-chat.com/search.php?mode=simplesearch',
                'Cookie':cookie}
    conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode(post), headers))
    array=conn.read()
    conn.close()
    return array

def creat_db(dbfilename):
    db = sqlite.connect(dbfilename)
    cur = db.cursor()
    cur.execute('pragma auto_vacuum=1')
    cur.execute('create table sources(addtime integer, filename varchar(32) PRIMARY KEY, showId integer, seasonId integer, episodeId integer, id integer, stype varchar(32))')
    cur.execute('create table cache(addtime integer, url varchar(32))')
    cur.execute('create table scan(addtime integer, filename varchar(32) PRIMARY KEY)')
    db.commit()
    cur.close()
    db.close()

def ClearCache(dbfilename):
    db = sqlite.connect(dbfilename)
    cur = db.cursor()
    #cur.execute('drop table cache')
    #cur.execute('create table cache(addtime integer, url varchar(32))')
    cur.execute('delete from cache')
    db.commit()
    cur.close()
    db.close()
    xbmcgui.Dialog().ok( __language__(30208), __language__(30236))
    xbmc.executebuiltin("Action(back)")

def invert_bool(var):
    if bool(var): var=False
    else:  var=True
    return var

class CacheDB:
    def __init__(self, url):
        self.dbfilename = os.path.join(__addonpath__, 'data.db3')
        self.url=url
        if not xbmcvfs.exists(self.dbfilename):
            creat_db(self.dbfilename)

    def get(self):
        self._connect()
        self.cur.execute('select addtime from cache where url="'+self.url+'"')
        x=self.cur.fetchone()
        self._close()
        if x: return x[0]

    def add(self):
        self._connect()
        self.cur.execute('insert into cache(addtime, url) values(?,?)', (int(time.time()), self.url))
        self.db.commit()
        self._close()

    def delete(self):
        self._connect()
        self.cur.execute('delete from cache where url="'+self.url+'"')
        self.db.commit()
        self._close()

    def _connect(self):
        self.db = sqlite.connect(self.dbfilename)
        self.cur = self.db.cursor()

    def _close(self):
        self.cur.close()
        self.db.close()

class Data():
    def __init__(self, cookie_auth, url, refresh_url=None):
        self.cookie=cookie_auth
        self.filename = self.url2filename(url)
        self.refresh=False
        if refresh_url:
            CacheDB(unicode(refresh_url)).delete()
        self.url=url
        if self.filename:
            if not xbmcvfs.exists(self.filename) \
                or forced_refresh_data=='true' \
                or not CacheDB(self.url).get() \
                or int(time.time())-CacheDB(self.url).get()>refresh_period*3600 \
                or str(refresh_always)=='true':
                self.refresh=True
                __settings__.setSetting("forced_refresh_data","false")


    def get(self):
        if self.filename:
            if self.refresh==True:
                self.write()
            self.fg = xbmcvfs.File(self.filename, 'r')
            self.data = self.fg.read()
            self.fg.close()
            x=re.match('.*?}$', self.data)
            if not x: self.data=self.data[0:len(self.data)-1]
            return self.data#[0:len(self.data)-1]
        else: return get_url(self.cookie, self.url)

    def write(self):
        try: CacheDB(self.url).delete()
        except: pass
        self.fw = xbmcvfs.File(self.filename, 'w')
        self.data=get_url(self.cookie, self.url)
        self.fw.write(self.data)
        self.fw.close()
        CacheDB(self.url).add()

    def url2filename(self, url):
        self.files=[r'shows.txt', r'showId_%s.txt', r'watched_showId_%s.txt', r'action_%s.txt']
        self.urls=['http://api.myshows.ru/profile/shows/$', 'http://api.myshows.ru/shows/(\d{1,20}?$)', 'http://api.myshows.ru/profile/shows/(\d{1,20}?)/$', 'http://api.myshows.ru/profile/episodes/(unwatched|next)/']
        self.i=-1
        for file in self.urls:
            self.i=self.i+1
            self.match=re.compile(str(file)).findall(url)
            if self.match:
                self.var=str(self.match[0])
                if str(self.files[self.i]).endswith('%s.txt'):
                    return os.path.join(__tmppath__, self.files[self.i] % (self.var))
                else:
                    return os.path.join(__tmppath__, self.files[self.i])
        return None

def getDirList(path, newl=None):
    l=[]
    if not newl: newl=os.listdir(path)
    for fl in newl:
        match=re.match('.avi|.mp4|.mkV|.flv|.mov|.vob|.wmv|.ogm|.asx|.mpg|mpeg|.avc|.vp3|.fli|.flc|.m4v', fl[int(len(fl))-4:len(fl)], re.I)
        if match:
            l.append(fl)
    return l

def cutFileNames(l):
    from difflib import Differ
    d = Differ()
    i=-1

    text1 = str(l[0])
    text2 = str(l[1])

    seps=['.|:| ', '.|:|x', ' |:|x', ' |:|-', '_|:|',]
    for s in seps:
        sep_file=str(s).split('|:|')[0]
        result=list(d.compare(text1.split(sep_file), text2.split(sep_file)))
        if len(result)>5:
            break

    print list(d.compare(text1.split(sep_file), text2.split(sep_file)))

    start=''
    end=''

    for res in result:
        if str(res).startswith('-') or str(res).startswith('+') or str(res).startswith('.?'):
            break
        start=start+str(res).strip()+sep_file
    result.reverse()
    for res in result:
        if str(res).startswith('-') or str(res).startswith('+') or str(res).startswith('?'):
            break
        end=sep_file+str(res).strip()+end


    newl=l
    l=[]
    print start
    print end
    for fl in newl:
        fl=fl[len(start):len(fl)-len(end)]
        l.append(fl)
    return l

def FileNamesPrepare(filename):
    my_season=None
    my_episode=None

    try:
        if int(filename):
            my_episode=int(filename)
            return [my_season, my_episode, filename]
    except: pass


    urls=['^(\d*)x(\d*).*?','.*?s(\d*)e(\d*).*?','.*?(\d*)-(\d*).*?','.*?E(\d*).*?']
    for file in urls:
        match=re.compile(file, re.DOTALL | re.I).findall(filename)
        if match:
            try:
                my_episode=int(match[1])
                my_season=int(match[0])
            except:
                try:
                    my_episode=int(match[0])
                except:
                    try:
                        my_episode=int(match[0][1])
                        my_season=int(match[0][0])
                    except:
                        try:
                            my_episode=int(match[0][0])
                        except: break
            return [my_season, my_episode, filename]

def TextBB(string, action=None, color=None):
    if action=='b':
        string='[B]'+string+'[/B]'
    return string

def jstr(s):
    if not s: s='null'
    elif not unicode(s).isnumeric(): s='"%s"'%(s)
    return str(s)

def PluginStatus():
    from torrents import TorrentDB
    try:
        vkpath=xbmcaddon.Addon(id='xbmc-vk.svoka.com').getAddonInfo('path')
        try: os.path.getsize(os.path.join(vkpath, 'xbmcvkui.py'))
        except: vkpath=xbmcaddon.Addon(id='xbmc-vk.svoka.com').getAddonInfo('path').decode('utf-8').encode('cp1251')
        try: os.path.getsize(os.path.join(__addonpath__, 'patch for xbmc-vk.svoka.com ver 2013-01-08', 'xbmcvkui.py'))
        except: __addonpath__=xbmcaddon.Addon(id='plugin.video.myshows').getAddonInfo('path').decode('utf-8').encode('cp1251')
        if os.path.getsize(os.path.join(vkpath, 'xbmcvkui.py'))==os.path.getsize(os.path.join(__addonpath__, 'patch for xbmc-vk.svoka.com ver 2013-01-08', 'xbmcvkui.py')) \
            and os.path.getsize(os.path.join(vkpath, 'xvvideo.py'))==os.path.getsize(os.path.join(__addonpath__, 'patch for xbmc-vk.svoka.com ver 2013-01-08', 'xvvideo.py')):
            vkstatus=unicode(__language__(30257))
        else: vkstatus=unicode(__language__(30258))
    except: vkstatus=unicode(__language__(30259))

    try:
        serialupath=xbmcaddon.Addon(id='plugin.video.serialu.net').getAddonInfo('path')
        try: os.path.getsize(os.path.join(serialupath, 'xbmcvkui.py'))
        except: serialupath=xbmcaddon.Addon(id='plugin.video.serialu.net').getAddonInfo('path').decode('utf-8').encode('cp1251')
        try: os.path.getsize(os.path.join(__addonpath__, 'patch for plugin.video.serialu.net ver 1.2.2', 'xbmcvkui.py'))
        except: __addonpath__=xbmcaddon.Addon(id='plugin.video.myshows').getAddonInfo('path').decode('utf-8').encode('cp1251')
        if os.path.getsize(os.path.join(serialupath, 'default.py'))==os.path.getsize(os.path.join(__addonpath__, 'patch for plugin.video.serialu.net ver 1.2.2', 'default.py')) \
            and os.path.getsize(os.path.join(serialupath, 'update.py'))==os.path.getsize(os.path.join(__addonpath__, 'patch for plugin.video.serialu.net ver 1.2.2', 'update.py')):
            serialustatus=unicode(__language__(30257))
        else: serialustatus=unicode(__language__(30258))
    except: serialustatus=unicode(__language__(30259))

    try: apps=get_apps()
    except: pass
    try: action=urllib.unquote_plus(apps['argv']['action'])
    except: action=None
    if action:
        if action=='vkcheck':
            text=vkstatus
        if action=='serialucheck':
            text=serialustatus
        if action=='about':
            text=unicode(__language__(30260))
        if text!=unicode(__language__(30257)):
            text2=unicode(__language__(30261))
        else:
            text2=''
        dialog = xbmcgui.Dialog()
        dialog.ok(unicode(__language__(30262)), text, text2)
        xbmc.executebuiltin("Action(back)")


    menu=[{"title":__language__(30142) % len(TorrentDB().get_all()),    "mode":"50",    "argv":{'action':''}},
          {"title":__language__(30143) % vkstatus       ,"mode":"61",    "argv":{'action':'vkcheck'}},
          {"title":__language__(30144) % serialustatus  ,"mode":"61",   "argv":{'action':'serialucheck'}},
          {"title":__language__(30145)                  ,"mode":"61",   "argv":{'action':'about'}}]
    for i in menu:
        link=Link(i['mode'], i['argv'])
        h=Handler(int(sys.argv[1]), link)
        h.item(link, title=unicode(i['title']))