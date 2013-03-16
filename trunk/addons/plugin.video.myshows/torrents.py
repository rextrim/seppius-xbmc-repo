# -*- coding: utf-8 -*-

import urllib, socket, time, os.path, base64
import xbmcplugin, xbmcgui, xbmc, xbmcaddon, xbmcvfs

try:
    from sqlite3 import dbapi2 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite

from functions import *
from net import *

try:
    from TSCore import TSengine as tsengine
    torrmode=True
except:
    torrmode=False

try:
    import libtorrent
    libmode=True
except:
    libmode=False

__version__ = "1.5.0"
__plugin__ = "MyShows.ru " + __version__
__author__ = "DiMartino"
__settings__ = xbmcaddon.Addon(id='plugin.video.myshows')
__language__ = __settings__.getLocalizedString
ruName=__settings__.getSetting("ruName")
cookie_auth=__settings__.getSetting("cookie_auth")
socket.setdefaulttimeout(60)
__addonpath__= __settings__.getAddonInfo('path')
icon   = __addonpath__+'/icon.png'
__tmppath__= os.path.join(__addonpath__, 'tmp')
striplist=['the', 'tonight', 'show', 'with', '  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ']

aceport=62062

try:
    fpath= os.path.expanduser("~")
    pfile= os.path.join(fpath,'AppData\Roaming\TorrentStream\engine' ,'acestream.port')
    gf = open(pfile, 'r')
    aceport=int(gf.read())
    gf.close()
    print aceport
except: aceport=62062


class TorrentDB:
    def __init__(self):
        dirname = xbmc.translatePath('special://temp')
        for subdir in ('xbmcup', sys.argv[0].replace('plugin://', '').replace('/', '')):
            dirname = os.path.join(dirname, subdir)
            if not xbmcvfs.exists(dirname):
                xbmcvfs.mkdir(dirname)
        self.dbfilename = os.path.join(dirname, 'data.db3')
        if not xbmcvfs.exists(self.dbfilename):
            creat_db(self.dbfilename)

    def get_all(self, noid=False, showId=None, seasonId=None, noseasonId=False):
        self._connect()
        if not showId: self.where=''
        else:
            self.where=' where showId='+str(showId)
            if seasonId: self.where+=' and seasonId='+str(seasonId)
            elif noseasonId==True: self.where+=' and seasonId is null'
            if noid: self.where+=' and id is null'
        self.cur.execute('select filename, stype, showId, seasonId, id, episodeId from sources'+self.where+' order by addtime desc')
        #xbmc.log(str('select filename, stype, showId, seasonId, id, episodeId from sources'+self.where+' order by addtime desc'))
        res = [{'filename': x[0], 'stype': x[1], 'showId': x[2], 'seasonId': x[3], 'id': x[4], 'episodeId': x[5]} for x in self.cur.fetchall()]
        ##xbmc.log(str(res))
        self._close()
        return res

    def get(self, showId, id=None, seasonId=None, noid=False, noseasonId=False):
        self._connect()
        self.where=' where showId='+str(showId)
        if id: self.where+=' and id='+str(id)
        elif noid==True: self.where+=' and id is null'
        if seasonId: self.where+=' and seasonId='+str(seasonId)
        elif noseasonId==True: self.where+=' and seasonId is null'
        #xbmc.log(str('select filename, stype, showId, seasonId, id, episodeId  from sources'+self.where+' order by addtime desc'))
        self.cur.execute('select filename, stype, showId, seasonId, id, episodeId from sources'+self.where)
        try:
            x=self.cur.fetchone()
            res = {'filename': x[0], 'stype': x[1], 'showId': x[2], 'seasonId': x[3], 'id': x[4], 'episodeId': x[5]}
            #xbmc.log(str(res))
        except: res=None
        self._close()
        return res

    def getbyfilename(self, filename):
        self._connect()
        if not '"' in list(filename):
            self.where=' where filename="'+filename+'"'
        else:
            self.where=" where filename='"+filename+"'"
        self.cur.execute('select filename, stype, showId, seasonId, id, episodeId from sources'+self.where)
        #xbmc.log(str('select filename, stype, showId, seasonId, id, episodeId  from sources'+self.where+' order by addtime desc'))
        x=self.cur.fetchone()
        try: res = {'filename': x[0], 'stype': x[1], 'showId': x[2], 'seasonId': x[3], 'id': x[4], 'episodeId': x[5]}
        except: res=None
        #xbmc.log(str(res))
        self._close()
        return res

    def countshowId(self, showId):
        self._connect()
        self.where=' where showId='+str(showId)+''
        self.cur.execute('select count(showId) from sources'+self.where)
        x=self.cur.fetchone()
        res=x[0]
        #xbmc.log(str(res))
        self._close()
        return res

    def add(self, filename, stype, showId, seasonId=None, id=None, episodeId=None):
        self._connect()
        try:self.cur.execute('insert into sources(addtime, filename, stype, showId, seasonId, id, episodeId) values(?,?,?,?,?,?,?)', (int(time.time()), filename, stype, showId, seasonId, id, episodeId))
        except: self.cur.execute('insert into sources(addtime, filename, stype, showId, seasonId, id, episodeId) values(?,?,?,?,?,?,?)', (int(time.time()), unicode(filename.decode('utf-8')), stype, showId, seasonId, id, episodeId))
        self.db.commit()
        self._close()

    def delete(self, filename):
        self._connect()
        if not '"' in list(unicode(filename)):
            self.cur.execute('delete from sources where filename=("'+unicode(filename)+'")')
        else:
            self.cur.execute("delete from sources where filename=('"+unicode(filename)+"')")
        self.db.commit()
        self._close()

    def deleteseason(self, showId, seasonId, noid=False):
        self._connect()
        self.where=' where showId='+str(showId)+' and seasonId='+str(seasonId)
        if noid==True: self.where+=' and id is null'
        else: self.where+=' and id not null'
        self.cur.execute('select count(filename) from sources'+self.where)
        self.i=self.cur.fetchone()
        if self.i[0]>0:
            self.cur.execute('delete from sources'+self.where)
            self.db.commit()
        self._close()
        return self.i[0]

    def deleteshow(self, showId, noseasonId=False):
        self._connect()
        self.where=' where showId='+str(showId)
        if noseasonId==True: self.where+=' and seasonId is null'
        self.cur.execute('select count(filename) from sources'+self.where)
        self.i=self.cur.fetchone()
        if self.i[0]>0:
            self.cur.execute('delete from sources'+self.where)
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
            self.where=' where filename="'+unicode(filename)+'"'
        else:
            self.where=" where filename='"+unicode(filename)+"'"
        try: self.cur.execute('select count(filename) from scan'+self.where)
        except:
            self.cur.execute('create table scan(addtime integer, filename varchar(32) PRIMARY KEY)')
            self.db.commit()
            self.cur.execute('select count(filename) from scan'+self.where)
        x=self.cur.fetchone()
        res=x[0]
        self._close()
        if res>0: res=True
        else: res=False
        return res

    def get_all(self):
        self._connect()
        stypelist=['multifile', 'multitorrent','serialu','rutracker']
        self.where=' where stype="unrealstuff"'
        for stype in stypelist:
            self.where+=' OR stype="'+str(stype)+'"'
        self.cur.execute('select filename, stype, showId, seasonId, id, episodeId from sources'+self.where+' order by addtime desc')
        res = [{'filename': x[0], 'stype': x[1], 'showId': x[2], 'seasonId': x[3], 'id': x[4], 'episodeId': x[5]} for x in self.cur.fetchall()]
        self._close()
        return res

    def delete(self, filename):
        self._connect()
        if not '"' in list(unicode(filename)):
            self.cur.execute('delete from scan where filename=("'+unicode(filename)+'")')
        else:
            self.cur.execute("delete from scan where filename=('"+unicode(filename)+"')")
        self.db.commit()
        self._close()

class Source:
    def __init__(self, stringdata=None):
        #xbmc.log('DAMN STRINGDATA IN HERE:'+str(stringdata))
        if not stringdata:
            params=get_params()
            stringdata = params['stringdata']
            #xbmc.log('DAMN GET_PARAMS STRINGDATA IN HERE:'+str(stringdata))
        self.stringdata=stringdata
        self.apps=get_apps(stringdata)
        #xbmc.log('DAMN UNQUOTED SELF.APPS IN HERE:'+str(self.apps))

        self.filename   = None
        self.showId     = None
        self.seasonId   = None
        self.mode       = None
        self.id         = None
        self.episodeId  = None
        self.ind        = None
        self.action     = None
        self.title      = None
        self.stype      = None
        self.myback_url = None


        try:    self.showId = self.apps['showId']
        except: pass
        try:    self.seasonId = self.apps['seasonId']
        except: pass
        try:    self.mode = int(self.apps['mode'])
        except: pass
        try:    self.id = self.apps['id']
        except: pass
        try:    self.episodeId = self.apps['episodeId']
        except: pass
        try:    self.ind = self.apps['ind']
        except: pass
        try:    self.action = self.apps['action']
        except: pass
        try:    self.title = str(self.apps['title'])
        except: pass
        try:    self.filename = self.getfilename()
        except: pass
        try:    self.stype = self.gettype()
        except: pass
        try:    self.myback_url = params['myback_url']
        except: pass

        try:
            xbmc.log('[MY SOURCE STYPE]: '+str(self.stype))
            xbmc.log('FILENAME HERE FROM GETDICT '+self.filename.decode('utf-8'))
        except: pass
        self.handle()

    def getfilename(self):
        try:
            self.filename = self.apps['filename']
            return urllib.unquote_plus(self.apps['filename']).decode('utf-8')
        except:
            getdict=TorrentDB().get(self.showId, self.id, self.seasonId, invert_bool(self.id))
            try: print ('FILENAME IN GETFILEANEM FROM GETDICT '+getdict['filename'].decode('utf-8'))
            except: pass
            try: return getdict['filename'].decode('utf-8')
            except:
                try:
                    return getdict['filename']
                except: return None

    def gettype(self):
        stype=None
        try:
            stype = self.apps['stype']
            return stype
        except:
            if self.filename:
                try:
                    #print self.filename
                    dumps=TorrentDB().getbyfilename(self.filename)
                    jdumps=json.loads(dumps)
                    stype=jdumps['stype']
                    return stype
                except:
                    #xbmc.log('FILENAME IN GETTYPE'+self.filename)
                    self.stypes=[r'json', r'vk-file', r'url-file', r'btchat', r'rutracker',r'tpb']
                    self.fnames=['{.*?}', 'http://.*?vk\.com.*?','http://.*?\.avi|mp4|mkv|flv|mov|vob|wmv|ogm|asx|mpg|mpeg|avc|vp3|fli|flc|m4v$', 'BTchatCom::.+', 'RuTrackerOrg::.+', 'ThePirateBaySe::.+']
                    self.i=-1
                    for fn in self.fnames:
                        self.i+=1
                        #xbmc.log(str(self.i)+':'+str(fn))
                        self.match=re.compile(str(fn), re.I | re.DOTALL).match(self.filename)
                        if self.match:
                            stype=self.stypes[self.i]
                            break
                    if stype=='json':
                        if json.loads(self.filename)['stype'] not in ('btchat', 'torrent', 'rutracker', 'tpb'):
                            stype=json.loads(self.filename)['stype']
                    elif stype not in ['vk-file', 'url-file', 'btchat', 'rutracker', 'tpb']:
                        if os.path.isdir(self.filename):
                            stype='dir'
                        elif self.filename.rfind('.torrent', len(self.filename)-8)==-1:
                            stype='file'
                        else:
                            stype='torrent'
                    return stype

            else:
                #xbmc.log('NO FILENAME IN GETTYPE '+str(self.filename))
                return None

    def addsource(self):
        try:
            TorrentDB().add(self.filename, self.stype, self.showId, self.seasonId, self.id, self.episodeId)
            showMessage(__language__(30208), __language__(30230) % self.filename)
        except: showMessage(__language__(30206), __language__(30237) % self.filename)

    def handle(self):
        pass

    def addjson(self):
        out=self.out()
        if out=='Ok':
            myshows_items=[]
            myshows_files=[]
            for k,v in self.filelist:
                stringdata = ('{"filename":"%s", "stype":"%s", "title":"%s", "ind":%s}' % (urllib.quote_plus(self.filename),self.stype,urllib.quote_plus(k),v))
                myshows_files.append(str(k)+'|:|'+str(stringdata))
            if len(myshows_files)==1:
                ret=0
                myshows_files[0]=unicode(myshows_files[0]).split('|:|')[1]
            else:
                myshows_files.sort()
                for x in myshows_files: myshows_items.append(urllib.unquote_plus(x).split('|:|')[0])
                for x in myshows_files: myshows_files[myshows_files.index(unicode(x))]=unicode(x).split('|:|')[1]
                myshows_items.append(unicode(__language__(30205)))
                myshows_files.append(unicode(__language__(30205)))

                dialog = xbmcgui.Dialog()
                ret = dialog.select(__language__(30223), myshows_items)
                if ret==myshows_items.index(unicode(__language__(30205))): return None
            runstring={"filename":myshows_files[ret], "stype":"json", "showId":self.showId, "episodeId":self.episodeId, "id":self.id, "seasonId":self.seasonId}
            sys_url = sys.argv[0] + '?mode=3010&stringdata='+makeapp(runstring)
            xbmc.executebuiltin('xbmc.RunPlugin("'+sys_url+'")')
        if not self.libmode:self.TSplayer.end()

    def out(self):
        #self.libmode=False
        self.libmode=libmode
        if int(__settings__.getSetting("torplayer"))==0 and self.libmode and torrmode:
            self.libmode=False
        if self.stype=='url-torrent':
            self.TSplayer=tsengine()
            try: out=self.TSplayer.load_torrent(self.filename,'TORRENT',port=aceport)
            except: out=self.TSplayer.load_torrent(urllib.unquote_plus(self.filename),'TORRENT',port=aceport)
            self.filelist=self.TSplayer.files.iteritems()
        else:
            self.stype='torrent'
            if not self.libmode:
                try: f = open(self.filename, 'rb')
                except:
                    try:f = open(urllib.unquote_plus(self.filename), 'rb')
                    except:
                        showMessage('Fail!', 'No such file or directory!')
                        return
                buf=f.read()
                f.close
                self.torr_link=base64.b64encode(buf)
                self.TSplayer=tsengine()
                out=self.TSplayer.load_torrent(self.torr_link,'RAW')
                self.filelist=self.TSplayer.files.iteritems()
            else:
                self.filelist=[]
                if os.path.exists(self.filename):
                    torrentFileInfo = libtorrent.torrent_info(self.filename)
                    s=torrentFileInfo.files()
                    for f in s:
                        self.filelist.append((f.path[f.path.find('\\')+1:],s.index(f)))
                        #print str((f.path[f.path.find('\\')+1:],s.index(f)))
                out='Ok'
        return out

    def addmultijson(self):
        i=0
        ind=-1
        #print '1ADDMULTIJSON IN DA HOUSE WITH FILENAME LOL: '+self.filename+' AND STYPE MTFKA '+self.stype
        out=self.out()
        myshows_items=[]
        myshows_files=[]
        myshows_temp=[]
        myshows_items_indexes={}
        if out=='Ok':
            for k,v in self.filelist:
                ind+=1
                stringdata = ('{"filename":"%s", "stype":"%s", "title":"%s", "ind":%s}' % (urllib.quote_plus(self.filename),self.stype,urllib.quote_plus(k),v))
                myshows_files.append((str(k),str(stringdata),ind))

            if len(myshows_files)==1:
                myshows_files[0]=unicode(myshows_files[0][1])
            elif len(myshows_files)>1:
                #myshows_files=sorted(myshows_files, key=lambda x: x[0])
                for x in myshows_files: myshows_items.append(urllib.unquote_plus(x[0]))
                for x in myshows_files: myshows_items_indexes[urllib.unquote_plus(x[0])]=x[2]
                for x in myshows_files: myshows_files[myshows_files.index(x)]=unicode(x[1])

                myshows_temp=getDirList(None, myshows_items)

                #print 'FUCK 1'+str(myshows_temp)+str(len(chooseDir(myshows_temp)))

                if len(chooseDir(myshows_temp))>1:
                    dialog = xbmcgui.Dialog()
                    ret = dialog.select(__language__(30238), chooseDir(myshows_temp))
                else: ret=0
                myshows_temp=chooseDir(myshows_temp, unicode(chooseDir(myshows_temp)[ret]))
                #print 'FUCK 2'+str(myshows_temp)
                data= Data(cookie_auth, 'http://api.myshows.ru/shows/'+str(self.showId))
                jdata = json.loads(data.get())

                if len(myshows_temp)>1: cutlist=cutFileNames(myshows_temp)
                else: cutlist=myshows_temp
                for fn in cutlist:
                    x=FileNamesPrepare(fn)
                    self.episodeId=x[1]
                    for id in jdata['episodes']:
                        if not x[0]: x[0]=self.seasonId
                        if jdata['episodes'][id]['seasonNumber']==x[0] and jdata['episodes'][id]['episodeNumber']==x[1]:
                            self.seasonId=x[0]
                            self.id=int(id)
                            break
                    self.filename=myshows_files[myshows_items_indexes[myshows_temp[cutlist.index(fn)]]]
                    if not TorrentDB().getbyfilename(self.filename):
                        #print 'adasdadsadasdas'
                        try:
                            TorrentDB().add(self.filename, "json", self.showId, self.seasonId, self.id, x[1])
                            i+=1
                            filename=str(myshows_files[cutlist.index(fn)])
                        except:
                            #print 'ZANYATO BIATCH'+str(x[1])+myshows_files[cutlist.index(fn)]+' '+str(self.showId)+' '+str(self.seasonId)+' '+str(self.id)+' '+str(x[1])
                            pass
                    else:
                        #print 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
                        pass

                if i>1:
                    showMessage(__language__(30208), __language__(30249) % (str(i)))
                elif i==1:
                    showMessage(__language__(30208), __language__(30230) % (urllib.unquote_plus(filename)))
        if not self.libmode: self.TSplayer.end()
        return i

    def addmultifile(self):
        i=0
        filename=self.filename
        data= Data(cookie_auth, 'http://api.myshows.ru/shows/'+str(self.showId))
        jdata = json.loads(data.get())
        dirlist=getDirList(filename)
        if len(dirlist)>1: cutlist=cutFileNames(dirlist)
        else: cutlist=dirlist
        #print 'BEGINSDA'+str(cutlist)
        for fn in cutlist:
            x=FileNamesPrepare(fn)
            if x:
                self.filename=os.path.join(filename, dirlist[cutlist.index(fn)])
                self.stype='file'
                self.episodeId=x[1]
                for id in jdata['episodes']:
                    if not self.seasonId: self.seasonId=x[0]
                    if jdata['episodes'][id]['seasonNumber']==self.seasonId and jdata['episodes'][id]['episodeNumber']==x[1]:
                        self.id=int(id)
                        break
                if not TorrentDB().getbyfilename(self.filename):
                    try:
                        TorrentDB().add(self.filename, self.stype, self.showId, self.seasonId, self.id, self.episodeId)
                        i+=1
                    except:
                        #print 'ZANYATO BIATCH'+str(x[1])+self.filename+' '+str(self.showId)+' '+str(self.seasonId)+' '+str(self.id)+' '+str(x[1])
                        pass
        try:TorrentDB().add(filename, 'multifile', self.showId, self.seasonId)
        except: pass
        if i>1:
            showMessage(__language__(30208), __language__(30249) % (str(i)))
        elif i==1:
            showMessage(__language__(30208), __language__(30230) % (urllib.unquote_plus(self.filename)))
        return i

    def play_torrent(self):
        #print '1PLAY URL IN DA HOUSE WITH FILENAME LOL: '+self.filename+' AND STYPE MTFKA '+self.stype
        skip=False
        if self.stype=='json':
            skip=True
            apps=json.loads(self.filename)
            self.filename=apps['filename']
            self.stype=apps['stype']

        #print 'PLAY URL IN DA HOUSE WITH FILENAME LOL: '+self.filename+' AND STYPE MTFKA '+self.stype
        out=self.out()
        #print '2PLAY URL IN DA HOUSE WITH FILENAME LOL: '+urllib.unquote_plus(self.filename)+' AND STYPE MTFKA '+self.stype
        if out=='Ok' and not skip:
            myshows_items=[]
            myshows_files=[]
            for k,v in self.filelist:
                stringdata = ('{"filename":"%s", "title":"%s", "ind":%s}' % (urllib.quote_plus(self.filename),urllib.quote_plus(k),v))
                myshows_files.append(str(k)+'|:|'+str(stringdata))
            myshows_files.sort()
            for x in myshows_files: myshows_items.append(urllib.unquote_plus(x).split('|:|')[0])
            for x in myshows_files: myshows_files[myshows_files.index(unicode(x))]=unicode(x).split('|:|')[1]
            print str(myshows_files)
            myshows_items.append(unicode(__language__(30205)))
            myshows_files.append(unicode(__language__(30205)))

            dialog = xbmcgui.Dialog()
            if len(myshows_items)>1: myshows_items=cutFileNames(myshows_items)
            ret = dialog.select(__language__(30223), myshows_items)
            if ret!=-1 and ret!=myshows_items.index(unicode(__language__(30205))):
                apps=json.loads(myshows_files[ret])
                self.play_it(apps)

        if out=='Ok' and skip:
            self.play_it(apps)
        if not self.libmode:self.TSplayer.end()

    def play_it(self, apps):
        #xbmc.log('THIS !@ '+unicode(apps))
        self.filename = urllib.unquote_plus(apps['filename'])
        self.title = urllib.unquote_plus(apps['title'])
        self.ind = apps['ind']
        if not self.libmode:
            self.TSplayer.play_url_ind(int(self.ind),self.title, str(icon), '')
        else:
            torrenter_setting=xbmcaddon.Addon(id='plugin.video.torrenter')
            torrenter_setting.setSetting("lastTorrent", self.filename)
            xbmc.executebuiltin('xbmc.RunPlugin("plugin://plugin.video.torrenter/?action=playTorrent&external=1&url='+str(self.ind)+'")')

class DownloadSource(Source):
    def handle(self):
        success=None
        self.ind=None
        if self.stype in ['json','btchat', 'torrent', 'multitorrent', 'rutracker','tpb']:

            if __settings__.getSetting("torrent_save")=='0':
                action=xbmcgui.Dialog()
                filename=action.browse(0, __language__(30248), 'video')
                if len(filename)>1:dirname=filename
                else: return
            else:
                dirname=__settings__.getSetting("torrent_dir")

            if self.stype=='json':
                self.stype=json.loads(self.filename)['stype']
                self.ind=json.loads(self.filename)['ind']
                self.filename = json.loads(self.filename)['filename']
            elif self.stype in ('rutracker',):
                xbmc.executebuiltin('XBMC.RunPlugin(plugin://plugin.video.torrenter/?action=openTorrent&silent=true&external=%s&url=%s&sdata=%s)' % (self.filename.split('::')[0],urllib.quote_plus(self.filename),urllib.quote_plus(self.stringdata)))
                xbmc.sleep(3000)
                self.filename=xbmcaddon.Addon(id='plugin.video.torrenter').getSetting('lastTorrent')

            if self.stype in ['torrent', 'multitorrent', 'rutracker']:
                try: f = open(self.filename, 'rb')
                except: f = open(urllib.unquote_plus(self.filename), 'rb')
                torrent=f.read()
                f.close
                success=Download().add(torrent, dirname)
            elif self.stype in ['tpb', 'btchat']:
                self.filename=self.filename.split('::')[1]
                success=Download().add_url(self.filename, dirname)
                showMessage(__language__(30211), __language__(30212))
                xbmc.sleep(1500)
                if self.stype=='tpb': xbmcgui.Dialog().ok(unicode(__language__(30269)), unicode(__language__(30270)))


            if success:
                self.filename=self.getfilename()
                id=chooseHASH()
                if id:
                    if self.id: DeleteSource()
                    Download().setprio(id[0], self.ind)
                    stringdata=json.loads(self.stringdata)
                    stringdata['stype']='BLANK'
                    stringdata=json.dumps(stringdata)
                    add=AddSource(stringdata)
                    add.uTorrentAdd(id, self.ind)
            else: showMessage(__language__(30206), __language__(30271))



        else:
            if xbmc.getCondVisibility("system.platform.windows"):
                downloadCmd = "start"
            else:
                downloadCmd = "open"
            os.system(downloadCmd + " " + self.filename)

def chooseHASH():
    dialog_items=[]
    dialog_files=[]
    hash=None
    dat=Download().list()
    for data in dat:
        print str((data['id'], data['dir'].encode('utf-8')))
        dialog_files.append((data['id'], data['dir'].encode('utf-8')))
        dialog_items.append('['+str(data['progress'])+'%] '+data['name'])
    dialog = xbmcgui.Dialog()
    ret = dialog.select(unicode(__language__(30272)), dialog_items)
    if ret>-1 and ret<len(dialog_files): hash=dialog_files[ret]
    return hash

class Serialu(Source):
    def handle(self):
        self.data= Data(cookie_auth, 'http://api.myshows.ru/shows/'+str(self.showId))
        self.jdata = json.loads(self.data.get())
        self.name=self.jdata['ruTitle']
        if not self.name: self.name=self.jdata['title']
        self.stringdata=urllib.quote_plus('{"stype":"serialu", "showId":'+jstr(self.showId)+', "episodeId":'+jstr(self.episodeId)+', "id":'+jstr(self.id)+', "seasonId":'+jstr(self.seasonId)+'}')


    def get(self):
        if self.myback_url:
            user_keyboard = xbmc.Keyboard()
            user_keyboard.setHeading(__language__(30256))
            user_keyboard.setHiddenInput(False)
            user_keyboard.setDefault(self.name)
            user_keyboard.doModal()
            if (user_keyboard.isConfirmed()):
                self.name = user_keyboard.getText().decode('utf-8')
                xbmc.executebuiltin('xbmc.RunPlugin("plugin://plugin.video.serialu.net/?mode=LIST&name='+urllib.quote_plus(self.name.encode('utf-8'))+'&stringdata='+self.stringdata+'")')
        else:
            xbmc.executebuiltin('xbmc.RunPlugin("plugin://plugin.video.serialu.net/?mode=LIST&name='+urllib.quote_plus(self.name.encode('utf-8'))+'&stringdata='+self.stringdata+'")')

    def read(self):
        getfilename=os.path.join(__tmppath__,'serialu_'+str(self.showId)+'.txt')
        self.fg = xbmcvfs.File(getfilename, 'r')
        self.getlist=self.fg.read()
        self.fg.close()
        return re.compile('{(.+?)}').findall(self.getlist)

    def add(self):
        i=0
        getdat=self.read()
        for getdata in getdat:
            getjdata=json.loads('{'+getdata+'}')
            if self.seasonId and self.seasonId!=getjdata['seasonId']: continue
            self.filename=getjdata['filename']
            self.stype='serialu-file'
            self.episodeId=getjdata['episodeId']
            for id in self.jdata['episodes']:
                #if not self.seasonId: self.seasonId=getjdata['seasonId']
                if self.jdata['episodes'][id]['seasonNumber']==getjdata['seasonId'] and self.jdata['episodes'][id]['episodeNumber']==getjdata['episodeId']:
                    self.id=int(id)
                    break
            if not self.getfilename():
                try:
                    TorrentDB().add(urllib.unquote_plus(self.filename), self.stype, self.showId, getjdata['seasonId'], self.id, self.episodeId)
                    i+=1
                except:
                    pass
        if i>1:
            try:TorrentDB().add(urllib.unquote_plus(self.stringdata), 'serialu', self.showId, self.seasonId)
            except: pass
            showMessage(__language__(30208), __language__(30249) % (str(i)))
        elif i==1:
            showMessage(__language__(30208), __language__(30230) % (urllib.unquote_plus(self.filename)))
        return i

class AddSource(Source):
    def handle(self):
        #print 'AddSOURCE self.stype in biginning, biatshes!: '+str(self.stype)
        if not self.stype:
            if self.id:
                myshows_titles=[__language__(30239), __language__(30240), __language__(30241), __language__(30242),__language__(30255), __language__(30273), __language__(30274), __language__(30243)]
                myshows_items=['file', 'vk-file', 'btchat', 'torrent', 'serialu', 'tpb', 'utorrent', None]
            else:
                myshows_titles=[__language__(30244),__language__(30268), __language__(30242), __language__(30245), __language__(30246),__language__(30255), __language__(30274), __language__(30243)]
                myshows_items=['dir', 'rutracker' , 'torrent', 'multifile', 'multitorrent','serialu', 'utorrent', None]
            dialog = xbmcgui.Dialog()
            i = dialog.select(__language__(30235), myshows_titles)
            if i>-1: stype=myshows_items[i]
            if i==-1: return
        else:
            stype=self.stype

        if stype=='file' or stype=='torrent':
            action=xbmcgui.Dialog()
            filename=action.browse(1, __language__(30229), 'video')
            if len(filename)>1:
                if filename.rfind('.torrent', len(filename)-8)==-1 and self.id==None: filename=os.path.dirname(filename)
                self.filename=filename
                self.stype=self.gettype()
                try:
                    self.addsource()
                    showMessage(__language__(30208), __language__(30230) % (filename))
                    AskPlay()
                except: showMessage(__language__(30206), __language__(30231) % (filename))
        elif stype=='multitorrent':
            action=xbmcgui.Dialog()
            filename=action.browse(1, __language__(30247), 'video', '.torrent')
            if filename and filename!='':
                self.filename=filename
                self.addmultijson()
                try:TorrentDB().add(self.filename, 'multitorrent', self.showId, self.seasonId)
                except: pass
        elif stype=='vk-file':
            VKSearch(self.showId, self.id)
        elif stype in ['btchat','tpb','rutracker']:
            TorrenterSearch(stype, self.showId, self.seasonId, self.id, self.episodeId)
        elif stype=='serialu':
            Serialu().get()
        elif stype=='dir' or stype=='multifile':
            self.addstype=stype
            self.DirAdd()
        elif stype=='utorrent':
            self.uTorrentAdd()

    def uTorrentAdd(self, id=None, ind=None):
        if not id: id, self.filename=chooseHASH()
        else: id, self.filename=id

        if len(self.filename)>1:
            if self.id:self.stype='file'
            else: self.stype='multifile'

            if self.stype=='multifile':
                i=self.addmultifile()
                showMessage(__language__(30208), __language__(30249) % (str(i)))
            elif self.stype=='file':
                dllist=sorted(Download().listfiles(id), key=lambda x: x[0])
                dirlist=[x[0] for x in dllist]
                if len(dirlist)>1: cutlist=cutFileNames(dirlist)
                else: cutlist=dirlist
                for s in dirlist:
                    i=dirlist.index(s)
                    cutlist[i]='['+str(dllist[i][1])+'%] '+cutlist[i]
                cutlist.append(unicode(__language__(30205)))
                if not ind and ind!=0:
                    dialog = xbmcgui.Dialog()
                    ret = dialog.select(__language__(30233), cutlist)
                else:
                    for s in dllist:
                        if s[2]==ind: ret=dirlist.index(s[0])
                if ret>-1 and ret<len(cutlist)-1:
                    self.filename=os.path.join(self.filename.decode('utf-8'),dirlist[ret])
                    if len(self.filename)>1:
                        try:
                            self.addsource()
                            showMessage(__language__(30208), __language__(30230) % (self.filename))
                            if dllist[ret][1]==100: AskPlay()
                            else: xbmcgui.Dialog().ok(unicode(__language__(30208)),unicode(__language__(30275))+unicode(dllist[ret][1])+'%.')
                        except: showMessage(__language__(30206), __language__(30231) % (self.filename))

    def DirAdd(self):
        action=xbmcgui.Dialog()
        filename=action.browse(0, __language__(30248), 'video')
        if len(filename)>1:
            self.filename=filename.decode('utf-8')
            if self.addstype=='dir':
                self.stype=self.gettype()
                try:
                    self.addsource()
                    showMessage(__language__(30208), __language__(30230) % (filename))
                except: showMessage(__language__(30206), __language__(30231) % (filename))
            elif self.addstype=='multifile':
                i=self.addmultifile()
                showMessage(__language__(30208), __language__(30249) % (str(i)))

class PlaySource(Source):
    def handle(self):
        if not self.filename:
            if len(TorrentDB().get_all(True, self.showId, self.seasonId))>0:
                ShowAllSources()
            else:
                AddSource()
        else:
            #xbmc.log('PlaySource SI & I'+str(self.showId)+' & '+str(self.id))
            PlayFile()
            #except: showMessage(__language__(30206), __language__(30250) % (self.filename))

class DeleteSource(Source):
    def handle(self):
        TorrentDB().delete(self.filename)
        showMessage(__language__(30208), __language__(30234) % (self.filename))

class ScanSource(Source):
    def handle(self):
        pass

    def scanone(self, silent=None):
        i=0
        self.stype=self.gettype()
        #print 'ScanSource: '+self.filename+' AND STYPE MTFKA '+self.stype
        if self.filename and self.filename!='':
            getdict=TorrentDB().getbyfilename(self.filename)
            self.showId=getdict['showId']
            self.seasonId=getdict['seasonId']
            if self.stype in ('multitorrent', 'torrent'):
                i=self.addmultijson()
            elif self.stype in ('rutracker','tpb'):
                xbmc.executebuiltin('XBMC.RunPlugin(plugin://plugin.video.torrenter/?action=openTorrent&silent=true&external=%s&url=%s&sdata=%s)' % (self.filename.split('::')[0],urllib.quote_plus(self.filename),urllib.quote_plus(self.stringdata)))
                xbmc.sleep(3000)
                self.filename=xbmcaddon.Addon(id='plugin.video.torrenter').getSetting('lastTorrent')
                i=self.addmultijson()
            elif self.stype in ('multifile', 'dir'):
                i=self.addmultifile()
            elif self.stype=='serialu':
                a=Serialu(self.filename)
                a.get()
                i=a.add()
        if not silent:
            xbmc.sleep(1000)
            xbmc.executebuiltin('Container.Refresh')
        else:
            return i

    def add(self):
        ScanDB().add(self.filename)
        showMessage(__language__(30208), __language__(30230) % (self.filename))
        xbmc.executebuiltin('Container.Refresh')

    def delete(self):
        ScanDB().delete(self.filename)
        showMessage(__language__(30208), __language__(30234) % (self.filename))
        xbmc.executebuiltin('Container.Refresh')

def ScanAll():
    i=0
    myscan=ScanDB()
    scanlist=myscan.get_all()
    if len(scanlist)>0:
        for x in scanlist:
            filename=unicode(x['filename'])
            ifstat=myscan.isfilename(filename)
            if ifstat==True:
                i+=ScanSource(stringdata=makeapp({"filename":filename})).scanone(True)
        xbmc.sleep(len(scanlist)*500)
        showMessage(__language__(30263), __language__(30249) % (str(i)))

class DeleteSourses(Source):
    def handle(self):
        if not self.seasonId:
            i=TorrentDB().deleteshow(showId=self.showId, noseasonId=False)
        else:
            i=TorrentDB().deleteseason(showId=self.showId, seasonId=self.seasonId, noid=False)
        showMessage(__language__(30208), __language__(30251) % str(i))

class AskPlay(Source):
    def handle(self):
        xbmc.sleep(1000)
        dialog = xbmcgui.Dialog()
        ok=dialog.yesno(__language__(30227), __language__(30252), self.filename)
        if ok:
            PlayFile()

class PlayFile(Source):
    def handle(self):
        #xbmc.log('LOL THIS IS STYPE IN PLAYFILE:'+str(self.stype))
        if self.stype=='file' or self.stype=='vk-file':
            xbmc.executebuiltin('xbmc.PlayMedia("'+self.filename.encode('utf-8')+'")')
        elif self.stype in ['rutracker', 'tpb','btchat']:
            if self.stype== 'tpb': showMessage(__language__(30211), __language__(30212))
            xbmc.executebuiltin('XBMC.RunPlugin(plugin://plugin.video.torrenter/?action=openTorrent&external=%s&url=%s&sdata=%s)' % (self.filename.split('::')[0],urllib.quote_plus(self.filename),self.stringdata))
        elif self.stype in ['torrent','multitorrent','url-torrent','json']:
            self.play_torrent()
        elif self.stype=='dir' or self.stype=='multifile':
            myshows_files=[unicode(__language__(30232))]
            myshows_files.extend(os.listdir(self.filename))
            myshows_files.append(unicode(__language__(30205)))
            dialog = xbmcgui.Dialog()
            i = dialog.select(__language__(30233), myshows_files)
            if i==myshows_files.index(unicode(__language__(30232))): AddSource()
            if i==myshows_files.index(unicode(__language__(30205))): return False
            filename=os.path.join(self.filename, myshows_files[i])
            if os.path.isdir(filename): PlayFile(makeapp({'filename':filename}))
            else:
                try:filename=filename.encode('utf-8')
                except: pass
                xbmc.executebuiltin('xbmc.PlayMedia("'+filename+'")')
        elif self.stype=='serialu':
            i=0
            getdat=Serialu().read()
            myshows_files=[]
            myshows_items=[]
            for getdata in getdat:
                getjdata=json.loads('{'+getdata+'}')
                if self.seasonId and self.seasonId!=getjdata['seasonId']: continue
                myshows_files.append(getjdata['filename'])
                myshows_items.append(str('S%sE%s' %(str(getjdata['seasonId']),str(getjdata['episodeId']))))
            myshows_files.append(unicode(__language__(30205)))
            myshows_items.append(unicode(__language__(30205)))
            dialog = xbmcgui.Dialog()
            i = dialog.select(__language__(30235), myshows_items)
            if i and i not in (-1, len(myshows_files)-1): xbmc.executebuiltin('xbmc.PlayMedia("'+urllib.unquote_plus(myshows_files[i])+'")')

class ShowAllSources(Source):
    def handle(self):
        myshows_files=[unicode(__language__(30232))]
        myshows_titles=[unicode(__language__(30232))]
        getlist=TorrentDB().get_all(True, self.showId, self.seasonId)
        for k in getlist:
            myshows_files.append(makeapp(k))
            title=''
            if str(k['seasonId'])!='None': title=title+'S'+int_xx(str(k['seasonId']))
            if str(k['episodeId'])!='None': title=title+'E'+int_xx(str(k['episodeId']))
            myshows_titles.append(title+' '+k['filename'].lstrip(os.path.dirname(k['filename'])))
        myshows_files.append(unicode(__language__(30205)))
        myshows_titles.append(unicode(__language__(30205)))
        dialog = xbmcgui.Dialog()
        i = dialog.select(__language__(30235), myshows_titles)
        #xbmc.log(str(i))
        if i==myshows_files.index(unicode(__language__(30232))): AddSource()
        elif i==-1 or i==myshows_files.index(unicode(__language__(30205))): return False
        else: PlayFile(myshows_files[i])

def VKSearch(showId, id):
    data= Data(cookie_auth, 'http://api.myshows.ru/shows/'+str(showId)).get()
    jdata = json.loads(data)

    id=str(id)
    t=jdata['title']
    e=str(jdata['episodes'][id]['episodeNumber'])
    s=str(jdata['episodes'][id]['seasonNumber'])
    a=jdata['episodes'][id]['airDate']
    et=jdata['episodes'][id]['title']
    try:    rt=jdata['ruTitle']
    except: rt=jdata['title']

    dialog_items=[u'%s Сезон %s Серия %s' % (rt, s, e),
                  u'%s %s' % (t, a),
                  u'%s %s.%s' % (t, s, e),
                  u'%s Сезон %s Серия %s' % (t, s, e),
                  u'%s %s Сезон %s Эпизод' % (t, s, e),
                  u'%s Season %s Episode %s' % (t, s, e),
                  u'%s %sx%s' % (t, s, e),
                  u'%s S%sE%s' % (t, int_xx(s), int_xx(e)),
                  u'%s.S%sE%s' % (t.replace(' ', '.'), int_xx(s), int_xx(e)),
                  u'%s %s %s' % (t, a, et),
                  u'%s S%sE%s' % (StripName(t, striplist), int_xx(s), int_xx(e)),
                  u'%s %s' % (StripName(t, striplist), rev_date(a).replace('.', ' ')),
                  unicode(__language__(30205))]

    dialog = xbmcgui.Dialog()
    ret = dialog.select(__language__(30204), dialog_items)
    query=dialog_items[ret].encode('utf-8')
    if ret>-1 and ret<len(dialog_items)-1:
        #print str(ret)
        query=urllib.quote(query)
        xbmc.executebuiltin('xbmc.RunPlugin("plugin://xbmc-vk.svoka.com/?query='+query+'&mode=SEARCH&external=1&stringdata='+urllib.quote_plus('{"stype":"vk-file","showId":'+str(showId)+',"id":'+id+'}')+'&sdata='+str('%s, %s, %s, %s') %(str(showId), s, id, e)+'")')
    return None

class TorrenterSearch():
    def __init__(self, stype, showId, seasonId, id=None, episodeId=None):
        self.stype, self.showId, self.seasonId, self.id, self.episodeId=stype, showId, seasonId, id, episodeId
        self.handle()

    def handle(self):
        data= Data(cookie_auth, 'http://api.myshows.ru/shows/'+str(self.showId)).get()
        jdata = json.loads(data)

        if self.id:
            id=str(self.id)
            e=str(jdata['episodes'][id]['episodeNumber'])
            a=jdata['episodes'][id]['airDate']
            et=jdata['episodes'][id]['title']
        s=str(self.seasonId)
        t=jdata['title']
        stypes={'tpb':'The Pirate Bay','rutracker':'RuTracker.Org', 'btchat':'BT-chat.com'}
        externals={'btchat':'BTchatCom', 'rutracker':'RuTrackerOrg', 'tpb':'ThePirateBaySe'}
        try:    rt=jdata['ruTitle']
        except: rt=jdata['title']


        if self.stype=='rutracker':
            dialog_items=[u'%s Сезон %s' % (rt, s),
                          u'%s Сезон %s 720p' % (rt, s),
                          u'%s %s' % (t, s),
                          u'%s Сезон %s' % (rt, int_xx(s)),
                          u'%s Сезон %s' % (t, int_xx(s)),
                          u'%s S%s' % (StripName(t, striplist), int_xx(s)),
                          unicode(__language__(30205))]
        else:
            dialog_items=[u'%s S%sE%s 720p' % (t, int_xx(s), int_xx(e)),
                          u'%s S%sE%s' % (t, int_xx(s), int_xx(e)),
                          u'%s %sx%s' % (t, s, e),
                          u'%s %s %s' % (t, a, et),
                          u'%s S%sE%s' % (StripName(t, striplist), int_xx(s), int_xx(e)),
                          u'%s %s' % (StripName(t, striplist), StripName(et, striplist)),
                          u'%s %s' % (StripName(t, striplist), rev_date(a).replace('.', ' ')),
                          unicode(__language__(30205))]


        
        dialog = xbmcgui.Dialog()
        ret = dialog.select(__language__(30276) % stypes[self.stype], dialog_items)
        query=dialog_items[ret].encode('utf-8')
        if ret>-1 and ret<len(dialog_items)-1:
            xbmc.executebuiltin('XBMC.ActivateWindow(Videos,plugin://plugin.video.torrenter/?action=search&url=%s&sdata=%s&external=%s)' % (query, urllib.quote_plus(json.dumps('{"stype":%s, "showId":%s, "seasonId":%s, "episodeId":%s, "id":%s}' % (jstr(self.stype), jstr(self.showId), jstr(self.seasonId), jstr(self.episodeId), jstr(self.id)))),externals[self.stype],))
        return

def chooseDir(urls, path=None):
    paths=[unicode(__language__(30254))]
    if not path:
        for url in urls:
            ext = url[:url.rfind('\\')]
            if ext!=url[:len(url)-1] and ext not in paths:
                paths.append(ext)
        return paths
    else:
        files=[]
        for url in urls:
            if path!=paths[0]:
                ext = str(url).replace(path+'\\','')
                if ext and ext!=url:
                    ixt = ext[:ext.rfind('\\')]
                    if ixt==ext[:len(ext)-1]:
                        files.append(url)
            else:
                ext = url[:url.rfind('\\')]
                if ext==url[:len(url)-1]:
                    files.append(url)
        return files

def prefix(showId=None, seasonId=None, id=None, stype=None):
    if not stype:
        if showId:
            getdict=TorrentDB().get(showId=showId, seasonId=seasonId, id=id, noid=True, noseasonId=invert_bool(seasonId))
            try: stype=getdict['stype']
            except: return ''
        else:
            getlist=TorrentDB().get_all(False, showId, seasonId)
            for k in getlist:
                if id and k['id']==id or not id and seasonId and k['seasonId']==seasonId:
                    stype=k['stype']
    stypes=['json', 'vk-file', 'url-file', 'btchat', 'dir', 'file', 'torrent', 'multifile', 'multitorrent','serialu-file','serialu','rutracker','tpb']
    prefixes=['JS', 'VK', 'UF', 'BT', 'D', 'F', 'T', 'MF', 'MT','SF','SU','RU','PB']
    prefix=None
    for i in stypes:
        if stype==i:
            prefix=('[B][%s][/B] ' %(prefixes[stypes.index(i)]))
            break
    if not prefix: prefix=''
    return prefix
