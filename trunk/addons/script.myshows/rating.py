# -*- coding: utf-8 -*-
"""Module used to launch rating dialogues and send ratings to trakt"""

import xbmc
import xbmcaddon
import xbmcgui
import utilities as utils


__addon__ = xbmcaddon.Addon("script.myshows")

def rate(rating, media):
    import kp, kinopoisk
    cookie=utils.get_string_setting('cookie')
    if cookie=='': cookie=None
    if not cookie:
        login=utils.get_string_setting('login')
        password=utils.get_string_setting('password')
        kpLogin=kp.Login(login,password,cookie)
        cookie=kpLogin.get_cookie()
        utils.set_string_setting('cookie', cookie)
    k=kinopoisk.KinoPoiskRuAgent()
    kpId,title,year=None,None,None
    if 'kinopoiskId' not in media:
        if 'titleAlt' in media: titles=(media['title'], media['titleAlt'])
        else: titles=(media['title'],)
        for i in titles:
            movies=k.search([],{'name':i,'year':media['year']},'English')
            if len(movies)>0:
                if movies[0][4]>90:
                    ret=0
                else:
                    items=[]
                    for i in movies: items.append('%s (%s)'%(i[1],str(i[2])))
                    ret=xbmcgui.Dialog().select('Movies:',items)
                if ret>-1:
                    kpId=movies[ret][0]
                    title=movies[ret][1].encode('utf-8')
                    year=str(movies[ret][2])
                    break
    else:
        kpId=str(media['kinopoiskId'])
        title=media['title'].encode('utf-8')
        year=str(media['year'])
    if kpId and kpId!='None':
        r_class=kp.Rate(str(rating),str(kpId), cookie)
        r=r_class.rateit()
        if r:
            utils.notification('Rated %s OK!' % (str(kpId)),'%s to %s (%s)!' %(str(rating), title, year))
            folderid=utils.get_string_setting('folderid')
            if folderid!="" and folderid>-1 and isinstance(int(folderid),int):
                r_class.moveit(int(folderid))
            return 1




def rateMedia(media_type, summary_info, unrate=False, rating=None, offline=False):
    xbmc.executebuiltin('Dialog.Close(all, true)')

    gui = RatingDialog(
        "RateKP.xml",
        __addon__.getAddonInfo('path'),
        media_type=media_type,
        media=summary_info,
        rating_type='advanced',
        offline=offline
    )

    gui.doModal()
    if gui.rating:
        rating = gui.rating

        if not rating or rating == "unrate":
            return
        elif offline:
            WatchedDB().check(str(gui.media), rating)
        else:
            rate(rating, gui.media)
    else:
        utils.Debug("[Rating] Rating dialog was closed with no rating.")

    del gui

class RatingDialog(xbmcgui.WindowXMLDialog):
    buttons = {
        10030:    'love',
        10031:    'hate',
        11030:    1,
        11031:    2,
        11032:    3,
        11033:    4,
        11034:    5,
        11035:    6,
        11036:    7,
        11037:    8,
        11038:    9,
        11039:    10
    }

    focus_labels = {
        10030: 1314,
        10031: 1315,
        11030: 1315,
        11031: 1316,
        11032: 1317,
        11033: 1318,
        11034: 1319,
        11035: 1320,
        11036: 1321,
        11037: 1322,
        11038: 1323,
        11039: 1314
    }

    def __init__(self, xmlFile, resourcePath, forceFallback=False, media_type=None, media=None, rating_type=None, rerate=False, offline=False):
        self.media_type = media_type
        self.media = media
        self.rating_type = rating_type
        self.rating = None
        self.rerate = rerate
        self.offline=offline

    def onInit(self):
        self.getControl(10014).setVisible(False)
        self.getControl(10015).setVisible(True)

        s = "%s (%s)" % (self.media['title'], self.media['year'])
        self.getControl(10012).setLabel(s)
        if self.offline: self.getControl(10011).setLabel('KinoPoisk.ru Rate Offline!')
        else: self.getControl(10011).setLabel('KinoPoisk.ru Rate')

        rateID = 11037
        self.setFocus(self.getControl(rateID))

    def onClick(self, controlID):
        if controlID in self.buttons:
            self.rating = self.buttons[controlID]
            self.close()

    def onFocus(self, controlID):
        if controlID in self.focus_labels:
            s = utils.getString(self.focus_labels[controlID])
            if self.rerate:
                if self.media['rating'] == self.buttons[controlID] or self.media['rating_advanced'] == self.buttons[controlID]:
                    s = utils.getString(1325)
            
            self.getControl(10013).setLabel(s)
        else:
            self.getControl(10013).setLabel('')

import time, xbmcvfs, os.path, sys, xbmcgui, ast
from utilities import get_bool_setting as getSettingAsBool, notification as showMessage
try:
    from sqlite3 import dbapi2 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite

__settings__ = xbmcaddon.Addon("script.myshows")
__language__ = __settings__.getLocalizedString

class WatchedDB:
    def __init__(self):
        dirname = xbmc.translatePath('special://temp')
        for subdir in ('xbmcup', sys.argv[0].replace('plugin://', '').replace('/', '')):
            dirname = os.path.join(dirname, subdir)
            if not xbmcvfs.exists(dirname):
                xbmcvfs.mkdir(dirname)
        self.dbfilename = os.path.join(dirname, 'myshows.db3')
        if not xbmcvfs.exists(self.dbfilename):
            creat_db(self.dbfilename)
        self.dialog = xbmcgui.Dialog()

    def _get(self, id):
        self._connect()
        self.where=' where id="%s"' % (id)
        self.cur.execute('select rating from watched'+self.where)
        res=self.cur.fetchone()
        self._close()
        return res[0] if res else None

    def _get_all(self):
        self._connect()
        self.cur.execute('select id, rating from watched order by addtime desc')
        res = [[x[0],x[1]] for x in self.cur.fetchall()]
        self._close()
        return res

    def check(self, id, rating=0):
        ok1,ok3=None,None
        db_rating=self._get(id)
        title=titlesync(id)
        if getSettingAsBool("silentoffline"):
            if db_rating==None and rating>=0:
                showMessage(__language__(30520),__language__(30522) % (str(rating)))
                ok1=True
            elif db_rating>=0 and rating!=db_rating:
                showMessage(__language__(30520),__language__(30523) % (str(rating)))
                ok3=True
            elif db_rating!=None and rating==db_rating:
                showMessage(__language__(30520),__language__(30524) % (str(rating)))
        else:
            if db_rating==None and rating>=0:
                ok1=self.dialog.yesno(__language__(30520),__language__(30525) % (str(rating)), unicode(title))
            elif db_rating and rating!=db_rating:
                ok3=self.dialog.yesno(__language__(30520),__language__(30526) % (str(db_rating), str(rating)),unicode(title))
            elif db_rating==0 and rating!=db_rating:
                ok3=True
            elif db_rating!=None and rating==db_rating:
                showMessage(__language__(30520),__language__(30527) % (str(rating)))

        if ok1:
            self._add(id, rating)
            return True
        if ok3:
            self._delete(id)
            self._add(id, rating)
            return True

    def onaccess(self):
        self._connect()
        self.cur.execute('select count(id) from watched')
        x=self.cur.fetchone()
        res=int(x[0])
        self._close()
        i=0

        if res>0:
            ok2=self.dialog.yesno(__language__(30521),__language__(30528) % (str(res)), __language__(30529))
            if ok2:
                for id,rating in self._get_all():
                    j=rate(rating, ast.literal_eval(id))
                    i=i+int(j)
                    self._delete(id)
                    showMessage(__language__(30521),__language__(30530) % (i))
            else:
                ok2=self.dialog.yesno(__language__(30521),__language__(30531) % (str(res)))
                if ok2:
                    for id,rating in self._get_all():
                        self._delete(id)
        return res

    def _add(self, id, rating=0):
        self._connect()
        self.cur.execute('insert into watched(addtime, rating, id) values(?,?,?)', (int(time.time()), int(rating), id))
        self.db.commit()
        self._close()

    def _delete(self, id):
        self._connect()
        self.cur.execute('delete from watched where id=("'+id+'")')
        self.db.commit()
        self._close()

    def _connect(self):
        self.db = sqlite.connect(self.dbfilename)
        self.cur = self.db.cursor()

    def _close(self):
        self.cur.close()
        self.db.close()

def titlesync(id):
    title=id
    try:
        jid=ast.literal_eval(id)
        try:
            if 'title' in jid and 'year' in jid:
                title="%s (%s)" % (jid["title"],jid["year"])
            elif 'title' in jid:
                title=jid["title"]
        except:pass
    except:pass
    return title

def creat_db(dbfilename):
    db = sqlite.connect(dbfilename)
    cur = db.cursor()
    cur.execute('pragma auto_vacuum=1')
    cur.execute('create table watched(addtime integer, rating integer, id varchar(32) PRIMARY KEY)')
    db.commit()
    cur.close()
    db.close()