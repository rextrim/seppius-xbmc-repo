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

__author__ = "DiMartino"
__settings__ = xbmcaddon.Addon(id='plugin.video.myshows')
__version__ = __settings__.getAddonInfo('version')
__plugin__ = "MyShows.ru " + __version__
__language__ = __settings__.getLocalizedString
ruName=__settings__.getSetting("ruName")
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
            try:
                return title.encode('utf-8'), jdata['episodes'][id]['title'].encode('utf-8')
            except:
                return title.encode('utf-8'), None
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
    return '%02d' % (int(intxx))

def StripName(name, list, replace=' '):
    lname=name.lower().split(' ')
    name=''
    for n in lname:
        if n not in list: name+=' '+n
    return name.strip()

def auth():
    login=__settings__.getSetting("username")
    passwd=__settings__.getSetting("password")
    if len(passwd)!=32:
        __settings__.setSetting("password",md5(passwd).hexdigest())
        passwd=__settings__.getSetting("password")
    url = 'http://api.myshows.ru/profile/login?login='+login+'&password='+passwd
    headers = {'User-Agent':'XBMC', 'Content-Type':'application/x-www-form-urlencoded'}
    try:    conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode({}), headers))
    except urllib2.HTTPError as e:
        Debug('[auth]: url - '+str(url)+'; HTTPError - '+str(e)+' ;e -'+str(e.code), True)
        if e.code in (403,404) or not login or login=='' or not passwd or passwd=='':
            if __settings__.getSetting("lastlogin")=='' or int(time.time())-int(__settings__.getSetting("lastlogin"))>60*1000:
                __settings__.setSetting( "lastlogin", str(round(time.time())) )
                dialog = xbmcgui.Dialog()
                ok=dialog.yesno( __language__(30201), __language__(30201), __language__(30202))
                if ok:
                    __settings__.openSettings()
            else:
                showMessage('HTTP - '+str(e.code), __language__(30201))
        return False
    cookie_src = conn.info().get('Set-Cookie')
    cookie_str = re.sub(r'(expires=.*?;\s|path=\/;\s|domain=\.myshows\.ru(?:,\s)?)', '', cookie_src)
    session =  cookie_str.split("=")[1].split(";")[0].strip()
    su_pass =  cookie_str.split("=")[-1].split(";")[0].strip()
    cookie='SiteUser[login]='+login+'; SiteUser[password]='+su_pass+'; PHPSESSID='+session
    __settings__.setSetting( "cookie_auth", cookie )
    __settings__.setSetting( "lastlogin", str(round(time.time())) )
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
        if array=='': array=True
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
    except:
        return False

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
    cur.execute('create table watched(addtime integer, rating integer, id varchar(32) PRIMARY KEY)')
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
    if not scan.get(): scan.add()
    try:
        if scan.get() \
            and int(time.time())-scan.get()>refresh_period*3600:
            scan.delete()
            scan.add()
            ScanAll()
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
            if re.search('profile', refresh_url):
                CacheDB(unicode('http://api.myshows.ru/profile/episodes/unwatched/')).delete()
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
            if self.refresh==True or not xbmcvfs.File(self.filename, 'r').size():
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
        self.data=get_url(self.cookie, self.url)
        if self.data:
            try:
                self.fw = xbmcvfs.File(self.filename, 'w')
            except:
                self.fw = open(self.filename, 'w')
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

def friend_xbmc():
    login=__settings__.getSetting("username").decode('utf-8','ignore')
    filename=os.path.join(__tmppath__, '%s.txt' %(login))
    if xbmcvfs.File(filename, 'r').size():
        return True
    socket.setdefaulttimeout(3)
    scan=CacheDB(login)
    if scan.get() and int(time.time())-scan.get()>refresh_period*3600 or not scan.get():
        scan.delete()
        scan.add()
        url='http://myshows.ru/xbmchub?friend-me'
        ok=Data(cookie_auth, url, '').get()
        try:
            if ok or not ok:
                try:
                    fw = xbmcvfs.File(filename, 'w')
                except:
                    fw = open(filename, 'w')
                fw.write(str(ok))
                fw.close()
                return True
            else:
                return False
        except:
            Debug('[friend_xbmc] Something went wrong!')
            return False

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

    text=sortext(l)
    newl=[]
    for li in l: newl.append(cutStr(li[0:len(li)-1-len(li.split('.')[-1])]))
    l=newl

    text1 = cutStr(text[0][0:len(text[0])-1-len(text[0].split('.')[-1])])
    text2 = cutStr(text[1][0:len(text[1])-1-len(text[1].split('.')[-1])])
    sep_file=" "
    result=list(d.compare(text1.split(sep_file), text2.split(sep_file)))
    Debug('[cutFileNames] '+unicode(result))

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
        if cutStr(fl[0:len(start)])==cutStr(start): fl=fl[len(start):]
        if cutStr(fl[len(fl)-len(end):])==cutStr(end): fl=fl[0:len(fl)-len(end)]
        try:
            isinstance(int(fl.split(sep_file)[0]), int)
            fl=fl.split(sep_file)[0]
        except:pass
        l.append(fl)
    Debug('[cutFileNames] [sorted l]  '+unicode(sorted(l,key=lambda x:x)), True)
    return l

def cutStr(s):
    return str(s).replace('.',' ').replace('_',' ').replace('[',' ').replace(']',' ').lower().strip()

def sortext(filelist):
    result={}
    for name in filelist:
        ext=name.split('.')[-1]
        try:result[ext]=result[ext]+1
        except: result[ext]=1
    lol=result.viewitems()
    lol=sorted(lol, key=lambda x: x[1])
    Debug('[sortext]: lol:'+str(lol))
    popext=lol[-1][0]
    result,i=[],0
    for name in filelist:
        if name.split('.')[-1]==popext:
            result.append(name)
            i=i+1
    result=sweetpair(result)
    Debug('[sortext]: result:'+str(result))
    return result

def sweetpair(l):
    from difflib import SequenceMatcher
    s = SequenceMatcher()
    ratio=[]
    for i in range(0, len(l)): ratio.append(0)
    for i in range(0, len(l)):
        for p in range(0, len(l)):
            s.set_seqs(l[i], l[p])
            ratio[i]=ratio[i]+s.quick_ratio()
    id1,id2=0,0
    for i in range(0, len(l)):
        if ratio[id1]<=ratio[i] and i!=id2 or id2==id1 and ratio[id1]==ratio[i]:
            id2=id1
            id1=i
            #Debug('1 - %d %d' % (id1, id2))
        elif (ratio[id2]<=ratio[i] or id1==id2) and i!=id1:
            id2=i
            #Debug('2 - %d %d' % (id1, id2))

    Debug('[sweetpair]: id1 '+l[id1]+':'+str(ratio[id1]))
    Debug('[sweetpair]: id2 '+l[id2]+':'+str(ratio[id2]))

    return [l[id1],l[id2]]

def FileNamesPrepare(filename):
    my_season=None
    my_episode=None

    try:
        if int(filename):
            my_episode=int(filename)
            Debug('[FileNamesPrepare] '+str([my_season, my_episode, filename]))
            return [my_season, my_episode, filename]
    except: pass


    urls=['s(\d+)e(\d+)','(\d+)[x|-](\d+)','E(\d+)','Ep(\d+)','\((\d+)\)']
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
            if my_season and my_season>100:my_season=None
            if my_episode and my_episode>365:my_episode=None
            Debug('[FileNamesPrepare] '+str([my_season, my_episode, filename]))
            return [my_season, my_episode, filename]

def filename2match(filename):
    results={'label':filename}
    urls=['(.+)s(\d+)e(\d+)','(.+)s(\d+)\.e(\d+)', '(.+) [\[|\(](\d+)[x|-](\d+)[\]|\)]', '(.+) (\d+)[x|-](\d+)'] #same in service
    for file in urls:
        match=re.compile(file, re.I | re.IGNORECASE).findall(filename)
        #print str(results)
        if match:
            results['showtitle'], results['season'], results['episode']=match[0]
            results['showtitle']=results['showtitle'].replace('.',' ').replace('_',' ').strip()
            Debug('[filename2match] '+str(results))
            return results
    urls=['(.+)(\d{4})\.(\d{2,4})\.(\d{2,4})','(.+)(\d{4}) (\d{2}) (\d{2})'] #same in service
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
    menu,dirs=[],[]
    try: apps=get_apps()
    except: pass
    try: action=urllib.unquote_plus(apps['argv']['action'])
    except: action=None
    try: hash=urllib.unquote_plus(apps['argv']['hash'])
    except: hash=None
    try: ind=urllib.unquote_plus(apps['argv']['ind'])
    except: ind=None
    try: tdir=urllib.unquote_plus(apps['argv']['tdir'])
    except: tdir=None

    if action:
        if action=='context':
            xbmc.executebuiltin("Action(ContextMenu)")
            return
        if (ind or ind==0) and action in ('0','3'):
            Download().setprio_simple(hash, action, ind)
        elif (ind or ind==0) and action=='play':
            p,dllist,i,folder,filename=Download().list(),Download().listfiles(hash),0,None,None
            for data in p:
                if data['id']==hash:
                    folder=data['dir']
                    break
            for data in dllist:
                if data[2]==int(ind):
                    filename=data[0]
                    break
            if isRemoteTorr():
               folder=folder.replace(__settings__.getSetting("torrent_dir"),__settings__.getSetting("torrent_replacement"))
            filename=os.path.join(folder,filename)
            xbmc.executebuiltin('xbmc.PlayMedia("'+filename.encode('utf-8')+'")')
        elif not tdir: Download().action_simple(action, hash)
        elif tdir and action in ('0','3'):
            dllist=sorted(Download().listfiles(hash), key=lambda x: x[0])
            for name,percent,ind,size in dllist:
                if '/' in name and tdir in name:
                    menu.append((hash, action, str(ind)))
            for hash, action, ind in menu: Download().setprio_simple(hash, action, ind)
            return
        xbmc.executebuiltin('Container.Refresh')
        return

    if not hash:
        for data in Download().list():
            status=" "
            if data['status'] in ('seed_pending','stopped'): status=TextBB(' [||] ','b')
            elif data['status'] in ('seeding','downloading'): status=TextBB(' [>] ','b')
            menu.append({"title":'['+str(data['progress'])+'%]'+status+data['name']+' ['+str(data['ratio'])+']', "mode":"52", "argv":{'hash':str(data['id'])}})
    elif not tdir:
        dllist=sorted(Download().listfiles(hash), key=lambda x: x[0])
        for name,percent,ind,size in dllist:
            if '/' not in name:
                menu.append({"title":'['+str(percent)+'%]'+'['+str(size)+'] '+name, "mode":"52", "argv":{'hash':hash,'ind':str(ind),'action':'context'}})
            else:
                tdir=name.split('/')[0]
                #tfile=name[len(tdir)+1:]
                if tdir not in dirs: dirs.append(tdir)
    elif tdir:
        dllist=sorted(Download().listfiles(hash), key=lambda x: x[0])
        for name,percent,ind,size in dllist:
            if '/' in name and tdir in name:
                menu.append({"title":'['+str(percent)+'%]'+'['+str(size)+'] '+name[len(tdir)+1:], "mode":"52", "argv":{'hash':hash,'ind':str(ind),'action':'context'}})

    for i in dirs:
        argv={'hash':hash,'tdir':i}
        link=Link("52", argv)
        h=Handler(int(sys.argv[1]), link)
        popup=[]
        folder=True
        actions=[('3', __language__(30281)),('0', __language__(30282))]
        for a,title in actions:
            argv['action']=a
            popup.append((Link("52", argv),title))
        h.item(link, title=unicode(i), popup=popup, popup_replace=True, folder=folder)

    for i in menu:
        link=Link(i['mode'], i['argv'])
        h=Handler(int(sys.argv[1]), link)
        popup=[]
        if not hash:
            actions=[('start', __language__(30281)),('stop', __language__(30282)),('remove',__language__(30283)),('removedata', __language__(30284)),]
            folder=True
        else:
            actions=[('3', __language__(30281)),('0', __language__(30282)),('play', __language__(30227))]
            folder=False
        for a,title in actions:
            i['argv']['action']=a
            popup.append((Link(i['mode'], i['argv']),title))
        h.item(link, title=unicode(i['title']), popup=popup, popup_replace=True, folder=folder)

def torrent_dir():
    KB = xbmc.Keyboard()
    KB.setHeading(__language__(30153))
    KB.setDefault(__settings__.getSetting("torrent_dir"))
    KB.doModal()
    if (KB.isConfirmed()):
        __settings__.setSetting("torrent_dir", KB.getText())

class PluginStatus():
    def __init__(self):
        self.patchfiles=[('myshows','script.myshows','script.myshows',['notification_service.py','utilities.py','service.py','scrobbler.py']),
                ('vkstatus','xbmc-vk.svoka.com','patch_for_xbmc-vk.svoka.com_ver_1.1.0',['xbmcvkui.py','xvvideo.py']),
                ('lostfilm','plugin.video.LostFilm','patch_for_lostfilm_ver_0.4.0',['default.py']),
                ('torrenterstatus','plugin.video.torrenter','patch_for_plugin.video.torrenter_ver_1.2.7',['Core.py','Downloader.py','resources/searchers/RuTrackerOrg.py','resources/searchers/ThePirateBaySe.py',
                 'resources/searchers/NNMClubRu.py'])]
        self.status={}
        for plug in self.patchfiles:
            self.status[plug[0]]=self.check_status(plug[1],plug[2],plug[3])

        self.translate={'PATCHED':unicode(__language__(30257)),
                       'NOT PATCHED':unicode(__language__(30258)),
                       'NOT INSTALLED':unicode(__language__(30259)),}
        self.vkstatus=self.translate[self.status['vkstatus']]
        self.torrenterstatus=self.translate[self.status['torrenterstatus']]
        self.myshows=self.translate[self.status['myshows']]
        self.lostfilm=self.translate[self.status['lostfilm']]
        self.search={'vkstatus':'VK-xbmc', 'torrenterstatus':'Torrenter', 'myshows':'MyShows.ru (Service)', 'lostfilm':'Lostfilm'}

    def menu(self):
        try:
            from TSCore import TSengine as tsengine
            TSstatus=unicode(__language__(30267))
        except: TSstatus=unicode(__language__(30259))

        from torrents import TorrentDB
        from net import Download

        socket.setdefaulttimeout(3)
        if Download().list():
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
            elif action=='lostfilm':
                text=self.lostfilm
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
            elif action=='torrent_dir':
                return torrent_dir()
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
              {"title":'script.module.torrent.ts (ACE TStream): %s' % TSstatus  ,"mode":"61",   "argv":{'action':'tscheck'}},
              {"title":'plugin.video.torrenter: %s' % self.torrenterstatus  ,"mode":"61",   "argv":{'action':'torrenterstatus'}},
              {"title":'plugin.video.LostFilm: %s' % self.lostfilm  ,"mode":"61",   "argv":{'action':'lostfilm'}},
              {"title":'uTorrent WebUI: %s' % utorrentstatus  ,"mode":"61",   "argv":{'action':'utorrentstatus'}},
              {"title":__language__(30153)  ,"mode":"61",   "argv":{'action':'torrent_dir'}},
              {"title":__language__(30145) + " (v. " +__version__ +")"  ,"mode":"61",   "argv":{'action':'about'}}]

        for i in menu:
            link=Link(i['mode'], i['argv'])
            h=Handler(int(sys.argv[1]), link)
            if i['argv']['action'] in self.status and self.status[i['argv']['action']]=='NOT PATCHED':
                h.item(link, title=unicode(i['title']),  popup=[(Link(i['mode']+'0', i['argv']),unicode(__language__(30286)))], popup_replace=True)
            elif i['argv']['action'] in self.status and self.status[i['argv']['action']]=='NOT INSTALLED':
                h.item(link, title=unicode(i['title']),  popup=[(Link(i['mode']+'1', i['argv']),unicode(__language__(30316)))], popup_replace=True)
            else:
                h.item(link, title=unicode(i['title']))

    def check_status(self,id,patchpath,filelist):
        import filecmp
        plugstatus=None
        try: plugpath=xbmcaddon.Addon(id).getAddonInfo('path')
        except: return "NOT INSTALLED"
        try: os.path.getsize(os.path.join(plugpath, filelist[0]))
        except:
            try: plugpath=xbmcaddon.Addon(id).getAddonInfo('path').decode('utf-8').encode('cp1251')
            except: return "NOT INSTALLED"
        try: os.path.getsize(os.path.join(__addonpath__, patchpath, filelist[0]))
        except: __addonpath__=xbmcaddon.Addon(id='plugin.video.myshows').getAddonInfo('path').decode('utf-8').encode('cp1251')
        for f in filelist:
            try:
                patch=os.path.join(__addonpath__, patchpath, f)
                original=os.path.join(plugpath, f)
                if os.path.isfile(original):
                    if not filecmp.cmp(original, patch):
                        plugstatus="NOT PATCHED"
            except: pass
        if not plugstatus: plugstatus="PATCHED"
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

    def use(self, action):
        if self.status[action] not in ('NOT INSTALLED','NOT PATCHED'):
            return True
        dialog = xbmcgui.Dialog()
        id,patchpath,filelist=None,None,None
        for plug in self.patchfiles:
            if plug[0]==action:
                id=plug[1]
                patchpath=plug[2]
                filelist=plug[3]
                break
        if id and patchpath and filelist and action:
            if self.status[action]=='NOT INSTALLED':
                ok=dialog.yesno(__language__(30316),__language__(30515),id)
                if ok:
                    self.install_plugin(action)
                    self.status[action]=self.check_status(id,patchpath,filelist)
                else:
                    return False
            if self.status[action]=='NOT PATCHED':
                ok=dialog.yesno(__language__(30316),__language__(30516),id)
                if ok:
                    self.install(action)
                    self.status[action]=self.check_status(id,patchpath,filelist)
                else:
                    return False
            return True

def saveCheckPoint():
    __settings__.setSetting("checkpoint", str(sys.argv[2]))

def gotoCheckPoint():
    xbmc.executebuiltin('XBMC.ActivateWindow(Videos,plugin://plugin.video.myshows/%s)' % (__settings__.getSetting("checkpoint")))

def smbtopath(path):
    x=path.split('@')
    if len(x)>1: path=x[1]
    else:path=path.replace('smb://','')
    return '\\\\'+path.replace('/','\\')

def PrepareFilename(filename):
    badsymb=[':','"','\\','/','\'','!','&','*','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ']
    for b in badsymb:
        filename=filename.replace(b,' ')
    return filename.rstrip('. ')

def kinorate(title,year,titleAlt=None,kinopoiskId=None):
    if kinopoiskId:
        match={'title':title.replace('"',''), 'year':str(year), 'kinopoiskId':str(kinopoiskId)}
    else:
        match={'title':title.replace('"',''), 'year':str(year)}
    if titleAlt:
        match['titleAlt']=titleAlt.replace('"','')
    try:
        xbmc.executebuiltin(
                    'xbmc.RunScript('+xbmcaddon.Addon("script.myshows").getAddonInfo("path")+os.sep+
                    'sync_exec.py,'+json.dumps(match).replace(',','|:|')+')')
    except: return False

class RateShow():
    def __init__(self, showId, watched_jdata=None):
        self.dialog = xbmcgui.Dialog()
        self.showId=showId
        self.list={}
        if watched_jdata:self.watched_jdata=watched_jdata
        else:
            watched_data= Data(cookie_auth, 'http://api.myshows.ru/profile/shows/'+str(showId)+'/',
                               'http://api.myshows.ru/profile/shows/'+str(showId)+'/')
            try:self.watched_jdata = json.loads(watched_data.get())
            except: return

    def seasonrates(self):
        jload=Data(cookie_auth, 'http://api.myshows.ru/profile/shows/').get()
        jshowdata = json.loads(jload)
        if str(self.showId) in jshowdata:
            self.list, seasonNumber=self.listSE(jshowdata[str(self.showId)]['totalEpisodes'])
            ratedict={}
            for i in self.list:
                for j in self.list[i]:
                    if self.watched_jdata.has_key(j):
                        if self.watched_jdata[j]['rating']:
                            if ratedict.has_key(i):
                                ratedict[i].append(self.watched_jdata[j]['rating'])
                            else:
                                ratedict[i]=[self.watched_jdata[j]['rating']]
            #Debug('[ratedict]:'+str(ratedict))
            for i in ratedict:
                ratedict[i]=(round(float(sum(ratedict[i]))/len(ratedict[i]),2),len(ratedict[i]))
            Debug('[ratedict]:'+str(ratedict))
        else:
            ratedict={}
        return ratedict

    def count(self):
        ratings,seasonratings=[],[]
        showId=str(self.showId)
        jload=Data(cookie_auth, 'http://api.myshows.ru/profile/shows/').get()
        jshowdata = json.loads(jload)
        self.list, seasonNumber=self.listSE(jshowdata[showId]['totalEpisodes'])
        old_rating=jshowdata[showId]['rating']
        for id in self.watched_jdata:
            if self.watched_jdata[id]['rating']:
                ratings.append(self.watched_jdata[id]['rating'])
                if id in self.list[str(seasonNumber)]:
                    seasonratings.append(self.watched_jdata[id]['rating'])
        #Debug('ratings:'+str(ratings)+'; seasonratings:'+str(seasonratings))
        if len(ratings)>0:
            rating=round(float(sum(ratings))/len(ratings),2)
        else: rating=0
        if len(seasonratings)>0:
            seasonrating=round(float(sum(seasonratings))/len(seasonratings),2)
        else: seasonrating=0
        return rating,seasonNumber,seasonrating,old_rating

    def listSE(self,maxep):
        listSE,seasonNumber={},0
        data= Data(cookie_auth, 'http://api.myshows.ru/shows/'+str(self.showId))
        jdata = json.loads(data.get())
        for id in jdata['episodes']:
            if maxep>=jdata['episodes'][id]['sequenceNumber']:
                if listSE.has_key(str(jdata['episodes'][id]['seasonNumber'])):
                    listSE[str(jdata['episodes'][id]['seasonNumber'])].append(id)
                else:
                    listSE[str(jdata['episodes'][id]['seasonNumber'])]=[id]
                if jdata['episodes'][id]['seasonNumber']>seasonNumber:
                    seasonNumber=jdata['episodes'][id]['seasonNumber']
        #Debug('[listSE] '+str(listSE)+str(seasonNumber))
        return listSE, seasonNumber

def isRemoteTorr():
    localhost=['127.0.0.1', '0.0.0.0', 'localhost']
    if __settings__.getSetting("torrent")=='0':
        if __settings__.getSetting("torrent_utorrent_host") not in localhost:
            Debug('[isRemoteTorr]: uTorrent is Remote!')
            return True
    elif __settings__.getSetting("torrent")=='1':
        if __settings__.getSetting("torrent_transmission_host") not in localhost:
            Debug('[isRemoteTorr]: Transmission is Remote!')
            return True

def season_banner(banners, season):
    import random
    try:season_banners = [banner for banner in banners if banner["bannertype"] == "season" and int(banner["season"]) == season]
    except:season_banners=[]
    if len(season_banners)>0:
        return season_banners[random.randint(0, len(season_banners)-1)]["bannerpath"]

def titlesync(id):
    title=id
    try:
        jid=json.loads(id)
        try:
            if 'showtitle' in jid and 'season' in jid and 'episode' in jid:
                title="%s S%02dE%02d" % (jid["showtitle"],jid["season"],jid["episode"])
            elif 'label' in jid:
                title=jid["label"]
        except:pass
    except:pass
    return title