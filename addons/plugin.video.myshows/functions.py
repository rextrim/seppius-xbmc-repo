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

__version__ = "1.7.2"
__plugin__ = "MyShows.ru " + __version__
__author__ = "DiMartino"
__settings__ = xbmcaddon.Addon(id='plugin.video.myshows')
__language__ = __settings__.getLocalizedString
login=__settings__.getSetting("username")
passwd=__settings__.getSetting("password")
ruName=__settings__.getSetting("ruName")
change_onclick=__settings__.getSetting("change_onclick")
cookie_auth=__settings__.getSetting("cookie_auth")
socket.setdefaulttimeout(60)
__addonpath__= __settings__.getAddonInfo('path')
icon   = __addonpath__+'/icon.png'
__tmppath__= os.path.join(__addonpath__, 'tmp')
forced_refresh_data=__settings__.getSetting("forced_refresh_data")
refresh_period=int('1|4|12|24'.split('|')[int(__settings__.getSetting("refresh_period"))])
refresh_always=__settings__.getSetting("refresh_always")
striplist=['the', 'tonight', 'show', 'with', '  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ']
debug = __settings__.getSetting("debug")

def sortcomma(dict, json):
    for x in dict:
        y=dict[x].split(',')
        dict[x]=''
        for i in y:
            if i not in json:
                dict[x]=dict[x]+','+i
        if len(dict[x])>0: dict[x]=dict[x][1:len(dict[x])]
    return dict

def Debug(msg, force = False):
    if(debug == 'true' or force):
        try:
            print "[MyShows.Ru] " + msg
        except UnicodeEncodeError:
            print "[MyShows.Ru UTF-8] " + msg.encode( "utf-8", "ignore" )

def showMessage(heading, message, times = 10000, forced=False):
    notification = __settings__.getSetting("notification")
    if debug=='true' or notification=='true' or forced:
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading.encode('utf-8'), unicode(message).encode('utf-8'), times, icon))

def id2title(showId, id=None, norus=False):
    jload=Data(cookie_auth, 'http://api.myshows.ru/shows/'+str(showId)).get()
    if jload:
        jdata = json.loads(jload)
        if ruName=='true' and jdata['ruTitle'] and not norus:
            title=jdata['ruTitle']
        else:
            title=jdata['title']
        Debug('[id2title]: '+ title)
        if id:
            return title.encode('utf-8'), jdata['episodes'][id]['title'].encode('utf-8')
        else:
            return title.encode('utf-8'), None

def id2date(showId, id):
    jload=Data(cookie_auth, 'http://api.myshows.ru/shows/'+str(showId)).get()
    if jload:
        jdata = json.loads(jload)
        if str(id) in jdata["episodes"]: return jdata["episodes"][str(id)]["airDate"]

def date2SE(showId, date):
    jload=Data(cookie_auth, 'http://api.myshows.ru/shows/'+str(showId)).get()
    if jload:
        jdata = json.loads(jload)
        for id in jdata['episodes']:
            #print jdata['episodes'][id]['airDate']+' NOT '+str(date)
            if jdata['episodes'][id]['airDate']==str(date):
                return id, jdata['episodes'][id]['seasonNumber'], jdata['episodes'][id]['episodeNumber']

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
    lname=name.lower().split(' ')
    name=''
    for n in lname:
        if n not in list: name+=' '+n
    return name.strip()

def auth():
    url = 'http://api.myshows.ru/profile/login?login='+login+'&password='+md5(passwd).hexdigest()
    headers = {'User-Agent':'XBMC', 'Content-Type':'application/x-www-form-urlencoded'}
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
    headers = { 'User-Agent':'XBMC',
                'Content-Type':'application/x-www-form-urlencoded',
                'Cookie':cookie}
    try:
        conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode({}), headers))
        array=conn.read()
        conn.close()
        return array
    except urllib2.HTTPError as e:
        if e.code==401:
            headers['Cookie']=auth()
            conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode({}), headers))
            array=conn.read()
            conn.close()
            return array
        else:
            if debug=='true': showMessage('HTTP Error', str(e.code), forced=True)
            xbmc.sleep(2000)
            return

def get_html_source(url):
    class AppURLopener(urllib.FancyURLopener):
        version = 'xxx'
    urllib._urlopener = AppURLopener()
    urllib.urlcleanup()
    sock = urllib.urlopen(url)
    htmlsource = sock.read()
    sock.close()
    return htmlsource

def get_data(cookie, url, refresh=False):
    if refresh==True:
        return get_url(cookie, url)
    else:
        pass

def post_url(cookie, url, post):
    headers = { 'User-Agent':'XBMC',
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

def ClearCache():
    dirname = xbmc.translatePath('special://temp')
    for subdir in ('xbmcup', sys.argv[0].replace('plugin://', '').replace('/', '')):
        dirname = os.path.join(dirname, subdir)
        if not xbmcvfs.exists(dirname):
            xbmcvfs.mkdir(dirname)
    dbfilename = os.path.join(dirname, 'data.db3')
    db = sqlite.connect(dbfilename)
    cur = db.cursor()
    cur.execute('delete from cache')
    db.commit()
    cur.close()
    db.close()
    xbmcgui.Dialog().ok( __language__(30208), __language__(30236))
    ontop('update')
    xbmc.executebuiltin("Action(back)")

def invert_bool(var):
    if bool(var): var=False
    else:  var=True
    return var

def getSettingAsBool(setting):
    return __settings__.getSetting(setting).lower() == "true"

class CacheDB:
    def __init__(self, url):
        dirname = xbmc.translatePath('special://temp')
        for subdir in ('xbmcup', sys.argv[0].replace('plugin://', '').replace('/', '')):
            dirname = os.path.join(dirname, subdir)
            if not xbmcvfs.exists(dirname):
                xbmcvfs.mkdir(dirname)
        self.dbfilename = os.path.join(dirname, 'data.db3')
        self.url=url
        if not xbmcvfs.exists(self.dbfilename):
            creat_db(self.dbfilename)

    def get(self):
        self._connect()
        self.cur.execute('select addtime from cache where url="'+self.url+'"')
        x=self.cur.fetchone()
        self._close()
        return x[0] if x else None

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

def auto_scan():
    from torrents import ScanAll
    scan=CacheDB('autoscan')
    try:
        if scan.get() \
            and int(time.time())-scan.get()>refresh_period*3600:
            showMessage(__language__(30277),__language__(30278))
            scan.delete()
            ScanAll()
            scan.add()
    except: showMessage(__language__(30279), __language__(30277))

class Data():
    def __init__(self, cookie_auth, url, refresh_url=None):
        if not xbmcvfs.exists(__tmppath__):
            xbmcvfs.mkdir(__tmppath__)
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
            try:self.data = self.fg.read()
            except:
                self.fg.close()
                self.fg = open(self.filename, 'r')
                self.data = self.fg.read()
            self.fg.close()
            x=re.match('.*?}$', self.data)
            if not x: self.data=self.data[0:len(self.data)-1]
            return self.data
        else: return get_url(self.cookie, self.url)

    def write(self):
        try: CacheDB(self.url).delete()
        except: pass
        self.fw = xbmcvfs.File(self.filename, 'w')
        try:self.data=get_url(self.cookie, self.url)
        except:
            self.fg.close()
            self.fw = open(self.filename, 'w')
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

def ontop(action='get', ontop=None):
    from torrents import prefix
    if action in ('update'):
        if ontop:
            jdata = json.loads(Data(cookie_auth, 'http://api.myshows.ru/profile/shows/').get())
            jstringdata=json.loads(ontop)
            showId=str(jstringdata['showId'])
            pre=prefix(showId=int(showId), seasonId=jstringdata['seasonId'])
            #if ruName=='true' and jdata[showId]['ruTitle']: title=pre+jdata[showId]['ruTitle']
            #else:
            title=pre+jdata[showId]['title']
            if jstringdata['seasonId']:
                mode="25"
                title+=' Season '+str(jstringdata['seasonId'])
            else:mode="20"
            ontop={'title':title,'mode':mode,'argv':{'stringdata':ontop}}
            #print unicode(ontop)
        __settings__.setSetting("ontop", str(ontop).encode('utf-8'))
    elif action=='get':
        x=__settings__.getSetting("ontop")
        if x!="None" and x:
            y={}
            y['mode']=re.compile("'%s': '(\d+)'" % ('mode')).findall(x)[0]
            y['argv']={}
            y['argv']['stringdata']=re.compile("{'%s': '(.+?)'}" % ('stringdata')).findall(x)[0]
            y['argv']['showId']=re.compile('"%s": (\d+),' % ('showId')).findall(y['argv']['stringdata'])[0]
            try:y['argv']['seasonNumber']=re.compile('"%s": (\d+),' % ('seasonId')).findall(y['argv']['stringdata'])[0]
            except:pass
            y['title']=re.compile("'%s': u'(.+?)'" % ('title')).findall(x)[0].encode('utf-8')
            #print unicode(y)
            return y
        else: return None

def getDirList(path, newl=None):
    l=[]
    try:
        if not newl: dirs, newl=xbmcvfs.listdir(path)
    except:
        try:
            if not newl: dirs, newl=xbmcvfs.listdir(path.decode('utf-8').encode('cp1251'))
        except:
            showMessage(__language__(30206), __language__(30280), forced=True)
            return l
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

    Debug('[cutFileNames] '+unicode(list(d.compare(text1.split(sep_file), text2.split(sep_file)))))

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
    Debug('[cutFileNames] [start] '+start)
    Debug('[cutFileNames] [end] '+end)
    for fl in newl:
        if fl[0:len(start)]==start: fl=fl[len(start):]
        if fl[len(fl)-len(end):]==end: fl=fl[0:len(fl)-len(end)]
        #fl=fl[len(start):len(fl)-len(end)] только это вместо 2 сверху
        l.append(fl)
    Debug('[cutFileNames] [cutnames] '+unicode(l))
    return l

def FileNamesPrepare(filename):
    my_season=None
    my_episode=None

    try:
        if int(filename):
            my_episode=int(filename)
            Debug('[FileNamesPrepare] '+str([my_season, my_episode, filename]))
            return [my_season, my_episode, filename]
    except: pass


    urls=['s(\d+)e(\d+)','(\d+)[x|-](\d+)','E(\d+)','\((\d{2}|\d{1})\)']
    for file in urls:
        match=re.compile(file, re.DOTALL | re.I | re.IGNORECASE).findall(filename)
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
            Debug('[FileNamesPrepare] '+str([my_season, my_episode, filename]))
            return [my_season, my_episode, filename]

def filename2match(filename):
    results={'label':filename}
    urls=['(.+)s(\d+)e(\d+)','(.+)s(\d+)\.e(\d+)', '(.+) [\[|\(](\d+)[x|-](\d+)[\]|\)]', '(.+) (\d+)[x|-](\d+)']
    for file in urls:
        match=re.compile(file, re.I | re.IGNORECASE).findall(filename)
        #print str(results)
        if match:
            results['showtitle'], results['season'], results['episode']=match[0]
            results['showtitle']=results['showtitle'].replace('.',' ').replace('_',' ').strip()
            Debug('[filename2match] '+str(results))
            return results
    urls=['(.+)(\d{4})\.(\d{2,4})\.(\d{2,4})']
    for file in urls:
        match=re.compile(file, re.I | re.IGNORECASE).findall(filename)
        if match:
            results['showtitle']=match[0][0].replace('.',' ').strip()
            results['date']='%s.%s.%s' % (match[0][3],match[0][2],match[0][1])
            Debug('[filename2match] '+str(results))
            return results

def TextBB(string, action=None, color=None):
    if action=='b':
        string='[B]'+string+'[/B]'
    return string

def jstr(s):
    if not s: s='null'
    elif not unicode(s).isnumeric(): s='"%s"'%(s)
    return str(s)

def lockView(viewId='list'):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    skinOptimizations = (
        { 'list': 50, 'info': 504,'wide': 51,'icons': 500, }, #Confluence
        { 'list': 50,'info': 51,'wide': 52,'icons': 53, } #Tra nsperency!
    )
    try: xbmc.executebuiltin("Container.SetViewMode(%s)" % str(skinOptimizations[0][viewId]))
    except: return

def uTorrentBrowser():
    from net import Download
    try: apps=get_apps()
    except: pass
    try: action=urllib.unquote_plus(apps['argv']['action'])
    except: action=None
    try: hash=urllib.unquote_plus(apps['argv']['hash'])
    except: hash=None
    try: ind=urllib.unquote_plus(apps['argv']['ind'])
    except: ind=None

    if action:
        if action=='context':
            xbmc.executebuiltin("Action(ContextMenu)")
            return
        if ind or ind==0:Download().action('action=setprio&hash=%s&p=%s&f=%s' % (hash, action, ind))
        else: Download().action('action=%s&hash=%s' % (action, hash))
        xbmc.executebuiltin('Container.Refresh')
        return

    menu=[]
    if not hash:
        for data in Download().list():
            menu.append({"title":'['+str(data['progress'])+'%] '+data['name'], "mode":"52", "argv":{'hash':str(data['id'])}})
    else:
        dllist=sorted(Download().listfiles(hash), key=lambda x: x[0])
        for s in dllist:
            menu.append({"title":'['+str(s[1])+'%] '+s[0], "mode":"52", "argv":{'hash':hash,'ind':str(s[2]),'action':'context'}})

    for i in menu:
        link=Link(i['mode'], i['argv'])
        h=Handler(int(sys.argv[1]), link)
        popup=[]
        if not hash:
            actions=[('start', __language__(30281)),('stop', __language__(30282)),('remove',__language__(30283)),('removedata', __language__(30284)),]
            folder=True
        else:
            actions=[('3', __language__(30281)),('0', __language__(30282))]
            folder=False
        for a,title in actions:
            i['argv']['action']=a
            popup.append((Link(i['mode'], i['argv']),title))
        h.item(link, title=unicode(i['title']), popup=popup, popup_replace=True, folder=folder)

class PluginStatus():
    def __init__(self):

        self.patchfiles=[('serialustatus','plugin.video.serialu.net','patch_for_plugin.video.serialu.net_ver_1.2.3',['default.py','update.py']),
                ('myshows','script.myshows','script.myshows',['notification_service.py','utilities.py','service.py','scrobbler.py']),
                ('vkstatus','xbmc-vk.svoka.com','patch_for_xbmc-vk.svoka.com_ver_0.8.2',['xbmcvkui.py','xvvideo.py']),
                ('torrenterstatus','plugin.video.torrenter','patch_for_plugin.video.torrenter_ver_1.1.8',['Core.py','Downloader.py','resources/searchers/RuTrackerOrg.py','resources/searchers/ThePirateBaySe.py',
                 'resources/searchers/NNMClubRu.py','resources/searchers/Kino_ZalTv.py','resources/searchers/icons/kino-zal.tv.png','resources/searchers/RuTorOrg.py','resources/searchers/KrasfsRu.py'])]
        self.status={}
        for plug in self.patchfiles:
            self.status[plug[0]]=self.check_status(plug[1],plug[2],plug[3])

        self.serialustatus=self.status['serialustatus']
        self.vkstatus=self.status['vkstatus']
        self.torrenterstatus=self.status['torrenterstatus']
        self.myshows=self.status['myshows']
        self.search={'serialustatus':'serialu.net', 'vkstatus':'VK-xbmc', 'torrenterstatus':'Torrenter', 'myshows':'MyShows.ru (Service)'}

    def menu(self):
        try:
            from TSCore import TSengine as tsengine
            TSstatus=unicode(__language__(30267))
        except: TSstatus=unicode(__language__(30259))

        try:
            import warnings
            warnings.filterwarnings('ignore', category=RuntimeWarning)
            import libtorrent
        except:
            self.torrenterstatus='LibTorrent '+unicode(__language__(30259))

        from torrents import TorrentDB
        from net import Download

        if Download().action('action=getsettings'):
            utorrentstatus=unicode(__language__(30147))
        else:
            utorrentstatus=unicode(__language__(30148))


        try: apps=get_apps()
        except: pass
        try: action=urllib.unquote_plus(apps['argv']['action'])
        except: action=None
        if action:
            if action=='vkstatus':
                text=self.vkstatus
            elif action=='serialustatus':
                text=self.serialustatus
            elif action=='torrenterstatus':
                text=self.torrenterstatus
                text2='Python-LibTorrent and Torrenter at http://xbmc.ru/'
            elif action=='myshows':
                text=self.myshows
                text2=unicode(__language__(30290))
            elif action=='utorrentstatus':
                text=utorrentstatus
                text2=unicode(__language__(30285))
            elif action=='tscheck':
                text='Script at http://xbmc.ru/forum/showthread.php?t=1962'
                text2='Engine at http://torrentstream.org/'
            elif action=='about':
                text=unicode(__language__(30260))
            if action not in ['tscheck', 'torrenterstatus', 'utorrentstatus']:
                if text!=unicode(__language__(30257)):
                    text2=unicode(__language__(30261))
            try:
                if not text2:
                    text2=''
            except: text2=''

            dialog = xbmcgui.Dialog()
            dialog.ok(unicode(__language__(30146)), text, text2)
            xbmc.executebuiltin("Action(back)")
            return

        menu=[{"title":__language__(30142) % len(TorrentDB().get_all()),    "mode":"50",    "argv":{'action':''}},
              {"title":'MyShows.ru (Service): %s' % self.myshows       ,"mode":"61",    "argv":{'action':'myshows',},},
              {"title":__language__(30143) % self.vkstatus       ,"mode":"61",    "argv":{'action':'vkstatus',},},
              {"title":__language__(30144) % self.serialustatus  ,"mode":"61",   "argv":{'action':'serialustatus'}},
              {"title":'script.module.torrent.ts (ACE TStream): %s' % TSstatus  ,"mode":"61",   "argv":{'action':'tscheck'}},
              {"title":'plugin.video.torrenter: %s' % self.torrenterstatus  ,"mode":"61",   "argv":{'action':'torrenterstatus'}},
              {"title":'uTorrent WebUI: %s' % utorrentstatus  ,"mode":"61",   "argv":{'action':'utorrentstatus'}},
              {"title":__language__(30145) + " (v. " +__version__ +")"  ,"mode":"61",   "argv":{'action':'about'}}]

        for i in menu:
            link=Link(i['mode'], i['argv'])
            h=Handler(int(sys.argv[1]), link)
            if i['argv']['action'] in self.status and self.status[i['argv']['action']]==unicode(__language__(30258)):
                h.item(link, title=unicode(i['title']),  popup=[(Link(i['mode']+'0', i['argv']),unicode(__language__(30286)))], popup_replace=True)
            elif i['argv']['action'] in self.status and self.status[i['argv']['action']]==unicode(__language__(30259)):
                h.item(link, title=unicode(i['title']),  popup=[(Link(i['mode']+'1', i['argv']),unicode(__language__(30316)))], popup_replace=True)
            else:
                h.item(link, title=unicode(i['title']))

    def check_status(self,id,patchpath,filelist):
        import filecmp
        plugstatus=None
        try: plugpath=xbmcaddon.Addon(id).getAddonInfo('path')
        except: return unicode(__language__(30259))
        try: os.path.getsize(os.path.join(plugpath, filelist[0]))
        except:
            try: plugpath=xbmcaddon.Addon(id).getAddonInfo('path').decode('utf-8').encode('cp1251')
            except: return unicode(__language__(30259))
        try: os.path.getsize(os.path.join(__addonpath__, patchpath, filelist[0]))
        except: __addonpath__=xbmcaddon.Addon(id='plugin.video.myshows').getAddonInfo('path').decode('utf-8').encode('cp1251')
        for f in filelist:
            try:
                patch=os.path.join(__addonpath__, patchpath, f)
                original=os.path.join(plugpath, f)
                if os.path.isfile(original):
                    if not filecmp.cmp(original, patch):
                        plugstatus=unicode(__language__(30258))
            except: pass
        if not plugstatus: plugstatus=unicode(__language__(30257))
        return plugstatus

    def install_plugin(self, action):
        xbmc.executebuiltin('XBMC.ActivateWindow(Addonbrowser,addons://search/%s)' % (self.search[action]))

    def install(self, action):
        import shutil
        plugstatus=False
        for plug in self.patchfiles:
            Debug('[PluginStatus] [install] '+unicode(plug))
            if plug[0]==action:
                id=plug[1]
                patchpath=plug[2]
                filelist=plug[3]
                break

        plugpath=xbmcaddon.Addon(id).getAddonInfo('path')
        try: os.path.getsize(os.path.join(plugpath, filelist[0]))
        except: plugpath=xbmcaddon.Addon(id).getAddonInfo('path').decode('utf-8').encode('cp1251')
        try: os.path.getsize(os.path.join(__addonpath__, patchpath, filelist[0]))
        except: __addonpath__=xbmcaddon.Addon(id='plugin.video.myshows').getAddonInfo('path').decode('utf-8').encode('cp1251')
        for f in filelist:
            try:success = shutil.copyfile(os.path.join(__addonpath__, patchpath, f), os.path.join(plugpath, f))
            except:plugstatus=True
        xbmc.executebuiltin('Container.Refresh')
        if not plugstatus: showMessage(__language__(30286), __language__(30208))
        else: showMessage(__language__(30286), __language__(30206), forced=True)

