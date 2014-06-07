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
__addonpath__= __settings__.getAddonInfo('path')
icon   = __addonpath__+'/icon.png'
__tmppath__= os.path.join(xbmc.translatePath('special://temp'), 'xbmcup', 'plugin.video.myshows')
forced_refresh_data=__settings__.getSetting("forced_refresh_data")
refresh_period=[1,4,12,24][int(__settings__.getSetting("refresh_period"))]
refresh_always=__settings__.getSetting("refresh_always")
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
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading.encode('utf-8').replace('"',"'"), unicode(message).replace('"',"'").encode('utf-8'), times, icon))

def id2title(showId, id=None, norus=False):
    jload=Data(cookie_auth, 'http://api.myshows.ru/shows/'+str(showId)).get(force_cache=True)
    if jload:
        jdata = json.loads(jload)
        if id and str(id) not in jdata['episodes']:
            __settings__.setSetting("forced_refresh_data","true")
            data= Data(cookie_auth, 'http://api.myshows.ru/shows/'+str(showId)).get()
            jdata = json.loads(data)
        if ruName=='true' and jdata['ruTitle'] and not norus:
            title=jdata['ruTitle']
        else:
            title=jdata['title']
        Debug('[id2title]: '+ title)
        if id:
            try:
                return title.encode('utf-8'), jdata['episodes'][str(id)]['title'].encode('utf-8')
            except:
                return title.encode('utf-8'), None
        else:
            return title.encode('utf-8'), None

def id2date(showId, id):
    jload=Data(cookie_auth, 'http://api.myshows.ru/shows/'+str(showId)).get(force_cache=True)
    if jload:
        jdata = json.loads(jload)
        if str(id) not in jdata['episodes']:
                __settings__.setSetting("forced_refresh_data","true")
                data= Data(cookie_auth, 'http://api.myshows.ru/shows/'+str(showId)).get()
                jdata = json.loads(data)
        if str(id) in jdata["episodes"]:
            return jdata["episodes"][str(id)]["airDate"]

def id2SE(showId, id):
    jload=Data(cookie_auth, 'http://api.myshows.ru/shows/'+str(showId)).get(force_cache=True)
    if jload:
        jdata = json.loads(jload)
        if str(id) not in jdata['episodes']:
                __settings__.setSetting("forced_refresh_data","true")
                data= Data(cookie_auth, 'http://api.myshows.ru/shows/'+str(showId)).get()
                jdata = json.loads(data)
        if str(id) in jdata["episodes"]:
            return jdata["episodes"][str(id)]["seasonNumber"], jdata["episodes"][str(id)]["episodeNumber"]

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
    if intxx and intxx!='None':
        return '%02d' % (int(intxx))
    else:
        return '00'

def StripName(name, list, replace=' '):
    lname=name.lower().split(' ')
    name=''
    for n in lname:
        if n not in list: name+=' '+n
    return name.strip()

def auth():
    login=__settings__.getSetting("username")
    passwd=__settings__.getSetting("password")
    if len(passwd)!=32 and passwd!='':
        __settings__.setSetting("password",md5(passwd).hexdigest())
        passwd=__settings__.getSetting("password")
    url = 'http://api.myshows.ru/profile/login?login='+login+'&password='+passwd
    headers = {'User-Agent':'XBMC', 'Content-Type':'application/x-www-form-urlencoded'}
    try:    conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode({}), headers))
    except urllib2.HTTPError as e:
        Debug('[auth]: url - '+str(url)+'; HTTPError - '+str(e)+' ;e -'+str(e.code), True)
        if e.code in (403,404) or not login or login=='' or not passwd or passwd=='':
            if __settings__.getSetting("lastlogin")=='' or float(time.time())-float(__settings__.getSetting("lastlogin"))>60*1000:
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
        #Debug('[get_url]: arr"'+str(array)+'"')
        if array=='':
            #Debug('[get_url][2]: arr=""')
            array=True
        return array
    except urllib2.HTTPError as e:
        #Debug('[get_url]: HTTPError, e.code='+str(e.code))
        if e.code==401:
            try:
                headers['Cookie']=auth()
                conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode({}), headers))
                array=conn.read()
                conn.close()
                if array=='':
                    array=True
                return array
            except:
                Debug('[get_url]: Denied! Wrong login or api is broken!')
                return
        elif e.code in [503]:
            Debug('[get_url]: Denied, HTTP Error, e.code='+str(e.code))
            return
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

    def ClearCache(self, silent=False):
        self._connect()
        self.cur.execute('delete from cache')
        self.db.commit()
        self._close()
        if not silent:
            xbmcgui.Dialog().ok( __language__(30208), __language__(30236))
            ontop('update')
            xbmc.executebuiltin("Action(back)")

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

def DownloadCache():
    useTVDB=getSettingAsBool('tvdb')
    urls=['http://api.myshows.ru/profile/shows/',
          'http://api.myshows.ru/profile/episodes/next/',
          'http://api.myshows.ru/profile/episodes/unwatched/',
          'http://api.myshows.ru/shows/top/all/',
          'http://api.myshows.ru/shows/top/male/',
          'http://api.myshows.ru/shows/top/female/',]
    titles=[]
    lang=[30100,30107,30106,30108,30109,30110]
    for l in lang: titles.append(__language__(l))

    data=Data(cookie_auth, 'http://api.myshows.ru/profile/shows/').get()
    if data:
        jdata = json.loads(data)
        count=len(jdata)

        dialog = xbmcgui.Dialog()
        ok=dialog.yesno(__language__(30548),__language__(30517) % count,__language__(30518))
        if ok:
            for showId in jdata:
                if ruName=='true' and jdata[showId]['ruTitle']:
                    title=jdata[showId]['ruTitle'].encode('utf-8')
                else:
                    title=jdata[showId]['title']
                titles.append(title)
                urls.append('http://api.myshows.ru/shows/'+showId)
                titles.append(title)
                urls.append('http://api.myshows.ru/profile/shows/'+showId+'/')

            if useTVDB:
                from search.scrapers import Scrapers
                TVDB=Scrapers()

            full_count=len(urls)
            progressBar = xbmcgui.DialogProgress()
            progressBar.create(__language__(30548), __language__(30518))
            for i in range(0,len(urls)):
                dat=Data(cookie_auth, urls[i]).get()
                if useTVDB:
                    match=re.compile('http://api.myshows.ru/shows/(\d{1,20}?$)').findall(urls[i])
                    if match:
                        jdat=json.loads(dat)
                        TVDB.scraper('tvdb', {'label':titles[i], 'search':[jdat['title'], titles[i]], 'year':str(jdat['year'])})
                iterator = int(round(i*100/full_count))
                progressBar.update(iterator, __language__(30549) % (i,full_count), titles[i])
                if progressBar.iscanceled():
                    progressBar.update(0)
                    progressBar.close()
                    break
    return

class Data():
    def __init__(self, cookie_auth, url, refresh_url=None):
        if not xbmcvfs.exists(__tmppath__):
            xbmcvfs.mkdirs(__tmppath__)
        self.cookie=cookie_auth
        self.filename = self.url2filename(url)
        self.refresh=False
        if refresh_url:
            CacheDB(unicode(refresh_url)).delete()
            if re.search('profile', refresh_url):
                CacheDB(unicode('http://api.myshows.ru/profile/episodes/unwatched/')).delete()
        self.url=url
        self.cache=CacheDB(self.url)
        if self.filename:
            if not xbmcvfs.exists(self.filename) \
                or getSettingAsBool('forced_refresh_data') \
                or not self.cache.get() \
                or int(time.time())-self.cache.get()>refresh_period*3600 \
                or str(refresh_always)=='true':
                self.refresh=True
                __settings__.setSetting("forced_refresh_data","false")

    def get(self, force_cache=False):
        if self.filename:
            if self.refresh==True and force_cache==False or not xbmcvfs.File(self.filename, 'r').size() or not re.search('='+__settings__.getSetting("username")+';', cookie_auth):
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
        if self.cache.get(): self.cache.delete()
        self.data=get_url(self.cookie, self.url)
        if self.data:
            try:
                self.fw = xbmcvfs.File(self.filename, 'w')
            except:
                self.fw = open(self.filename, 'w')
            self.fw.write(self.data)
            self.fw.close()
            self.cache.add()
        elif self.data==False:
            Debug('[Data][write] Going offline cuz no self.data '+str(self.data)+' self.filename '+self.filename)
            TimeOut().go_offline()

    def url2filename(self, url):
        self.files=[r'shows.txt', r'showId_%s.txt', r'watched_showId_%s.txt', r'action_%s.txt', r'top_%s.txt']
        self.urls=['http://api.myshows.ru/profile/shows/$', 'http://api.myshows.ru/shows/(\d{1,20}?$)', 'http://api.myshows.ru/profile/shows/(\d{1,20}?)/$', 'http://api.myshows.ru/profile/episodes/(unwatched|next)/', 'http://api.myshows.ru/shows/top/(all|male|female)/']
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
    lol=result.iteritems()
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
            results['showtitle']=results['showtitle'].replace('.',' ').replace('_',' ').strip().replace('The Daily Show','The Daily Show With Jon Stewart')
            Debug('[filename2match] '+str(results))
            return results
    urls=['(.+)(\d{4})\.(\d{2,4})\.(\d{2,4})','(.+)(\d{4}) (\d{2}) (\d{2})'] #same in service
    for file in urls:
        match=re.compile(file, re.I | re.IGNORECASE).findall(filename)
        if match:
            results['showtitle']=match[0][0].replace('.',' ').strip().replace('The Daily Show','The Daily Show With Jon Stewart')
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

    DownloadList=Download().list()
    if not DownloadList:
        showMessage(__language__(30206), __language__(30148), forced=True)
        return

    if action:
        if action=='context':
            xbmc.executebuiltin("Action(ContextMenu)")
            return
        if action=='search' and hash:
            title=None
            for data in DownloadList:
                if data['id']==hash:
                    title=data['name']
                    break
            if title:
                titles=PrepareSearch(title)
                if len(titles)>1:
                    ret=xbmcgui.Dialog().select(unicode(__language__(30101)), titles)
                else: ret=0
                if ret>-1:
                    xbmc.executebuiltin('ActivateWindow(Videos,plugin://plugin.video.myshows/?mode=19&action=%s)' % (titles[ret]))
            return
        if (ind or ind==0) and action in ('0','3'):
            Download().setprio_simple(hash, action, ind)
        elif (ind or ind==0) and action=='play':
            p,dllist,i,folder,filename=DownloadList,Download().listfiles(hash),0,None,None
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
        elif not tdir and action not in ('0','3'): Download().action_simple(action, hash)
        elif action in ('0','3'):
            dllist=sorted(Download().listfiles(hash), key=lambda x: x[0])
            for name,percent,ind,size in dllist:
                if tdir:
                    if '/' in name and tdir in name:
                        menu.append((hash, action, str(ind)))
                else:
                    menu.append((hash, action, str(ind)))
            for hash, action, ind in menu: Download().setprio_simple(hash, action, ind)
            return
        xbmc.executebuiltin('Container.Refresh')
        return

    if not hash:
        for data in DownloadList:
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
        actions=[('3', __language__(30320)),('0',__language__(30321))]
        for a,title in actions:
            argv['action']=a
            popup.append((Link("52", argv),title))
        h.item(link, title=unicode(i), popup=popup, popup_replace=True, folder=folder)

    for i in menu:
        link=Link(i['mode'], i['argv'])
        h=Handler(int(sys.argv[1]), link)
        popup=[]
        if not hash:
            actions=[('start', __language__(30281)),('stop', __language__(30282)),('remove',__language__(30283)),('search', __language__(30101)),('3', __language__(30320)),('0',__language__(30321)),('removedata', __language__(30284))]
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
                ('lostfilm','plugin.video.LostFilm','patch_for_lostfilm_ver_0.4.2',['default.py','Downloader.py']),
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

        try:
            import warnings
            warnings.filterwarnings('ignore', category=RuntimeWarning)
            import libtorrent
            libmode=unicode(__language__(30267))
        except:
            libmode=unicode(__language__(30259))

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
            elif action=='libmode':
                text=libmode
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
            elif action=='timeout':
                if TimeOut().timeout()==TimeOut().online:
                    TimeOut().go_offline(manual=True)
                else:
                    TimeOut().go_online()
                text=unicode(__language__(30546))
                text2=unicode(__language__(30545)) % TimeOut().timeout()
            if action not in ['tscheck', 'torrenterstatus', 'utorrentstatus','timeout']:
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
              {"title":__language__(30160),    "mode":"63",    "argv":{'action':''}},
              {"title":__language__(30137),    "mode":"60",    "argv":{'action':''}},
              {"title":unicode(__language__(30545)) % TimeOut().timeout()  ,"mode":"61",   "argv":{'action':'timeout'}},
              {"title":'MyShows.ru (Service): %s' % self.myshows       ,"mode":"61",    "argv":{'action':'myshows',},},
              {"title":__language__(30143) % self.vkstatus       ,"mode":"61",    "argv":{'action':'vkstatus',},},
              {"title":'script.module.torrent.ts (ACE TStream): %s' % TSstatus  ,"mode":"61",   "argv":{'action':'tscheck'}},
              {"title":'Python-LibTorrent: %s' % libmode  ,"mode":"61",   "argv":{'action':'libmode'}},
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
                        Debug('[PluginStatus][check_status]: diffrent file '+original)
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
    Debug('[smbtopath]:'+'\\\\'+path.replace('/','\\'))
    return '\\\\'+path.replace('/','\\')

def PrepareFilename(filename):
    badsymb=[':','"','\\','/','\'','!','&','*','?','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ']
    for b in badsymb:
        filename=filename.replace(b,' ')
    return filename.rstrip('. ')

def PrepareSearch(filename):
    titles=[filename]
    rstr='. -'
    badsymb=[':','"',r'\\','/',r'\'','!','&','*','_','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ','  ']
    for b in badsymb:
        filename=filename.replace(b,' ')

    filename=re.sub("\([^)]*\)([^(]*)", "\\1", filename)
    filename=re.sub("\[[^\]]*\]([^\[]*)", "\\1", filename)
    filename=filename.strip().rstrip(rstr)

    if titles[0]!=filename and filename!='': titles.insert(0,filename)

    title_array=[(u'(.+?)(Cезон|cезон|Сезон|сезон|Season|season|СЕЗОН|SEASON)',titles[0],0),
                 (u'(.+?)[sS](\d{1,2})',titles[0].replace('.',' '),0),
                 ]
    for regex, title, i in title_array:
        recomp=re.compile(regex)
        match=recomp.findall(title)
        if match:
            titles.insert(0,match[0][i].rstrip(rstr))

    return titles

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
            except:
                Debug('[RateShow] no watched_jdata1')
                return
            if not self.watched_jdata:
                Debug('[RateShow] no watched_jdata2')
                return

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

def auth_xbmc(login=None, passwd=None):
    if not login:
        login='xbmchub'
        passwd='c4a915feabca7186e589ff095b116d54'
    if len(passwd)!=32:
            passwd=md5(passwd).hexdigest()
    url = 'http://api.myshows.ru/profile/login?login='+login+'&password='+passwd
    headers = {'User-Agent':'XBMC', 'Content-Type':'application/x-www-form-urlencoded'}
    try: conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode({}), headers))
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
        return
    cookie_src = conn.info().get('Set-Cookie')
    cookie_str = re.sub(r'(expires=.*?;\s|path=\/;\s|domain=\.myshows\.ru(?:,\s)?)', '', cookie_src)
    session =  cookie_str.split("=")[1].split(";")[0].strip()
    su_pass =  cookie_str.split("=")[-1].split(";")[0].strip()
    cookie='SiteUser[login]='+login+'; SiteUser[password]='+su_pass+'; PHPSESSID='+session
    conn.close()
    return cookie

def changeDBTitle(showId):
    from utilities import xbmcJsonRequest
    shows = xbmcJsonRequest({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetTVShows', 'params': {'properties': ['title']}, 'id': 0})

    if not shows:
        Debug('[changeDBTitle]: XBMC JSON Result was empty.')
        return

    if 'tvshows' in shows:
        shows = shows['tvshows']
        Debug("[changeDBTitle]: XBMC JSON Result: '%s'" % str(shows))
    else:
        Debug("[changeDBTitle]: Key 'tvshows' not found")
        return

    if len(shows)>0:
        newtitle=id2title(showId,None,True)[0].decode('utf-8', 'ignore')
        dialog = xbmcgui.Dialog()
        dialog_items,dialog_ids=[__language__(30205)],[-1]
        shows=sorted(shows,key=lambda x:x['tvshowid'],reverse=True)
        for show in shows:
            dialog_ids.append(show['tvshowid'])
            dialog_items.append(show['title'])

        ret = dialog.select(newtitle, dialog_items)
        if ret>0:
            ok=dialog.yesno(__language__(30322),__language__(30534),__language__(30535) % (dialog_items[ret],newtitle))
            if ok:
                result=xbmcJsonRequest({'jsonrpc': '2.0', 'method': 'VideoLibrary.SetTVShowDetails', 'params': {'tvshowid': int(dialog_ids[ret]), 'title': unicode(newtitle)}, 'id': 1})
                if result in [newtitle,'OK']:
                    showMessage(__language__(30208), __language__(30536) % (newtitle), forced=True)
                else:
                    Debug("[changeDBTitle]: XBMC JSON Result: '%s'" % str(result))
        return

class TimeOut():
    def __init__(self):
        self.scan=CacheDB('web_timeout')
        self.gone_online=CacheDB('go_online')
        self.get=self.scan.get()
        self.online=30
        self.offline=1

    def go_offline(self, manual=False):
        gone_online=self.gone_online.get()
        if gone_online: gone_online=int(gone_online)
        else:gone_online=0
        if not manual:
            if gone_online and gone_online+self.online>=int(round(time.time())):
                Debug('[TimeOut]: too soon to go back offline! %d s' % ((gone_online+self.online)-int(round(time.time()))))
                return
        if self.timeout()==self.online:
            Debug('[TimeOut]: Gone offline! %d s' % ((gone_online+self.online)-int(round(time.time()))))
            showMessage(__language__(30520), __language__(30545) % (self.offline))
            if self.get: self.scan.delete()
            self.scan.add()

    def go_online(self):
        if self.get:
            self.scan.delete()
            Debug('[TimeOut]: Gone online!')
            showMessage(__language__(30521), __language__(30545) % (self.online))
            if self.gone_online.get():
                self.gone_online.delete()
            self.gone_online.add()

    def timeout(self):
        if self.get and int(time.time())-self.get<refresh_period*3600:
            to=self.offline
        else:
            to=self.online
        #Debug('[TimeOut]: '+str(to))
        return to

class DuoCookie():
    def __init__(self):
        self.login=__settings__.getSetting("username")
        self.passwd=__settings__.getSetting("password")
        self.login2=__settings__.getSetting("username2")
        self.passwd2=__settings__.getSetting("password2")
        self.duo_bool=__settings__.getSetting("duo_bool")

    def switch(self):
        if self.login2!='' and self.passwd2!='':
            __settings__.setSetting("username",self.login2)
            __settings__.setSetting("password",self.passwd2)
            __settings__.setSetting("username2",self.login)
            __settings__.setSetting("password2",self.passwd)
            CacheDB('').ClearCache(silent=True)
            __settings__.setSetting("forced_refresh_data","true")

    def cookie(self,i):
        if i==1:
            #Debug('[DuoCookie][cookie]:cookie_auth - '+str(cookie_auth))
            return cookie_auth
        elif i==2:
            return auth_xbmc(self.login2,self.passwd2)

    def ask(self, id):
        if self.duo_bool=='false' or self.login2=='' or self.passwd2=='':
            return cookie_auth
        else:
            duo_last_id=__settings__.getSetting("duo_last_id")
            if id!=duo_last_id or duo_last_id=='':
                titles=[__language__(30540) % self.login,
                        __language__(30541) % self.login2,
                        __language__(30542) % self.login2,
                        __language__(30543),]
                dialog = xbmcgui.Dialog()
                i = dialog.select(__language__(30544), titles)
            else:
                i=int(__settings__.getSetting("duo_last_i"))

            if i>-1:
                __settings__.setSetting("duo_last_id",id)
                __settings__.setSetting("duo_last_i",str(i))

            if i<1:
                return cookie_auth
            elif i==1:
                return auth_xbmc(self.login2,self.passwd2)
            elif i==2:
                self.switch()
                return auth_xbmc(self.login2,self.passwd2)
            elif i==3:
                return "BOTH"

socket.setdefaulttimeout(TimeOut().timeout())
