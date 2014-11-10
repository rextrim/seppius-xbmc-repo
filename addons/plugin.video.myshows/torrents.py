# -*- coding: utf-8 -*-

try:
    from sqlite3 import dbapi2 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite

from functions import *
from net import *
from cxzto import *

try:
    from TSCore import TSengine as tsengine

    torrmode = True
except:
    torrmode = False

try:
    import warnings

    warnings.filterwarnings('ignore', category=RuntimeWarning)
    import libtorrent

    libmode = True
except:
    libmode = False

# Debug('LibTorrent is '+str(libmode)+'; AceStream is '+str(torrmode))

__version__ = "1.9.11"
__plugin__ = "MyShows.ru " + __version__
__author__ = "DiMartino"
__settings__ = xbmcaddon.Addon(id='plugin.video.myshows')
__language__ = __settings__.getLocalizedString
ruName = __settings__.getSetting("ruName")
cookie_auth = __settings__.getSetting("cookie_auth")
socket.setdefaulttimeout(TimeOut().timeout())
__addonpath__ = __settings__.getAddonInfo('path')
icon = __addonpath__ + '/icon.png'
__tmppath__ = os.path.join(xbmc.translatePath('special://temp'), 'xbmcup', 'plugin.video.myshows')
__baseurl__ = "http://api.myshows.me"
striplist = ['the', 'tonight', '  ', 'with', 'jon', 'stewart', '  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ']
subs_ext = ['ass', 'mpsub', 'rum', 'sbt', 'sbv', 'srt', 'ssa', 'sub', 'sup', 'w32']
allowed_ext = ['avi', 'mp4', 'mkv', 'flv', 'mov', 'vob', 'wmv', 'ogm', 'asx', 'mpg', 'mpeg', 'avc', 'vp3', 'fli', 'flc',
               'm4v']
allowed_ext.extend(subs_ext)
debug = __settings__.getSetting("debug")
aceport = 62062

try:
    fpath = os.path.expanduser("~")
    pfile = os.path.join(fpath, 'AppData\Roaming\TorrentStream\engine', 'acestream.port')
    gf = open(pfile, 'r')
    aceport = int(gf.read())
    gf.close()
    print aceport
except:
    aceport = 62062


class TorrentDB:
    def __init__(self):
        dirname = xbmc.translatePath('special://temp')
        for subdir in ('xbmcup', __settings__.getAddonInfo('id').replace('plugin://', '').replace('/', '')):
            dirname = os.path.join(dirname, subdir)
            if not xbmcvfs.exists(dirname):
                xbmcvfs.mkdir(dirname)
        self.dbfilename = os.path.join(dirname, 'data.db3')
        if not xbmcvfs.exists(self.dbfilename):
            creat_db(self.dbfilename)

    def get_all(self, noid=False, showId=None, seasonId=None, noseasonId=False):
        self._connect()
        if not showId:
            self.where = ''
        else:
            self.where = ' where showId=' + str(showId)
            if seasonId:
                self.where += ' and seasonId=' + str(seasonId)
            elif noseasonId == True:
                self.where += ' and seasonId is null'
            if noid: self.where += ' and id is null'
        self.cur.execute(
            'select filename, stype, showId, seasonId, id, episodeId from sources' + self.where + ' order by addtime desc')
        res = [{'filename': x[0], 'stype': x[1], 'showId': x[2], 'seasonId': x[3], 'id': x[4], 'episodeId': x[5]} for x
               in self.cur.fetchall()]
        self._close()
        return res

    def get(self, showId, id=None, seasonId=None, noid=False, noseasonId=False):
        self._connect()
        self.where = ' where showId=' + str(showId)
        if id:
            self.where += ' and id=' + str(id)
        elif noid == True:
            self.where += ' and id is null'
        if seasonId:
            self.where += ' and seasonId=' + str(seasonId)
        elif noseasonId == True:
            self.where += ' and seasonId is null'
        self.cur.execute('select filename, stype, showId, seasonId, id, episodeId from sources' + self.where)
        try:
            x = self.cur.fetchone()
            res = {'filename': x[0], 'stype': x[1], 'showId': x[2], 'seasonId': x[3], 'id': x[4], 'episodeId': x[5]}
        except:
            res = None
        self._close()
        return res

    def getbyfilename(self, filename):
        self._connect()
        if not '"' in list(filename):
            self.where = ' where filename="' + filename + '"'
        else:
            self.where = " where filename='" + filename + "'"
        self.cur.execute('select filename, stype, showId, seasonId, id, episodeId from sources' + self.where)
        x = self.cur.fetchone()
        try:
            res = {'filename': x[0], 'stype': x[1], 'showId': x[2], 'seasonId': x[3], 'id': x[4], 'episodeId': x[5]}
        except:
            res = None
        self._close()
        return res

    def countshowId(self, showId):
        self._connect()
        self.where = ' where showId=' + str(showId) + ''
        self.cur.execute('select count(showId) from sources' + self.where)
        x = self.cur.fetchone()
        res = x[0]
        self._close()
        return res

    def add(self, filename, stype, showId, seasonId=None, id=None, episodeId=None):
        self._connect()
        try:
            self.cur.execute(
                'insert into sources(addtime, filename, stype, showId, seasonId, id, episodeId) values(?,?,?,?,?,?,?)',
                (int(time.time()), filename, stype, showId, seasonId, id, episodeId))
        except:
            self.cur.execute(
                'insert into sources(addtime, filename, stype, showId, seasonId, id, episodeId) values(?,?,?,?,?,?,?)',
                (int(time.time()), unicode(filename.decode('utf-8')), stype, showId, seasonId, id, episodeId))
        self.db.commit()
        self._close()

    def delete(self, filename):
        self._connect()
        if not '"' in list(unicode(filename)):
            self.cur.execute('delete from sources where filename=("' + unicode(filename) + '")')
        else:
            self.cur.execute("delete from sources where filename=('" + unicode(filename) + "')")
        self.db.commit()
        self._close()

    def deleteseason(self, showId, seasonId, noid=False):
        self._connect()
        self.where = ' where showId=' + str(showId) + ' and seasonId=' + str(seasonId)
        if noid == True:
            self.where += ' and id is null'
        else:
            self.where += ' and id not null'
        self.cur.execute('select count(filename) from sources' + self.where)
        self.i = self.cur.fetchone()
        if self.i[0] > 0:
            self.cur.execute('delete from sources' + self.where)
            self.db.commit()
        self._close()
        return self.i[0]

    def deleteshow(self, showId, noseasonId=False):
        self._connect()
        self.where = ' where showId=' + str(showId)
        if noseasonId == True: self.where += ' and seasonId is null'
        self.cur.execute('select count(filename) from sources' + self.where)
        self.i = self.cur.fetchone()
        if self.i[0] > 0:
            self.cur.execute('delete from sources' + self.where)
            self.db.commit()
        self._close()
        return self.i[0]

    def _connect(self):
        self.db = sqlite.connect(self.dbfilename)
        self.cur = self.db.cursor()

    def _close(self):
        self.cur.close()
        self.db.close()


class ScanDB(TorrentDB):
    def add(self, filename):
        self._connect()
        self.cur.execute('insert into scan(addtime, filename) values(?,?)', (int(time.time()), unicode(filename)))
        self.db.commit()
        self._close()

    def isfilename(self, filename):
        self._connect()
        if not '"' in list(unicode(filename)):
            self.where = ' where filename="' + unicode(filename) + '"'
        else:
            self.where = " where filename='" + unicode(filename) + "'"
        try:
            self.cur.execute('select count(filename) from scan' + self.where)
        except:
            self.cur.execute('create table scan(addtime integer, filename varchar(32) PRIMARY KEY)')
            self.db.commit()
            self.cur.execute('select count(filename) from scan' + self.where)
        x = self.cur.fetchone()
        res = x[0]
        self._close()
        if res > 0:
            res = True
        else:
            res = False
        return res

    def get_all(self):
        self._connect()
        stypelist = ['multifile', 'multitorrent', 'rutracker', 'nnm', 'kz', 'cxzto']
        self.where = ' where (stype="unrealstuff"'
        for stype in stypelist:
            self.where += ' OR stype="' + str(stype) + '"'
        self.cur.execute(
            'select filename, stype, showId, seasonId, id, episodeId from sources' + self.where + ') and id is Null order by addtime desc')
        res = [{'filename': x[0], 'stype': x[1], 'showId': x[2], 'seasonId': x[3], 'id': x[4], 'episodeId': x[5]} for x
               in self.cur.fetchall()]
        self._close()
        return res

    def delete(self, filename):
        self._connect()
        if not '"' in list(unicode(filename)):
            self.cur.execute('delete from scan where filename=("' + unicode(filename) + '")')
        else:
            self.cur.execute("delete from scan where filename=('" + unicode(filename) + "')")
        self.db.commit()
        self._close()


class Source:
    def __init__(self, stringdata=None):
        if not stringdata:
            params = get_params()
            stringdata = params['stringdata']
        self.stringdata = stringdata
        self.apps = get_apps(stringdata)

        self.filename = None
        self.showId = None
        self.seasonId = None
        self.mode = None
        self.id = None
        self.episodeId = None
        self.ind = None
        self.action = None
        self.title = None
        self.stype = None
        self.myback_url = None

        try:
            self.showId = self.apps['showId']
        except:
            pass
        try:
            self.seasonId = self.apps['seasonId']
        except:
            pass
        try:
            self.mode = int(self.apps['mode'])
        except:
            pass
        try:
            self.id = self.apps['id']
        except:
            pass
        try:
            self.episodeId = self.apps['episodeId']
        except:
            pass
        try:
            self.ind = self.apps['ind']
        except:
            pass
        try:
            self.action = self.apps['action']
        except:
            pass
        try:
            self.title = str(self.apps['title'])
        except:
            pass
        try:
            self.filename = self.getfilename()
        except:
            pass
        try:
            self.stype = self.gettype()
        except:
            pass
        try:
            self.myback_url = params['myback_url']
        except:
            pass

        try:
            Debug('[MY SOURCE STYPE]: ' + str(self.stype))
            Debug('FILENAME HERE FROM GETDICT ' + self.filename.decode('utf-8'))
        except:
            pass
        self.handle()

    def getfilename(self):
        try:
            self.filename = self.apps['filename']
            return urllib.unquote_plus(self.apps['filename']).decode('utf-8')
        except:
            getdict = TorrentDB().get(self.showId, self.id, self.seasonId, invert_bool(self.id))
            try:
                Debug('FILENAME IN GETFILEANEM FROM GETDICT ' + getdict['filename'].decode('utf-8'))
            except:
                pass
            try:
                return getdict['filename'].decode('utf-8')
            except:
                try:
                    return getdict['filename']
                except:
                    return None

    def gettype(self):
        stype = None
        try:
            stype = self.apps['stype']
            return stype
        except:
            if self.filename:
                try:
                    dumps = TorrentDB().getbyfilename(self.filename)
                    jdumps = json.loads(dumps)
                    stype = jdumps['stype']
                    return stype
                except:
                    self.stypes = [r'json', r'cxzto', r'vk-file', r'lostfilm', r'url-file', r'btchat', r'rutracker',
                                   r'tpb', r'nnm', r'kz', 'smb', 'torrenter']
                    self.fnames = ['{.*?}', 'http://cxz.to.*?', 'http://.*?vk\.(com|me).*?', 'http://tracktor\.in.*?',
                                   'http://.*?\.avi|mp4|mkv|flv|mov|vob|wmv|ogm|asx|mpg|mpeg|avc|vp3|fli|flc|m4v$',
                                   'BTchatCom::.+', 'RuTrackerOrg::.+', 'ThePirateBaySe::.+', 'NNMClubRu::.+',
                                   'Kino_ZalTv::.+', '^smb://.+?', '\w+::.+']
                    self.i = -1
                    for fn in self.fnames:
                        self.i += 1
                        self.match = re.compile(str(fn), re.I | re.DOTALL).match(self.filename)
                        if self.match:
                            stype = self.stypes[self.i]
                            break
                    if stype == 'json':
                        if json.loads(self.filename)['stype'] not in (
                        'btchat', 'torrent', 'rutracker', 'tpb', 'nnm', 'kz', 'torrenter', 'lostfilm'):
                            stype = json.loads(self.filename)['stype']
                    elif stype not in ['vk-file', 'cxzto', 'url-file', 'btchat', 'rutracker', 'tpb', 'nnm', 'kz',
                                       'torrenter', 'lostfilm']:
                        if len(xbmcvfs.listdir(self.filename)[1]) > 0:
                            stype = 'dir'
                        elif self.filename.rfind('.torrent', len(self.filename) - 8) == -1:
                            stype = 'file'
                        else:
                            stype = 'torrent'
                    return stype
            else:
                if xbmcEpisode(self.showId, self.seasonId, self.episodeId):
                    stype = 'xbmc'
                return stype

    def addsource(self):
        try:
            if self.stype == 'torrenterall':
                externals = TorrenterSearch(self.stype, self.showId, self.seasonId, stop='STOP').externals
                for i in externals.iterkeys():
                    if externals[i] == self.filename.split('::')[0]:
                        self.stype = i
                        break
            if self.stype == 'torrenterall': self.stype = 'torrenter'
            TorrentDB().add(self.filename, self.stype, self.showId, self.seasonId, self.id, self.episodeId)
            showMessage(__language__(30208), __language__(30230) % self.filename)
        except:
            showMessage(__language__(30206), __language__(30237) % self.filename, forced=True)

    def handle(self):
        pass

    def addjson(self):
        out = self.out()
        if out == 'Ok':
            myshows_items = []
            myshows_files = []
            for k, v in self.filelist:
                stringdata = ('{"filename":"%s", "stype":"%s", "title":"%s", "ind":%s}' % (
                urllib.quote_plus(self.filename), self.stype, urllib.quote_plus(k), v))
                myshows_files.append(str(k) + '|:|' + str(stringdata))
            if len(myshows_files) == 1:
                ret = 0
                myshows_files[0] = unicode(myshows_files[0]).split('|:|')[1]
            else:
                myshows_files.sort()
                for x in myshows_files: myshows_items.append(urllib.unquote_plus(x).split('|:|')[0])
                for x in myshows_files: myshows_files[myshows_files.index(unicode(x))] = unicode(x).split('|:|')[1]
                myshows_items.append(unicode(__language__(30205)))
                myshows_files.append(unicode(__language__(30205)))

                dialog = xbmcgui.Dialog()
                ret = dialog.select(__language__(30223), myshows_items)
                if ret == myshows_items.index(unicode(__language__(30205))): return None
            runstring = {"filename": myshows_files[ret], "stype": "json", "showId": self.showId,
                         "episodeId": self.episodeId, "id": self.id, "seasonId": self.seasonId}
            sys_url = __settings__.getAddonInfo('id') + '?mode=3010&stringdata=' + makeapp(runstring)
            xbmc.executebuiltin('xbmc.RunPlugin("' + sys_url + '")')
        if not self.libmode: self.TSplayer.end()

    def out(self):
        self.libmode = libmode
        if int(__settings__.getSetting("torplayer")) == 0 and torrmode:
            self.libmode = False
        if self.stype in ('url-torrent',):
            self.TSplayer = tsengine()
            try:
                out = self.TSplayer.load_torrent(self.filename, 'TORRENT', port=aceport)
            except:
                out = self.TSplayer.load_torrent(urllib.unquote_plus(self.filename), 'TORRENT', port=aceport)
            self.filelist = self.TSplayer.files.iteritems()
        else:
            self.stype = 'torrent'
            if not self.libmode:
                try:
                    f = open(self.filename, 'rb')
                except:
                    try:
                        f = open(urllib.unquote_plus(self.filename), 'rb')
                    except:
                        showMessage('Fail!', 'No such file or directory!')
                        return
                buf = f.read()
                f.close
                self.torr_link = base64.b64encode(buf)
                self.TSplayer = tsengine()
                out = self.TSplayer.load_torrent(self.torr_link, 'RAW')
                self.filelist = self.TSplayer.files.iteritems()
            else:
                self.filelist = []
                if os.path.exists(self.filename):
                    torrentFileInfo = libtorrent.torrent_info(self.filename)
                    s = torrentFileInfo.files()
                    for f in s:
                        self.filelist.append((f.path[f.path.find('\\') + 1:], s.index(f)))
                out = 'Ok'
        return out

    def addmultijson(self):
        i = 0
        ind = -1
        out = self.out()
        myshows_items = []
        myshows_files = []
        myshows_items_indexes = {}
        if out == 'Ok':
            for k, v in self.filelist:
                ind += 1
                stringdata = ('{"filename":"%s", "stype":"%s", "title":"%s", "ind":%s}' % (
                urllib.quote_plus(self.filename), self.stype, urllib.quote_plus(k), v))
                myshows_files.append((str(k), str(stringdata), ind))

            if len(myshows_files) == 1:
                myshows_files[0] = unicode(myshows_files[0][1])
            elif len(myshows_files) > 1:
                for x in myshows_files: myshows_items.append(urllib.unquote_plus(x[0]))
                for x in myshows_files: myshows_items_indexes[urllib.unquote_plus(x[0])] = x[2]
                for x in myshows_files: myshows_files[myshows_files.index(x)] = unicode(x[1])
                myshows_temp = getDirList(None, myshows_items)

                if len(chooseDir(myshows_temp)) > 1:
                    dialog = xbmcgui.Dialog()
                    ret = dialog.select(__language__(30238), chooseDir(myshows_temp))
                else:
                    ret = 0
                if ret != None:
                    myshows_temp = chooseDir(myshows_temp, unicode(chooseDir(myshows_temp)[ret]))
                    data = Data(cookie_auth, __baseurl__ + '/shows/' + str(self.showId))
                    jdata = json.loads(data.get())

                    if len(myshows_temp) > 1:
                        cutlist = cutFileNames(myshows_temp)
                    else:
                        cutlist = myshows_temp
                    for fn in cutlist:
                        doit = False
                        x = FileNamesPrepare(fn)
                        self.episodeId = x[1]
                        if not self.seasonId and not x[0]:
                            break
                        else:
                            for id in jdata['episodes']:
                                if jdata['episodes'][id]['seasonNumber'] == x[0] and jdata['episodes'][id][
                                    'episodeNumber'] == x[1] \
                                        or not x[0] and jdata['episodes'][id]['seasonNumber'] == self.seasonId and \
                                                        jdata['episodes'][id]['episodeNumber'] == x[1]:
                                    self.id = int(id)
                                    doit = True
                                    break
                            self.filename = myshows_files[myshows_items_indexes[myshows_temp[cutlist.index(fn)]]]
                            if not TorrentDB().getbyfilename(self.filename) and doit:
                                try:
                                    if x[0]:
                                        seasonId = x[0]
                                    else:
                                        seasonId = self.seasonId
                                    TorrentDB().add(self.filename, 'json', self.showId, seasonId, self.id, x[1])
                                    i += 1
                                    filename = str(myshows_files[cutlist.index(fn)])
                                except:
                                    pass
                            else:
                                pass
                    if i > 1:
                        showMessage(__language__(30208), __language__(30249) % (str(i)))
                    elif i == 1:
                        try:
                            showMessage(__language__(30208), __language__(30230) % (urllib.unquote_plus(filename)))
                        except:
                            showMessage(__language__(30208), __language__(30249) % (str(i)))
        if not self.libmode:
            self.TSplayer.end()
            xbmc.sleep(10000)
        return i

    def addmultifile(self):
        i = 0
        filename = self.filename
        data = Data(cookie_auth, __baseurl__ + '/shows/' + str(self.showId))
        jdata = json.loads(data.get())
        dirlist = getDirList(filename)
        if len(dirlist) > 1:
            cutlist = cutFileNames(dirlist)
        else:
            cutlist = dirlist
        for fn in cutlist:
            x = FileNamesPrepare(fn)
            if x:
                doit = False
                Debug('[addmultifile]: filename - ' + filename)
                self.filename = os.path.join(filename.encode('utf-8', 'ignore'), dirlist[cutlist.index(fn)])
                self.episodeId = x[1]
                if not self.seasonId and not x[0]:
                    break
                else:
                    for id in jdata['episodes']:
                        if jdata['episodes'][id]['seasonNumber'] == x[0] and jdata['episodes'][id]['episodeNumber'] == \
                                x[1] \
                                or not x[0] and jdata['episodes'][id]['seasonNumber'] == self.seasonId and \
                                                jdata['episodes'][id]['episodeNumber'] == x[1]:
                            self.id = int(id)
                            doit = True
                            break
                    if not TorrentDB().getbyfilename(self.filename) and doit:
                        try:
                            if x[0]:
                                seasonId = x[0]
                            else:
                                seasonId = self.seasonId
                            TorrentDB().add(self.filename, 'file', self.showId, seasonId, self.id, self.episodeId)
                            i += 1
                        except:
                            pass
        try:
            TorrentDB().add(filename, 'multifile', self.showId, self.seasonId)
        except:
            pass
        if i > 1:
            showMessage(__language__(30208), __language__(30249) % (str(i)))
        elif i == 1:
            showMessage(__language__(30208), __language__(30230) % (urllib.unquote_plus(self.filename)))
        return i

    def play_torrent(self):
        skip = False
        if self.stype == 'json':
            skip = True
            apps = json.loads(self.filename)
            self.filename = apps['filename']
            self.stype = apps['stype']
        out = self.out()
        if out == 'Ok' and not skip:
            myshows_items = []
            myshows_files = []
            for k, v in self.filelist:
                stringdata = ('{"filename":"%s", "title":"%s", "ind":%s}' % (
                urllib.quote_plus(self.filename), urllib.quote_plus(k), v))
                myshows_files.append(str(k) + '|:|' + str(stringdata))
            myshows_files.sort()
            for x in myshows_files: myshows_items.append(urllib.unquote_plus(x).split('|:|')[0])
            for x in myshows_files: myshows_files[myshows_files.index(unicode(x))] = unicode(x).split('|:|')[1]
            Debug(str(myshows_files))
            myshows_items.append(unicode(__language__(30205)))
            myshows_files.append(unicode(__language__(30205)))

            dialog = xbmcgui.Dialog()
            if len(myshows_items) > 1: myshows_items = cutFileNames(myshows_items)
            ret = dialog.select(__language__(30223), myshows_items)
            if ret != -1 and ret != myshows_items.index(unicode(__language__(30205))):
                apps = json.loads(myshows_files[ret])
                self.play_it(apps)

        if out == 'Ok' and skip:
            self.play_it(apps)
        if not self.libmode: self.TSplayer.end()

    def play_it(self, apps):
        self.libmode = libmode
        if int(__settings__.getSetting("torplayer")) == 0 and torrmode:
            self.libmode = False
        self.filename = urllib.unquote_plus(apps['filename'])
        self.title = urllib.unquote_plus(apps['title'])
        self.ind = apps['ind']
        if not self.libmode:
            self.TSplayer.play_url_ind(int(self.ind), self.title, str(icon), '')
        else:
            torrenter_setting = xbmcaddon.Addon(id='plugin.video.torrenter')
            torrenter_setting.setSetting("lastTorrent", self.filename)
            epinfo = ''
            if self.showId and self.id:
                if not self.seasonId or not self.episodeId and self.episodeId != 0:
                    Debug('[play_it]: not self.seasonId or not self.episodeId')
                    self.seasonId, self.episodeId = id2SE(self.showId, self.id)
                if self.seasonId:
                    title, label = id2title(self.showId, self.id, norus=True)
                    if title and label:
                        epinfo = '&seasonId=%s&episodeId=%s&title=%s&label=%s' % (
                        str(self.seasonId), str(self.episodeId), urllib.quote_plus(title), urllib.quote_plus(label))
            xbmc.executebuiltin(
                'xbmc.RunPlugin("plugin://plugin.video.torrenter/?action=playTorrent&external=1&url=%s%s")' % (
                str(self.ind), epinfo))


class DownloadSource(Source):
    def handle(self):
        if self.stype in ['json', 'btchat', 'torrent', 'multitorrent', 'rutracker', 'tpb', 'nnm', 'kz', 'torrenter',
                          'lostfilm']:
            self.download()
        elif self.stype:
            #xbmcgui.Dialog().ok('LOL', 'Not good stype')
            pass
        elif not self.stype and self.id:
            TorrenterSearch('tpb', self.showId, self.seasonId, self.id, self.episodeId, stop=None, silent='true')
        elif not self.stype and not self.id:
            TorrenterSearch('nnm', self.showId, self.seasonId, None, None, stop=None, silent='true')
        else:
            if xbmc.getCondVisibility("system.platform.windows"):
                downloadCmd = "start"
            else:
                downloadCmd = "open"
            os.system(downloadCmd + " " + self.filename)

    def download(self):
        success = None
        self.ind, self.title = None, None
        nomagnet = False
        Debug('[DownloadSource][download]: stype is ' + str(self.stype))
        if self.stype in ['json', 'btchat', 'torrent', 'multitorrent', 'rutracker', 'tpb', 'nnm', 'kz', 'torrenter',
                          'lostfilm']:
            items, clean = Download().listdirs()
            if __settings__.getSetting("torrent_save") == '0':
                if __settings__.getSetting("torrent") == '0':
                    if len(items) > 1:
                        dialog = xbmcgui.Dialog()
                        dirid = dialog.select(__language__(30248), items)
                    else:
                        dirid = 0
                    if dirid == -1: return
                    dirname = clean[dirid]
                elif __settings__.getSetting("torrent") == '1':
                    dirname = clean[0]
            else:
                dirname = __settings__.getSetting("torrent_dir")

            if self.stype == 'json':
                j = json.loads(self.filename)
                self.stype, self.ind, self.filename, self.title = j['stype'], j['ind'], j[
                    'filename'], urllib.unquote_plus(j['title'])
                nomagnet = True
            elif self.stype in ('rutracker', 'nnm', 'kz') or self.stype == 'torrenter' and self.filename.split('::')[1][
                                                                                           0:6] != 'magnet':
                xbmc.executebuiltin(
                    'XBMC.RunPlugin(plugin://plugin.video.torrenter/?action=openTorrent&silent=true&external=%s&url=%s&sdata=%s)'
                    % (
                    self.filename.split('::')[0], urllib.quote_plus(self.filename), urllib.quote_plus(self.stringdata)))
                xbmc.sleep(3000)
                nomagnet = True
                self.filename = xbmcaddon.Addon(id='plugin.video.torrenter').getSetting('lastTorrent')

            if self.stype in ['torrent', 'multitorrent', 'rutracker', 'nnm', 'kz', 'torrenter'] and nomagnet:
                try:
                    f = open(self.filename, 'rb')
                except:
                    f = open(urllib.unquote_plus(self.filename), 'rb')
                torrent = f.read()
                f.close
                success = Download().add(torrent, dirname)
            elif self.stype in ['tpb', 'btchat', 'torrenter', 'lostfilm'] and not nomagnet:
                if self.stype != 'lostfilm': self.filename = self.filename.split('::')[1]
                success = Download().add_url(self.filename, dirname)
                showMessage(__language__(30211), __language__(30212))
                xbmc.sleep(1500)
                if self.stype in ['tpb', 'torrenter']:
                    xbmc.sleep(15000)
                    #xbmcgui.Dialog().ok(unicode(__language__(30269)), unicode(__language__(30270)))

            if success:
                self.filename = self.getfilename()
                id = chooseHASH(self.showId, self.id, self.seasonId, self.episodeId)
                if id:
                    if self.id:
                        DeleteSource()
                        if self.title:
                            try:
                                for listfiles in Download().listfiles(id[0]):
                                    if isSubtitle(self.title, listfiles[0]):
                                        Download().setprio_simple(id[0], '3', listfiles[2])
                            except:
                                pass
                    Download().setprio(id[0], self.ind)
                    stringdata = json.loads(urllib.unquote_plus(self.stringdata))
                    stringdata['stype'] = 'BLANK'
                    add = AddSource(json.dumps(stringdata))
                    add.uTorrentAdd(id, self.ind)
                    xbmc.sleep(10)
                    if self.title:
                        TorrentDB().add(self.filename, 'json', self.showId, self.seasonId, self.id, self.episodeId)
            else:
                showMessage(__language__(30206), __language__(30271), forced=True)


def chooseHASH(showId=None, id=None, seasonId=None, episodeId=None, auto_only=False):
    socket.setdefaulttimeout(3)
    dialog_items, dialog_items_clean = [], []
    dialog_files = []
    hash, title = None, None
    dat = Download().list()
    if not dat:
        socket.setdefaulttimeout(TimeOut().timeout())
        return
    for data in dat:
        #Debug('[chooseHASH]: '+str((data['id'], data['dir'].encode('utf-8'))))
        dialog_files.append((data['id'], data['dir'].encode('utf-8')))
        dialog_items.append('[' + str(data['progress']) + '%] ' + data['name'])
        dialog_items_clean.append(data['name'])
    if showId: title = id2title(showId, None, True)[0]
    if title and dialog_items_clean:
        items, files, match, count = [], [], 0, 0
        for d_fileindex in range(0, len(dialog_items_clean)):
            d_item = dialog_items_clean[d_fileindex]
            f2m = filename2match(d_item)
            if f2m and (re.search(title, f2m['showtitle']) or re.search(
                    PrepareFilename(title).replace('The Daily Show With Jon Stewart', 'The Daily Show'),
                    f2m['showtitle'])):
                items.append(dialog_items[d_fileindex])
                files.append(dialog_files[d_fileindex])
                if 'date' in f2m and id2date(showId, id) == f2m['date'] or \
                                                        'season' in f2m and 'episode' in f2m and int(
                                        f2m['season']) == seasonId and int(f2m['episode']) == episodeId:
                    count += 1
                    match = d_fileindex
        if count == 1:
            return dialog_files[match]
        if auto_only: return
        if len(items) > 1:
            items.append(unicode(__language__(30205)))
            ret = xbmcgui.Dialog().select(unicode(__language__(30272)), items)
            if ret > -1 and ret < len(files):
                hash = files[ret]
                return hash
        elif len(items) == 1:
            hash = files[0]
            return hash
    ret = xbmcgui.Dialog().select(unicode(__language__(30272)), dialog_items)
    if ret > -1 and ret < len(dialog_files): hash = dialog_files[ret]
    return hash


def askDeleteFile(showId, id):
    seasonId, episodeId = id2SE(showId, id)
    id = chooseHASH(showId, id, int(seasonId), int(episodeId), True)
    action = 'removedata'
    if id:
        id = id[0]
        name = None
        dat = Download().list()
        for data in dat:
            if data['id'] == id:
                name = data['name']
                break
        if name:
            dialog = xbmcgui.Dialog()
            ok = dialog.yesno(__language__(30512), __language__(30513) % (action), name)
            if ok:
                Download().action_simple(action, id)


class Serialu(Source):
    def handle(self):
        self.data = Data(cookie_auth, __baseurl__ + '/shows/' + str(self.showId))
        self.jdata = json.loads(self.data.get())
        self.name = self.jdata['ruTitle']
        if not self.name: self.name = self.jdata['title']
        self.stringdata = urllib.quote_plus(
            '{"stype":"serialu", "showId":' + jstr(self.showId) + ', "episodeId":' + jstr(
                self.episodeId) + ', "id":' + jstr(self.id) + ', "seasonId":' + jstr(self.seasonId) + '}')


    def get(self):
        if self.myback_url:
            user_keyboard = xbmc.Keyboard()
            user_keyboard.setHeading(__language__(30256))
            user_keyboard.setHiddenInput(False)
            user_keyboard.setDefault(self.name)
            user_keyboard.doModal()
            if (user_keyboard.isConfirmed()):
                self.name = user_keyboard.getText().decode('utf-8')
                xbmc.executebuiltin(
                    'xbmc.RunPlugin("plugin://plugin.video.serialu.net/?mode=LIST&name=' + urllib.quote_plus(
                        self.name.encode('utf-8')) + '&stringdata=' + self.stringdata + '")')
        else:
            xbmc.executebuiltin(
                'xbmc.RunPlugin("plugin://plugin.video.serialu.net/?mode=LIST&name=' + urllib.quote_plus(
                    self.name.encode('utf-8')) + '&stringdata=' + self.stringdata + '")')

    def read(self):
        getfilename = os.path.join(__tmppath__, 'serialu_' + str(self.showId) + '.txt')
        self.fg = xbmcvfs.File(getfilename, 'r')
        self.getlist = self.fg.read()
        self.fg.close()
        return re.compile('{(.+?)}').findall(self.getlist)

    def add(self):
        i = 0
        getdat = self.read()
        for getdata in getdat:
            getjdata = json.loads('{' + getdata + '}')
            if self.seasonId and self.seasonId != getjdata['seasonId']: continue
            self.filename = getjdata['filename']
            self.stype = 'serialu-file'
            self.episodeId = getjdata['episodeId']
            for id in self.jdata['episodes']:
                #if not self.seasonId: self.seasonId=getjdata['seasonId']
                if self.jdata['episodes'][id]['seasonNumber'] == getjdata['seasonId'] and self.jdata['episodes'][id][
                    'episodeNumber'] == getjdata['episodeId']:
                    self.id = int(id)
                    break
            if not self.getfilename():
                try:
                    TorrentDB().add(urllib.unquote_plus(self.filename), self.stype, self.showId, getjdata['seasonId'],
                                    self.id, self.episodeId)
                    i += 1
                except:
                    pass
        if i > 1:
            try:
                TorrentDB().add(urllib.unquote_plus(self.stringdata), 'serialu', self.showId, self.seasonId)
            except:
                pass
            showMessage(__language__(30208), __language__(30249) % (str(i)))
        elif i == 1:
            showMessage(__language__(30208), __language__(30230) % (urllib.unquote_plus(self.filename)))
        return i


class AddSource(Source):
    def handle(self):
        if self.stype == 'xbmc': self.stype = None
        if not self.stype:
            myshows_titles, myshows_items = self.menu()
            if getSettingAsBool('flexmenu') and len(myshows_items) == 2:
                i = 0
            else:
                dialog = xbmcgui.Dialog()
                i = dialog.select(__language__(30235), myshows_titles)
            if i > -1: stype = myshows_items[i]
            if i == -1: return
        else:
            stype = self.stype

        if stype == 'file' or stype == 'torrent':
            action = xbmcgui.Dialog()
            filename = action.browse(1, __language__(30229), 'video')
            if len(filename) > 1:
                if filename.rfind('.torrent', len(filename) - 8) == -1 and self.id == None: filename = os.path.dirname(
                    filename)
                self.filename = filename
                self.stype = self.gettype()
                try:
                    self.addsource()
                    showMessage(__language__(30208), __language__(30230) % (filename))
                    AskPlay()
                except:
                    try:
                        showMessage(__language__(30206), __language__(30231) % (filename), forced=True)
                    except:
                        showMessage(__language__(30206), __language__(30231) % (''), forced=True)
        elif stype == 'multitorrent':
            action = xbmcgui.Dialog()
            filename = action.browse(1, __language__(30247), 'video', '.torrent')
            if filename and filename != '':
                self.filename = filename
                self.addmultijson()
                try:
                    TorrentDB().add(self.filename, 'multitorrent', self.showId, self.seasonId)
                except:
                    pass
        elif stype == 'vk-file':
            VKSearch(self.showId, self.id)
        elif stype == 'lostfilm':
            LFSearch(self.showId, self.id)
        elif stype == 'cxzto':
            CXZTOSearch(self.showId, self.seasonId, self.id)
        elif stype in ['btchat', 'tpb', 'rutracker', 'nnm', 'kz', 'torrenterall']:
            TorrenterSearch(stype, self.showId, self.seasonId, self.id, self.episodeId)
        elif stype == 'serialu':
            Serialu().get()
        elif stype == 'dir' or stype == 'multifile':
            self.addstype = stype
            self.DirAdd()
        elif stype == 'utorrent':
            self.uTorrentAdd()

    def menu(self):
        if getSettingAsBool('flexmenu'):
            Debug('[AddSource][menu]: Using flexmenu')
            myshows_titles, myshows_items = [], []

            menu = [  # name: 'setting_name',lang,mode (0 - all, 1 - ep only, 2 - season/show only
                      ['cxzto', 30550, 0, 'cxzto'],
                      ['torrenterall', 30291, 0, 'torrenterall'],
                      ['multifile', 30245, 2, 'multifile'],
                      ['dir', 30244, 2, 'dir'],
                      ['rutracker', 30268, 2, 'rutracker'],
                      ['nnm', 30288, 2, 'nnm'],
                      ['multitorrent', 30246, 2, 'multitorrent'],
                      ['file', 30239, 1, 'file'],
                      ['vk-file', 30240, 1, 'vk-file'],
                      ['lostfilm', 30241, 1, 'lostfilm'],
                      ['tpb', 30273, 1, 'tpb'],
                      ['torrent_menu', 30242, 0, 'torrent'],
                      ['utorrent', 30274, 0, 'utorrent'],
            ]

            for item in menu:
                if self.id and item[2] in (0, 1) or not self.id and item[2] in (0, 2):
                    if getSettingAsBool(item[0]):
                        if item[0] == 'lostfilm':
                            socket.setdefaulttimeout(1)
                            try:
                                if 'lostfilm' in get_url(cookie_auth,
                                                         'http://myshows.ru/int/controls/view/episode/' + str(
                                                                 self.id) + '/'):
                                    item[1] = 30514
                            except:
                                pass
                            socket.setdefaulttimeout(TimeOut().timeout())

                        if isinstance(item[1], int):
                            myshows_titles.append(__language__(item[1]))
                        else:
                            myshows_titles.append(item[1])
                        myshows_items.append(item[3])
            myshows_titles.append(__language__(30243))
            myshows_items.append(None)
        else:
            if self.id:
                myshows_titles = [__language__(30291), __language__(30239), __language__(30240), __language__(30241),
                                  __language__(30242), __language__(30273), __language__(30274), __language__(30550),
                                  __language__(30243)]
                myshows_items = ['torrenterall', 'file', 'vk-file', 'lostfilm', 'torrent', 'tpb', 'utorrent', 'cxzto',
                                 None]
                socket.setdefaulttimeout(1)
                try:
                    if 'lostfilm' in get_url(cookie_auth,
                                             'http://myshows.ru/int/controls/view/episode/' + str(self.id) + '/'):
                        myshows_titles[3] = __language__(30514)
                except:
                    pass
                socket.setdefaulttimeout(TimeOut().timeout())
            else:
                myshows_titles = [__language__(30291), __language__(30244), __language__(30268), __language__(30288),
                                  __language__(30242), __language__(30245), __language__(30246), __language__(30274),
                                  __language__(30243)]
                myshows_items = ['torrenterall', 'dir', 'rutracker', 'nnm', 'torrent', 'multifile', 'multitorrent',
                                 'utorrent', None]

        return myshows_titles, myshows_items

    def uTorrentAdd(self, id=None, ind=None, play=False):
        if not id:
            id, self.filename = chooseHASH(self.showId, self.id, self.seasonId, self.episodeId)
        else:
            id, self.filename = id
        ret = None

        if len(self.filename) > 1:
            if self.id:
                self.stype = 'file'
            else:
                self.stype = 'multifile'

            if self.stype == 'multifile':
                if isRemoteTorr():
                    dialog = xbmcgui.Dialog()
                    torrent_replacement = __settings__.getSetting("torrent_replacement")
                    ok = False
                    if torrent_replacement not in ['', None] and getSettingAsBool("torrent_replacement_ask"):
                        ok = dialog.yesno(__language__(30292), __language__(30293), torrent_replacement)
                    if torrent_replacement in ['', None] or ok:
                        torrent_replacement = dialog.browse(0, __language__(30294), 'video')
                        __settings__.setSetting("torrent_replacement", torrent_replacement)
                    if torrent_replacement and torrent_replacement != '':
                        self.filename = os.path.join(torrent_replacement, os.path.basename(self.filename))
                    else:
                        return
                try:
                    self.filename = self.filename.decode('utf-8', 'ignore')
                except:
                    pass
                i = self.addmultifile()
                showMessage(__language__(30208), __language__(30249) % (str(i)))
            elif self.stype == 'file':
                dllist = sorted(Download().listfiles(id), key=lambda x: x[0])
                #dirlist=[x[0] for x in dllist]
                dirlist, videolist, cutlist = [], [], []
                for x in dllist:
                    dirlist.append(x[0].encode('utf-8', 'ignore'))
                    match = re.match('.avi|.mp4|.mkV|.flv|.mov|.vob|.wmv|.ogm|.asx|.mpg|mpeg|.avc|.vp3|.fli|.flc|.m4v',
                                     x[0][int(len(x[0])) - 4:len(x[0])], re.I)
                    if match:
                        videolist.append(x[0].encode('utf-8', 'ignore'))
                #print str(videolist)
                if len(videolist) == 2 and self.id:
                    samplelist = []
                    for z in (0, 1):
                        match = re.match('sample', videolist[z], re.I)
                        if not match:
                            samplelist.append(videolist[z])
                    if len(samplelist) == 1: videolist = samplelist
                if len(videolist) == 1:
                    cutlist.extend(dirlist)
                    ret = dirlist.index(videolist[0].encode('utf-8', 'ignore'))
                else:
                    if len(dirlist) > 1:
                        cutlist = cutFileNames(dirlist)
                        for s in dirlist:
                            i = dirlist.index(s)
                            cutlist[i] = '[' + str(dllist[i][1]) + '%][' + dllist[i][3] + '] ' + cutlist[i]
                        cutlist.append(unicode(__language__(30205)))
                        if not ind and ind != 0:
                            if len(dirlist) > 1:
                                dialog = xbmcgui.Dialog()
                                ret = dialog.select(__language__(30233), cutlist)
                                if ret == cutlist.index(unicode(__language__(30205))):
                                    return
                            else:
                                ret = 0
                        else:
                            for s in dllist:
                                if s[2] == ind: ret = dirlist.index(s[0].encode('utf-8', 'ignore'))
                    else:
                        showMessage(unicode(__language__(30269)), unicode(__language__(30296)))
                if ret > -1:
                    if not isRemoteTorr():
                        self.filename = os.path.join(self.filename, dirlist[ret])
                    else:
                        dialog = xbmcgui.Dialog()
                        torrent_replacement = __settings__.getSetting("torrent_replacement")
                        ok = False
                        if torrent_replacement not in ['', None] and getSettingAsBool("torrent_replacement_ask"):
                            ok = dialog.yesno(__language__(30292), __language__(30293), torrent_replacement)
                        if torrent_replacement in ['', None] or ok:
                            torrent_replacement = dialog.browse(0, __language__(30294), 'video')
                            __settings__.setSetting("torrent_replacement", torrent_replacement)
                        if torrent_replacement != '':
                            items = Download().listdirs()
                            if __settings__.getSetting("torrent_save") == '0':
                                dirid = xbmcgui.Dialog().select(__language__(30248), items[0])
                                if dirid == -1: return
                                dirname = items[1][dirid]
                            else:
                                dirname = __settings__.getSetting("torrent_dir")
                            Debug('[uTorrentAdd]: dirname is "' + dirname + '"')
                            self.filename = self.filename.replace('\\\\', '\\')
                            dirname, torrent_replacement = dirname.rstrip('\\/'), torrent_replacement.rstrip('\\/')
                            Debug('[Remote Torrent] Try to replace %s to %s in %s' % (
                            dirname, torrent_replacement, self.filename))
                            self.filename = self.filename.replace(dirname, torrent_replacement)
                            self.filename = os.path.join(self.filename, dirlist[ret]).replace('\\', '/')
                        else:
                            return
                    self.filename = self.filename.decode('utf-8')
                    if len(self.filename) > 1:
                        try:
                            self.addsource()
                            showMessage(__language__(30208), __language__(30230) % (self.filename))
                            if dllist[ret][1] == 100:
                                if not play:
                                    AskPlay()
                                else:
                                    PlayFile()
                            else:
                                showMessage(unicode(__language__(30208)),
                                            unicode(__language__(30275)) + unicode(dllist[ret][1]) + '%.')
                        except:
                            showMessage(__language__(30206), __language__(30231) % (self.filename), forced=True)

    def DirAdd(self):
        action = xbmcgui.Dialog()
        filename = action.browse(0, __language__(30248), 'video')
        if len(filename) > 1:
            self.filename = filename.decode('utf-8')
            if self.addstype == 'dir':
                self.stype = self.gettype()
                try:
                    self.addsource()
                    showMessage(__language__(30208), __language__(30230) % (filename.decode('utf-8', 'ignore')))
                except:
                    showMessage(__language__(30206), __language__(30231) % (filename.decode('utf-8', 'ignore')),
                                forced=True)
            elif self.addstype == 'multifile':
                i = self.addmultifile()
                showMessage(__language__(30208), __language__(30249) % (str(i)))


class PlaySource(Source):
    def handle(self):
        if self.filename or self.stype == 'xbmc' and __settings__.getSetting("alwaysxbmcstart") == 'true':
            PlayFile()
        else:
            if len(TorrentDB().get_all(True, self.showId, self.seasonId)) > 0 or self.stype == 'xbmc':
                ShowAllSources()
            else:
                if getSettingAsBool('torrent_addsource'):
                    id = chooseHASH(self.showId, self.id, self.seasonId, self.episodeId, True)
                    if id:
                        stringdata = json.loads(urllib.unquote_plus(self.stringdata))
                        stringdata['stype'] = 'BLANK'
                        AddSource(json.dumps(stringdata)).uTorrentAdd(id=id, play=True)
                        return
                AddSource()


class DeleteSource(Source):
    def handle(self):
        TorrentDB().delete(self.filename)
        showMessage(__language__(30208), __language__(30234) % (self.filename))


class ScanSource(Source):
    def handle(self):
        pass

    def scanone(self, silent=None):
        i = 0
        self.stype = self.gettype()
        if self.filename and self.filename != '':
            getdict = TorrentDB().getbyfilename(self.filename)
            self.showId = getdict['showId']
            self.seasonId = getdict['seasonId']
            if self.stype in ('multitorrent', 'torrent'):
                i = self.addmultijson()
            elif self.stype in ('rutracker', 'tpb', 'nnm', 'kz', 'torrenter'):
                xbmc.executebuiltin(
                    'XBMC.RunPlugin(plugin://plugin.video.torrenter/?action=openTorrent&silent=true&external=%s&url=%s&sdata=%s)' %
                    (
                    self.filename.split('::')[0], urllib.quote_plus(self.filename), urllib.quote_plus(self.stringdata)))
                xbmc.sleep(3000)
                self.filename = xbmcaddon.Addon(id='plugin.video.torrenter').getSetting('lastTorrent')
                i = self.addmultijson()
            elif self.stype in ('multifile', 'dir'):
                i = self.addmultifile()
            elif self.stype == 'serialu':
                a = Serialu(self.filename)
                a.get()
                i = a.add()
            elif self.stype == 'cxzto':
                i = self.scancxzto()
        if not silent:
            xbmc.sleep(1000)
            xbmc.executebuiltin('Container.Refresh')
        else:
            return i

    def add(self):
        ScanDB().add(self.filename)
        showMessage(__language__(30208), __language__(30230) % (self.filename))
        xbmc.executebuiltin('Container.Refresh')

    def scancxzto(self):
        cxzdata = json.loads(self.filename)
        episode_list = cxzEpisodeListByRel(cxzdata['href'], cxzdata['rel'], cxzdata['season'])

        i = 0
        data = Data(cookie_auth, __baseurl__ + '/shows/' + str(self.showId))
        jdata = json.loads(data.get())

        for episode in episode_list:
            doit = False
            self.episodeId = episode['episode']
            self.filename = episode['href']
            for id in jdata['episodes']:
                #Debug('[scancxzto]: seasonId - '+str(jdata['episodes'][id]['seasonNumber'])+'; episodeId - '+str(jdata['episodes'][id]['seasonNumber']))
                if jdata['episodes'][id]['seasonNumber'] == self.seasonId and jdata['episodes'][id][
                    'episodeNumber'] == self.episodeId:
                    #Debug('[scancxzto]: FOUND!')
                    self.id = int(id)
                    doit = True
                    break
            #Debug('[scancxzto]: filename - '+self.filename)
            if not TorrentDB().getbyfilename(self.filename) and doit:
                try:
                    TorrentDB().add(self.filename, 'cxzto', self.showId, self.seasonId, self.id, self.episodeId)
                    i += 1
                except:
                    pass

        if i > 1:
            showMessage(__language__(30208), __language__(30249) % (str(i)))
        elif i == 1:
            showMessage(__language__(30208), __language__(30230) % (urllib.unquote_plus(self.filename)))
        return i

    def delete(self):
        ScanDB().delete(self.filename)
        showMessage(__language__(30208), __language__(30234) % (self.filename))
        xbmc.executebuiltin('Container.Refresh')


def ScanAll():
    dialog = xbmcgui.Dialog()
    myscan = ScanDB()
    scanlist = []
    multilist = myscan.get_all()
    if len(multilist) > 0:
        for x in multilist:
            filename = unicode(x['filename'])
            ifstat = myscan.isfilename(filename)
            if ifstat == True:
                scanlist.append(filename)
    #Debug('[ScanAll]: scanlist '+str(scanlist))
    if len(scanlist) > 0:
        ok = dialog.yesno(__language__(30140), __language__(30141) + '?')
        i = 0
        if ok:
            showMessage(__language__(30277), __language__(30278))
            for filename in scanlist:
                i += ScanSource(stringdata=makeapp({"filename": filename})).scanone(True)
            xbmc.sleep(len(scanlist) * 500)
            showMessage(__language__(30263), __language__(30249) % (str(i)))
            if i > 0:
                xbmc.executebuiltin('ActivateWindow(Videos,plugin://plugin.video.myshows/?mode=50)')
            else:
                xbmc.executebuiltin('ActivateWindow(Videos,plugin://plugin.video.myshows/)')


class DeleteSourses(Source):
    def handle(self):
        if not self.seasonId:
            i = TorrentDB().deleteshow(showId=self.showId, noseasonId=False)
        else:
            i = TorrentDB().deleteseason(showId=self.showId, seasonId=self.seasonId, noid=False)
        showMessage(__language__(30208), __language__(30251) % str(i))


class AskPlay(Source):
    def handle(self):
        xbmc.sleep(1000)
        dialog = xbmcgui.Dialog()
        ok = dialog.yesno(__language__(30227), __language__(30252), self.filename)
        if ok:
            PlayFile()


class PlayFile(Source):
    def handle(self):
        if self.stype == 'xbmc':
            self.stype = 'file'
            self.filename = xbmcEpisode(self.showId, self.seasonId, self.episodeId)['file']
        if self.stype == 'file' or self.stype == 'vk-file':
            self.playfile()
        if self.stype == 'cxzto':
            if self.id not in ['0', 0, None, 'None']:
                self.filename = PlayCXZTO(self.filename)
                self.playfile()
            else:
                self.playcxzto()
        elif self.stype in ['rutracker', 'tpb', 'btchat', 'nnm', 'kz', 'torrenter']:
            if self.stype in ['tpb', 'torrenter']: showMessage(__language__(30211), __language__(30212))
            #print urllib.quote_plus(self.filename)
            #print self.filename
            xbmc.executebuiltin(
                'XBMC.RunPlugin(plugin://plugin.video.torrenter/?action=openTorrent&external=%s&url=%s&sdata=%s)' % (
                self.filename.split('::')[0], urllib.quote_plus(self.filename), self.stringdata))
        elif self.stype in ['torrent', 'multitorrent', 'url-torrent', 'json']:
            self.play_torrent()
        elif self.stype == 'lostfilm':
            xbmc.executebuiltin(
                'XBMC.RunPlugin(plugin://plugin.video.LostFilm/?mode=OpenCat&text=0&title=Title&url=%s)' % (
                urllib.quote_plus(self.filename)))
        elif self.stype == 'dir' or self.stype == 'multifile':
            myshows_files = [unicode(__language__(30232))]
            files = sorted(xbmcvfs.listdir(self.filename)[1], key=lambda x: x[0])
            myshows_files.extend(files)
            myshows_files.append(unicode(__language__(30205)))
            dialog = xbmcgui.Dialog()
            i = dialog.select(__language__(30233), myshows_files)
            if i == myshows_files.index(unicode(__language__(30232))): AddSource()
            if i == myshows_files.index(unicode(__language__(30205))): return False
            filename = os.path.join(self.filename, myshows_files[i])
            if os.path.isdir(filename):
                PlayFile(makeapp({'filename': filename}))
            else:
                try:
                    self.filename = filename.decode('utf-8')
                except:
                    self.filename = filename
                self.playfile()
        elif self.stype == 'serialu':
            i = 0
            getdat = Serialu().read()
            myshows_files = []
            myshows_items = []
            for getdata in getdat:
                getjdata = json.loads('{' + getdata + '}')
                if self.seasonId and self.seasonId != getjdata['seasonId']: continue
                myshows_files.append(getjdata['filename'])
                myshows_items.append(str('S%sE%s' % (str(getjdata['seasonId']), str(getjdata['episodeId']))))
            myshows_files.append(unicode(__language__(30205)))
            myshows_items.append(unicode(__language__(30205)))
            dialog = xbmcgui.Dialog()
            i = dialog.select(__language__(30235), myshows_items)
            if i and i not in (-1, len(myshows_files) - 1): xbmc.executebuiltin(
                'xbmc.PlayMedia("' + urllib.unquote_plus(myshows_files[i]) + '")')

    def playfile(self):
        if self.showId and self.id:
            if not self.seasonId or not self.episodeId and self.episodeId != 0:
                Debug('[PlayFile]: not self.seasonId or not self.episodeId')
                self.seasonId, self.episodeId = id2SE(self.showId, self.id)
            if self.seasonId:
                title, label = id2title(self.showId, self.id, norus=True)
                #label='%s [myshows_showId|%d|myshows_id|%d]' % (label, self.showId, self.id)
                i = xbmcgui.ListItem(label, path=self.filename.encode('utf-8'), thumbnailImage='')

                i.setInfo(type='video', infoLabels={'title': label,
                                                    'episode': self.episodeId,
                                                    'season': self.seasonId,
                                                    'tvshowtitle': title})
                i.setProperty('IsPlayable', 'true')
                xbmc.Player().play(self.filename.encode('utf-8'), i)
            else:
                Debug('[PlayFile]: did not found self.seasonId')
                xbmc.executebuiltin('xbmc.PlayMedia("' + self.filename.encode('utf-8') + '")')
        else:
            Debug('[PlayFile]: not self.showId and self.id')
            xbmc.executebuiltin('xbmc.PlayMedia("' + self.filename.encode('utf-8') + '")')

    def playcxzto(self):
        cxzdata = json.loads(self.filename)
        episode_list = cxzEpisodeListByRel(cxzdata['href'], cxzdata['rel'], cxzdata['season'])
        myshows_files = []
        myshows_items = []
        for episode in episode_list:
            myshows_files.append(episode['href'])
            myshows_items.append(episode['string'])
        myshows_files.append(unicode(__language__(30205)))
        myshows_items.append(unicode(__language__(30205)))
        dialog = xbmcgui.Dialog()
        i = dialog.select(__language__(30235), myshows_items)
        if i != None and i not in (-1, len(myshows_files) - 1): xbmc.executebuiltin(
            'xbmc.PlayMedia("' + PlayCXZTO(myshows_files[i]) + '")')


class ShowAllSources(Source):
    def handle(self):
        if self.stype == 'xbmc':
            myshows_files = [unicode(__language__(30295)), unicode(__language__(30232))]
            myshows_titles = [unicode(__language__(30295)), unicode(__language__(30232))]
        else:
            myshows_files = [unicode(__language__(30232))]
            myshows_titles = [unicode(__language__(30232))]
        getlist = TorrentDB().get_all(True, self.showId, self.seasonId)
        for k in getlist:
            myshows_files.append(makeapp(k))
            title = ''
            if str(k['seasonId']) != 'None': title = title + 'S' + int_xx(str(k['seasonId']))
            if str(k['episodeId']) != 'None': title = title + 'E' + int_xx(str(k['episodeId']))
            myshows_titles.append(title + ' ' + k['filename'].lstrip(os.path.dirname(k['filename'])))
        myshows_files.append(unicode(__language__(30205)))
        myshows_titles.append(unicode(__language__(30205)))
        dialog = xbmcgui.Dialog()
        i = dialog.select(__language__(30235), myshows_titles)
        try:
            if i == myshows_files.index(unicode(__language__(30295))): PlayFile()
        except:
            pass
        if i == myshows_files.index(unicode(__language__(30232))):
            AddSource()
        elif i == -1 or i == myshows_files.index(unicode(__language__(30205))):
            return False
        else:
            if self.id and (self.episodeId or self.episodeId == 0):
                stringdata = json.loads(urllib.unquote_plus(myshows_files[i]))
                stringdata['episodeId'] = self.episodeId
                stringdata['id'] = self.id
                Debug('[ShowAllSources]: PlayFile ' + str(stringdata))
                PlayFile(json.dumps(stringdata))
            else:
                PlayFile(myshows_files[i])


def VKSearch(showId, id):
    PluginStatus().use('vkstatus')
    data = Data(cookie_auth, __baseurl__ + '/shows/' + str(showId)).get()
    jdata = json.loads(data)

    id = str(id)
    t = jdata['title']
    e = str(jdata['episodes'][id]['episodeNumber'])
    s = str(jdata['episodes'][id]['seasonNumber'])
    a = jdata['episodes'][id]['airDate']
    et = jdata['episodes'][id]['title']
    try:
        rt = jdata['ruTitle']
    except:
        rt = jdata['title']

    dialog_items = [u'%s Сезон %s Серия %s' % (rt, s, e),
                    u'%s %s' % (t, a),
                    u'%s %s.%s' % (t, s, e),
                    u'%s Сезон %s Серия %s' % (t, s, e),
                    u'%s %s Сезон %s Эпизод' % (t, s, e),
                    u'%s Season %s Episode %s' % (t, s, e),
                    u'%s %sx%s' % (t, s, e),
                    u'%s S%sE%s' % (t, int_xx(s), int_xx(e)),
                    u'%s.S%sE%s' % (t.replace(' ', '.'), int_xx(s), int_xx(e)),
                    u'%s %s %s' % (t, a, et),
                    u'%s %s' % (t, et),
                    u'%s S%sE%s' % (StripName(t, striplist), int_xx(s), int_xx(e)),
                    u'%s %s' % (StripName(t, striplist), rev_date(a).replace('.', ' ')),
                    unicode(__language__(30205))]

    dialog = xbmcgui.Dialog()
    ret = dialog.select(__language__(30204), dialog_items)
    query = dialog_items[ret].encode('utf-8')
    if ret > -1 and ret < len(dialog_items) - 1:
        query = urllib.quote(query)
        xbmc.executebuiltin(
            'xbmc.RunPlugin("plugin://xbmc-vk.svoka.com/?query=' + query + '&mode=SEARCH&external=1&stringdata=' + urllib.quote_plus(
                '{"stype":"vk-file","showId":' + str(showId) + ',"id":' + id + '}') + '&sdata=' + str(
                '%s, %s, %s, %s') % (str(showId), s, id, e) + '")')
    return None


def LFSearch(showId, id):
    PluginStatus().use('lostfilm')
    data = Data(cookie_auth, __baseurl__ + '/shows/' + str(showId)).get()
    jdata = json.loads(data)

    id = str(id)
    t = jdata['title']
    if t == 'House': t = 'House M.D.'
    Debug('[LFSearch] t is ' + t)
    match = re.compile('(.+) \(\d{4}\)').findall(t)
    if match:
        t = match[0]
    e = str(jdata['episodes'][id]['episodeNumber'])
    s = str(jdata['episodes'][id]['seasonNumber'])

    lostlink = None
    #LFshowId=None
    int_html = get_url(cookie_auth, 'http://myshows.ru/int/controls/view/episode/' + id + '/')
    #Debug('[LFSearch] int_html: '+str(int_html))
    if int_html and 'lostfilm' in int_html:
        try:
            lostlink = re.findall('<a.*?href=\"(http://lostfilm.tv/.*?)\">', int_html)[0]
        except:
            Debug('[LFSearch]: not lostlink on id_html')
    elif int_html:
        show_html = get_url(cookie_auth, 'http://myshows.ru/view/' + id + '/')
        try:
            lostlink = re.findall('<a.*?href=\"(http://lostfilm.tv/.*?)\">', show_html)[0]
        except:
            Debug('[LFSearch]: not lostlink on show_html')

    #if LFshowId:
    sdata = '&sdata=' + str('%s, %s, %s, %s') % (str(showId), s, id, e)
    if lostlink:
        sdata = sdata + '&lostlink=' + urllib.quote_plus(
            lostlink.replace('http://lostfilm.tv', 'http://www.lostfilm.tv'))
        Debug('[LFSearch]: lostlink: ' + lostlink.replace('http://lostfilm.tv', 'http://www.lostfilm.tv'))
        #url=urllib.quote('("'+str(LFshowId)+'","'+s+'","'+int_xx(e)+'")')
    url = ('%s, %s, %s') % (t, s, int_xx(e))
    xbmc.executebuiltin('xbmc.RunPlugin("plugin://plugin.video.LostFilm/?url=' + url + '&mode=myshows' + sdata + '")')
    return None


def CXZTOSearch(showId, seasonId=None, id=None):
    data = Data(cookie_auth, __baseurl__ + '/shows/' + str(showId)).get(force_cache=True)
    jdata = json.loads(data)

    id = str(id)
    t = jdata['title']
    r = jdata['ruTitle']
    y = jdata['year']

    #Debug('[CXZTOSearch] t is '+t)
    #episode
    if id not in ['0', 'None']:
        e = int(jdata['episodes'][id]['episodeNumber'])
        s = int(jdata['episodes'][id]['seasonNumber'])
        seasons = []
        eplist = cxzEpisodeList(t, r, y, s, e)[0]
        if len(eplist) > 0:
            #print str(eplist)
            myshows_files, myshows_items = [], []
            for ep in eplist:
                myshows_files.append(ep['href'])
                myshows_items.append(ep['title'])
            myshows_files.append(unicode(__language__(30205)))
            myshows_items.append(unicode(__language__(30205)))
            if len(myshows_files) > 2:
                dialog = xbmcgui.Dialog()
                i = dialog.select(__language__(30235), myshows_items)
            else:
                i = 0
            if i != None and i not in (-1, len(myshows_files) - 1):
                stringdata = makeapp(
                    {"filename": myshows_files[i], "stype": "cxzto", "showId": int(showId), "seasonId": s,
                     "id": int(id), "episodeId": e})
                Source(stringdata).addsource()
                AskPlay(stringdata)
        else:
            showMessage("CXZ.TO", __language__(30403))
            return
    elif seasonId:
        e = None
        s = int(seasonId)
        seasons = [s]
    else:
        e = None
        s = None
        seasons = countSeasons(jdata)[0]
        #print str(seasons)

    #season/show
    for s in seasons:
        slist = cxzEpisodeList(t, r, y, s, e)[1]
        #print str(slist)
        if len(slist) > 0:
            myshows_files, myshows_items = [], []
            for season in slist:
                season["stype"] = "cxzto"
                myshows_files.append(json.dumps(season))
                myshows_items.append(season['title'])
            myshows_files.append(unicode(__language__(30205)))
            myshows_items.append(unicode(__language__(30205)))
            if len(myshows_files) > 2:
                dialog = xbmcgui.Dialog()
                i = dialog.select('%s %d' % (__language__(30138), s), myshows_items)
            else:
                i = 0
            if i != None and i not in (-1, len(myshows_files) - 1):
                stringdata = makeapp(
                    {"filename": myshows_files[i], "stype": "cxzto", "showId": int(showId), "seasonId": s})
                Source(stringdata).addsource()
                ScanSource(stringdata).scanone()
        else:
            showMessage('%s %d %s' % (__language__(30138), s, "CXZ.TO"), __language__(30403))
    return


class TorrenterSearch():
    def __init__(self, stype, showId, seasonId, id=None, episodeId=None, stop=None, silent=None):
        PluginStatus().use('torrenterstatus')
        self.stype, self.showId, self.seasonId, self.id, self.episodeId, self.silent = stype, showId, seasonId, id, episodeId, silent
        self.stypes = {'tpb': 'The Pirate Bay', 'rutracker': 'RuTracker.Org', 'btchat': 'BT-chat.com',
                       'nnm': 'NNM-Club.Ru', 'kz': 'Kino-Zal.Tv', 'torrenterall': 'All Torrenter Trackers'}
        self.externals = {'btchat': 'BTchatCom', 'rutracker': 'RuTrackerOrg', 'tpb': 'ThePirateBaySe',
                          'nnm': 'NNMClubRu', 'kz': 'Kino_ZalTv', 'torrenterall': 'torrenterall'}
        if not stop:
            self.handle()

    def handle(self):
        data = Data(cookie_auth, __baseurl__ + '/shows/' + str(self.showId)).get(force_cache=True)
        jdata = json.loads(data)

        if self.id:
            id = str(self.id)
            if id not in jdata['episodes']:
                __settings__.setSetting("forced_refresh_data", "true")
                data = Data(cookie_auth, __baseurl__ + '/shows/' + str(self.showId)).get()
                jdata = json.loads(data)
            e = str(jdata['episodes'][id]['episodeNumber'])
            a = jdata['episodes'][id]['airDate']
            et = jdata['episodes'][id]['title']
        s = str(self.seasonId)
        t = jdata['title']
        try:
            rt = jdata['ruTitle']
        except:
            rt = jdata['title']

        if self.stype in ['rutracker', 'nnm', 'kz'] or self.stype == 'torrenterall' and not self.id:
            dialog_items = [u'%s Сезон %s' % (rt, s),
                            u'%s %s 720p' % (t, s),
                            u'%s Сезон %s 720p' % (rt, s),
                            u'%s %s' % (t, s),
                            u'%s Сезон %s' % (rt, int_xx(s)),
                            u'%s Сезон %s' % (t, int_xx(s)),
                            u'%s S%s' % (StripName(t, striplist), int_xx(s)),
                            u'%s' % (rt),
                            u'%s' % (t),
                            unicode(__language__(30205))]
        else:
            dialog_items = [u'%s S%sE%s 720p' % (t, int_xx(s), int_xx(e)),
                            u'%s S%sE%s' % (t, int_xx(s), int_xx(e)),
                            u'%s %sx%s' % (t, s, e),
                            u'%s %s %s' % (t, a, et),
                            u'%s S%sE%s' % (StripName(t, striplist), int_xx(s), int_xx(e)),
                            u'%s %s' % (StripName(t, striplist), StripName(et, striplist)),
                            u'%s %s' % (StripName(t, striplist), rev_date(a).replace('.', ' ')),
                            u'%s ' % (t),
                            u'%s %s' % (t, rev_date(a)),
                            unicode(__language__(30205))]
        silent, i = '', 1
        if self.silent and self.id:
            silent, i = "&silent=true", 0
            dialog_items = [u'%s S%sE%s 720p' % (t, int_xx(s), int_xx(e)),
                            u'%s S%sE%s' % (t, int_xx(s), int_xx(e)),
                            u'%s %s' % (t, rev_date(a)),
                            u'%s %s' % (StripName(t, striplist), rev_date(a))]
        elif self.silent and not self.id and self.seasonId:
            silent, i = "&silent=true", 0
            dialog_items = [u'%s Сезон %s  720p' % (t, s),
                            u'%s Сезон %s' % (t, s),
                            u'%s Сезон %s' % (rt, s),
                            u'%s Сезон %s  720p' % (rt, s)]
        dialog = xbmcgui.Dialog()
        ret = dialog.select(__language__(30276) % self.stypes[self.stype], dialog_items)
        query = dialog_items[ret].encode('utf-8')
        if ret > -1 and ret < len(dialog_items) - i:
            url = 'plugin://plugin.video.torrenter/?action=search&url=%s&sdata=%s&external=%s%s' % \
                  (urllib.quote_plus(query),
                   urllib.quote_plus(json.dumps('{"stype":%s, "showId":%s, "seasonId":%s, "episodeId":%s, "id":%s}' %
                                                (jstr(self.stype), jstr(self.showId), jstr(self.seasonId),
                                                 jstr(self.episodeId), jstr(self.id)))), self.externals[self.stype],
                   silent)
            if self.silent:
                xbmc.executebuiltin('xbmc.RunPlugin(%s)' % (url))
            else:
                xbmc.executebuiltin('ActivateWindow(Videos,"%s")' % (url))
        return


class MoveToXBMC(Source):
    def handle(self):
        dialog = xbmcgui.Dialog()
        self.allowed_stypes = ['dir', ' multifile', 'file']
        if self.stype not in self.allowed_stypes:
            ok = dialog.yesno(__language__(30299), __language__(30298), __language__(30232) + '?')
            if ok:
                AddSource()
                self.filename = self.getfilename()
                self.stype = self.gettype()
        self.stopped = None
        if getSettingAsBool('alwayschoosemovemode'):
            ret = dialog.select(__language__(30297),
                                [__language__(30027), __language__(30028), __language__(30029), __language__(30030),
                                 __language__(30551), __language__(30205)])
            if ret >= 0 and ret < 4:
                self.movemode = ret + 1
            elif ret == 4:
                self.movemode = 10  #sub_copy
            else:
                self.movemode = None
        else:
            self.movemode = int(__settings__.getSetting("movemode"))
        if not xbmc.getCondVisibility("system.platform.windows") and self.movemode: self.movemode = self.movemode + 4
        Debug('[MoveToXBMC]: Mode is ' + str(self.movemode))

        if self.movemode in (10, 14):
            if self.stype in ['dir', ' multifile', 'file']:
                self.subs_copy()
            return

        xbmclib = __settings__.getSetting("xbmclib")
        if xbmclib == '':
            ok = dialog.yesno(__language__(30299), __language__(30500), __language__(30501))
            if ok:
                xbmclib = dialog.browse(0, __language__(30502), 'video')
                if xbmclib != '':
                    __settings__.setSetting("xbmclib", xbmclib)
            else:
                return
        elif __settings__.getSetting("askxbmclib") == 'true':
            ok = dialog.yesno(__language__(30299), __language__(30503), xbmclib)
            if ok:
                newxbmclib = dialog.browse(0, __language__(30502), 'video')
                if newxbmclib and newxbmclib != xbmclib:
                    xbmclib = newxbmclib
                    if dialog.yesno(__language__(30299), __language__(30504), xbmclib):
                        __settings__.setSetting("xbmclib", xbmclib)
        Debug('[MoveToXBMC]: xbmclib is ' + xbmclib)

        folder = self.filename
        if self.stype == 'file': folder = os.path.dirname(self.filename)
        self.orig_xbmclib = xbmclib
        if xbmclib.startswith('smb://'): xbmclib = smbtopath(xbmclib)

        if xbmclib != '' and xbmcvfs.exists(folder + os.sep):
            self.xbmclib = xbmclib
            self.title = id2title(self.showId, None, True)[0]
            success = self.move(folder)

            subtitledirs = xbmcvfs.listdir(folder)[0]
            for d in subtitledirs:
                for x in xbmcvfs.listdir(folder.encode('utf-8', 'ignore') + os.sep + d)[0]:
                    subtitledirs.append(d + os.sep + x)
            if len(subtitledirs) > 0 and success:
                subtitledirs.insert(0, __language__(30505))
                subtitledirs_titles = [__language__(30505)]
                for i in range(1, len(subtitledirs)):
                    subtitledirs_titles.append(subtitledirs[i] + ' (%d)' % self.count_subs(
                        folder.encode('utf-8', 'ignore') + os.sep + subtitledirs[i]))
                ret = dialog.select(__language__(30506), subtitledirs_titles)
                if self.movemode in (3, 4):
                    self.movemode = 1
                    renamebool = False
                else:
                    renamebool = True
                if ret:
                    self.move(os.path.join(folder, subtitledirs[ret].decode('utf-8', 'ignore')), renamebool)

            if success:
                items = [__language__(30507), __language__(30508), self.orig_xbmclib]
                ret = dialog.select(__language__(30509), items)
                if ret == 1:
                    xbmc.executebuiltin('XBMC.UpdateLibrary(video)')
                elif ret > 1:
                    xbmc.executebuiltin('XBMC.UpdateLibrary(video,' + items[ret] + ')')

    def move(self, folder, renamebool=True):
        import shutil

        filelist = xbmcvfs.listdir(folder)[1]
        movelist = []
        newfolder = self.mkdirs(self.seasonId)
        if self.stype == 'file':
            for i in range(0, len(filelist)):
                try:
                    filename_if = self.filename[:len(self.filename) - len(self.filename.split('.')[-1]) - 1]
                    filename_if = os.path.split(filename_if)[-1]
                    filename_if2 = filelist[i][:len(filename_if)]
                    if filelist[i].lower().split('.')[-1] in allowed_ext and \
                                    filename_if.lower() == filename_if2.lower():
                        movelist.append((filelist[i], self.episodeId, self.seasonId))
                except:
                    Debug('[move]: except for i=' + str(i))
        elif self.stype in ['dir', ' multifile']:
            if len(filelist) > 1:
                cutfilelist = cutFileNames(filelist)
            else:
                cutfilelist = filelist
            for i in range(0, len(filelist)):
                FNP = FileNamesPrepare(cutfilelist[i])
                try:
                    movelist.append((filelist[i], FNP[1], FNP[0]))
                except:
                    Debug('[MoveToXBMC][move]: Error finding epnum for ' + filelist[i])
                    movelist.append((filelist[i], None, None))

        if folder.startswith('smb://'): folder = smbtopath(folder)

        if self.movemode in (1, 2, 3, 4):
            newfolder = newfolder.decode('utf-8', 'ignore')

        if self.movemode in (2, 6):
            uTorrentCheck = self.uTorrentCheck(folder, 'remove')
            Debug('[MoveToXBMC][move]: uTorrent id is ' + str(uTorrentCheck))

        if self.movemode in (4, 8):
            self.uTorrentCheck(folder, 'stop')
            Debug('[MoveToXBMC][move]: uTorrent id is ' + str(self.stopped))

        if self.movemode == 3:  #Windows: Symbolic link
            junction_path = os.path.join(__addonpath__, 'resources', 'junction.exe')
            if not xbmcvfs.exists(junction_path): shutil.move(junction_path.replace('junction.exe', 'junction'),
                                                              junction_path)
            delete = xbmcvfs.rmdir(newfolder)
            if not delete:
                if xbmcgui.Dialog().yesno(__language__(30510), __language__(30511), newfolder):
                    shutil.rmtree(newfolder, ignore_errors=True)
            folder = folder.rstrip('\\')
            Debug('[MoveToXBMC][move]: Linking "' + folder + '" "' + newfolder + '"')
            os.system(junction_path + ' "' + newfolder + '" "' + folder + '"')
            return True

        if self.movemode == 4:  #Windows: backward Symbolic link
            delete = xbmcvfs.rmdir(newfolder)
            if not delete:
                if xbmcgui.Dialog().yesno(__language__(30510), __language__(30511), newfolder):
                    shutil.rmtree(newfolder, ignore_errors=True)
            shutil.move(folder, newfolder)
            junction_path = os.path.join(__addonpath__, 'resources', 'junction.exe')
            if not xbmcvfs.exists(junction_path): shutil.move(junction_path.replace('junction.exe', 'junction'),
                                                              junction_path)
            folder = folder.rstrip('\\')
            newfolder = newfolder.rstrip('\\')
            Debug('[MoveToXBMC][move]: Linking "' + newfolder + '" "' + folder + '"')
            os.system(junction_path + ' "' + folder + '" "' + newfolder + '"')
            return True

        if self.movemode == 9:  #Test
            print self.uTorrentCheck(folder, 'stop')
            return False

        Debug('[MoveToXBMC][move] movelist:' + str(movelist))
        for file, episodeId, seasonId in movelist:
            if not seasonId: seasonId = self.seasonId
            if episodeId:
                newfilename = "%s.S%sE%s" % (PrepareFilename(self.title).replace(' ', '.'),
                                             int_xx(seasonId), int_xx(episodeId)) + '.' + file.split('.')[-1]
            else:
                newfilename = file
            if self.movemode not in (3, 4):
                newfolder = self.mkdirs(seasonId)
            newfolder = newfolder.decode('utf-8', 'ignore')
            file = file.decode('utf-8', 'ignore')
            newfilename = newfilename.decode('utf-8', 'ignore')
            if self.movemode == 1 or self.movemode == 5:  #Copy
                shutil.copyfile(os.path.join(folder, file), os.path.join(newfolder, file))
                if renamebool: shutil.move(os.path.join(newfolder, file), os.path.join(newfolder, newfilename))
            if self.movemode == 2 or self.movemode == 6:  #Move
                shutil.move(os.path.join(folder, file), os.path.join(newfolder, newfilename))
            if self.movemode == 7:
                os.symlink(os.path.join(folder, file), os.path.join(newfolder, newfilename))
            if self.movemode == 8:  #Move & backward Symbolic link
                shutil.move(os.path.join(folder, file), os.path.join(newfolder, newfilename))
                os.symlink(os.path.join(newfolder, newfilename), os.path.join(folder, file))

        if self.movemode in (4, 8):
            self.uTorrentCheck(folder, 'start')
        return True

    def mkdirs(self, seasonId):
        prepare = PrepareFilename(self.title)
        newdir = os.path.join(self.xbmclib, prepare, 'Season ' + str(seasonId))
        if not newdir.startswith('\\\\'): xbmcvfs.mkdirs(newdir)
        if not os.path.exists(newdir):
            newdir = self.xbmclib
            for subdir in (prepare, 'Season ' + str(seasonId)):
                newdir = os.path.join(newdir, subdir)
                if not os.path.exists(newdir):
                    os.mkdir(newdir)
        return newdir

    def count_subs(self, folder):
        count = 0
        filelist = xbmcvfs.listdir(folder)[1]
        for i in range(0, len(filelist)):
            if filelist[i].lower().split('.')[-1] in subs_ext:
                count += 1
        return count

    def uTorrentCheck(self, folder, action):
        socket.setdefaulttimeout(3)
        ulist = Download().list()
        socket.setdefaulttimeout(TimeOut().timeout())
        if ulist:
            utordirs = []
            for data in ulist: utordirs.append((data['id'], data['name']))
            foldname = folder[len(os.path.dirname(folder)) + 1:]
            for id, dir in utordirs:
                #dir=dir[len(os.path.dirname(dir))+1:]
                if foldname == dir:
                    dialog = xbmcgui.Dialog()
                    ok = dialog.yesno(__language__(30512), __language__(30513) % (action), dir)
                    if ok:
                        Download().action_simple(action, id)
                        if action != 'start': xbmc.sleep(10000)
                        return id

    def subs_copy(self):
        if self.stype == 'file':  #один файл
            folder = os.path.dirname(self.filename)
        else:
            folder = self.filename
        subtitledirs = xbmcvfs.listdir(folder)[0]
        for d in subtitledirs:
            for x in xbmcvfs.listdir(folder.encode('utf-8', 'ignore') + os.sep + d)[0]:
                subtitledirs.append(d + os.sep + x)
        if len(subtitledirs) > 0:
            subtitledirs.insert(0, __language__(30505))
            subtitledirs_titles = [__language__(30505)]
            if self.stype == 'file':  #один файл
                for i in range(1, len(subtitledirs)):
                    filelist = xbmcvfs.listdir(folder.encode('utf-8', 'ignore') + os.sep + subtitledirs[i])[1]
                    for x in range(0, len(filelist)):
                        if isSubtitle(self.filename, filelist[x], only_subs=True):
                            subtitledirs_titles.append(subtitledirs[i])
                            break
            else:
                for i in range(1, len(subtitledirs)):
                    subtitledirs_titles.append(subtitledirs[i] + ' (%d)' % self.count_subs(
                        folder.encode('utf-8', 'ignore') + os.sep + subtitledirs[i]))
            ret = xbmcgui.Dialog().select(__language__(30506), subtitledirs_titles)
            if ret != -1:
                i = 0
                #import shutil
                #if folder.startswith('smb://'):folder=smbtopath(folder)
                if self.stype == 'file':
                    newfolder = os.path.join(folder, subtitledirs_titles[ret].decode('utf-8', 'ignore'))
                else:
                    newfolder = os.path.join(folder, subtitledirs[ret].decode('utf-8', 'ignore'))
                Debug("[subs_copy]: newfolder %s" % (newfolder))
                for file in xbmcvfs.listdir(newfolder)[1]:
                    if self.stype == 'file':
                        if isSubtitle(self.filename, file, only_subs=True):
                            i = i + 1
                            xbmcvfs.copy(os.path.join(newfolder, file), os.path.join(folder, file))
                    else:
                        i = i + 1
                        xbmcvfs.copy(os.path.join(newfolder, file), os.path.join(folder, file))
                showMessage(__language__(30552), __language__(30553) % (i))


def chooseDir(urls, path=None):
    paths = [unicode(__language__(30254))]
    if not path:
        for url in urls:
            ext = url[:url.rfind('\\')]
            if ext != url[:len(url) - 1] and ext not in paths:
                paths.append(ext)
        return paths
    else:
        files = []
        for url in urls:
            if path != paths[0]:
                ext = str(url).replace(path + '\\', '')
                if ext and ext != url:
                    ixt = ext[:ext.rfind('\\')]
                    if ixt == ext[:len(ext) - 1]:
                        files.append(url)
            else:
                ext = url[:url.rfind('\\')]
                if ext == url[:len(url) - 1]:
                    files.append(url)
        return files


def prefix(showId=None, seasonId=None, id=None, stype=None, episodeNumber=None):
    if not stype:
        if showId:
            getdict = TorrentDB().get(showId=showId, seasonId=seasonId, id=id, noid=True,
                                      noseasonId=invert_bool(seasonId))
            try:
                stype = getdict['stype']
            except:
                pass
        else:
            getlist = TorrentDB().get_all(False, showId, seasonId)
            for k in getlist:
                if id and k['id'] == id or not id and seasonId and k['seasonId'] == seasonId:
                    stype = k['stype']
        if not stype and episodeNumber:  #XBMC
            #if xbmcEpisode(showId, seasonId, episodeNumber):
            #    stype='xbmc'
            return ''
    stypes = ['json', 'vk-file', 'url-file', 'btchat', 'dir', 'file', 'torrent', 'multifile', 'multitorrent',
              'serialu-file', 'serialu', 'rutracker', 'tpb', 'nnm', 'kz', 'torrenter', 'xbmc', 'lostfilm', 'cxzto']
    prefixes = ['JS', 'VK', 'UF', 'BT', 'D', 'F', 'T', 'MF', 'MT', 'SF', 'SU', 'RU', 'PB', 'NN', 'KZ', 'TR', 'XBMC',
                'LF', 'CZ']
    prefix = None
    if stype:
        prefix = ('[B][%s][/B] ' % (prefixes[stypes.index(stype)]))
    if not prefix: prefix = ''
    return prefix


def xbmcEpisode(showId, seasonId, episodeNumber):
    from utilities import xbmcJsonRequest

    title = id2title(showId, None, norus=True)[0]
    shows = xbmcJsonRequest(
        {'jsonrpc': '2.0', 'method': 'VideoLibrary.GetTVShows', 'params': {'properties': ['title']}, 'id': 0})
    if not shows:
        Debug('[Prefix] xbmc json request was empty.')
        return
    if 'tvshows' in shows:
        shows = shows['tvshows']
    else:
        Debug("[Prefix] Key 'tvshows' not found")
        return
    for show in shows:
        if show['title'] == title.decode('utf-8'):
            episodes = xbmcJsonRequest({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetEpisodes',
                                        'params': {'tvshowid': show['tvshowid'], 'season': seasonId,
                                                   'properties': ['episode', 'file']}, 'id': 0})
            if 'episodes' in episodes:
                episodes = episodes['episodes']
                for episode in episodes:
                    if episode['episode'] == episodeNumber:
                        return episode


def isSubtitle(filename, filename2, only_subs=False):
    filename_if = filename[:len(filename) - len(filename.split('.')[-1]) - 1]
    filename_if = filename_if.split('/')[-1].split('\\')[-1]
    filename_if2 = filename2.split('/')[-1].split('\\')[-1][:len(filename_if)]
    #print 'Compare '+filename_if.lower()+' and '+filename_if2.lower()+' and '+filename2.lower().split('.')[-1]
    if only_subs:
        ext = subs_ext
    else:
        ext = allowed_ext
    if filename2.lower().split('.')[-1] in ext and \
                    filename_if.lower() == filename_if2.lower():
        return True
    return False