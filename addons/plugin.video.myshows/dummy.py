# -*- coding: utf-8 -*-

import json, sys, urllib, re, os
class TorrentDB:
    def __init__(self):
        self.dbfilename = os.path.join(__addonpath__, 'data.db3')

    def get_all(self, noid=False, showId=None, seasonId=None):
        self._connect()
        if not showId: self.where=''
        else:
            self.where=' where showId='+str(showId)
            if seasonId: self.where+=' and seasonId='+str(seasonId)
            if noid: self.where+=' and id is null'
        self.cur.execute('select filename, stype, showId, seasonId, id, episodeId from sources'+self.where+' order by addtime desc')
        #xbmc.log(str('select filename, stype, showId, seasonId, id, episodeId from sources'+self.where+' order by addtime desc'))
        res = [{'filename': x[0], 'stype': x[1], 'showId': x[2], 'seasonId': x[3], 'id': x[4], 'episodeId': x[5]} for x in self.cur.fetchall()]
        ##xbmc.log(str(res))
        self._close()
        return res

    def get(self, showId, id=None, seasonId=None, noid=False):
        self._connect()
        self.where=' where showId='+str(showId)
        if id: self.where+=' and id='+str(id)
        else: self.where+=' and seasonId='+str(seasonId)
        if not id and noid==True: self.where+=' and id is null'
        self.cur.execute('select filename, stype, showId, seasonId, id, episodeId from sources'+self.where)
        #xbmc.log(str('select filename, stype, showId, seasonId, id, episodeId  from sources'+self.where+' order by addtime desc'))
        try:
            x=self.cur.fetchone()
            res = {'filename': x[0], 'stype': x[1], 'showId': x[2], 'seasonId': x[3], 'id': x[4], 'episodeId': x[5]}
            #xbmc.log(str(res))
        except: res=None
        self._close()
        return res

    def getbyfilename(self, filename):
        self._connect()
        self.where=' where filename="'+filename+'"'
        self.cur.execute('select filename, stype, showId, seasonId, id, episodeId from sources'+self.where)
        #xbmc.log(str('select filename, stype, showId, seasonId, id, episodeId  from sources'+self.where+' order by addtime desc'))
        x=self.cur.fetchone()
        res = {'filename': x[0], 'stype': x[1], 'showId': x[2], 'seasonId': x[3], 'id': x[4], 'episodeId': x[5]}
        #xbmc.log(str(res))
        self._close()
        return res

    def add(self, filename, stype, showId, seasonId=None, id=None, episodeId=None):
        self._connect()
        self.cur.execute('insert into sources(addtime, filename, stype, showId, seasonId, id, episodeId) values(?,?,?,?,?,?,?)', (int(time.time()), filename, stype, showId, seasonId, id, episodeId))
        self.db.commit()
        self._close()

    def delete(self, filename):
        self._connect()
        self.cur.execute("delete from sources where filename='"+unicode(filename)+"'")
        self.db.commit()
        self._close()

    def _connect(self):
        self.db = sqlite.connect(self.dbfilename)
        self.cur = self.db.cursor()

    def _close(self):
        self.cur.close()
        self.db.close()
try:
    from sqlite3 import dbapi2 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite

__addonpath__=r'C:\Users\Админ\AppData\Roaming\XBMC\addons\plugin.video.myshows'

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

filenames=['D:\seriez\Suzumiya Haruhi no Yuuutsu S1 720р',u'D:\seriez\The.Newsroom.S01.720p.HDTVRip.2xRus.Eng.HDCLUB',u'D:\seriez\DoctorWho.Season5.RusSub.HDTV.720p',u'D:\seriez\Twilight_Zone_Season_3',u'D:\seriez\Suits\Season 2']

filename=filenames[0].decode('utf-8')
dirlist=getDirList(filename)
print dirlist
cutlist=cutFileNames(dirlist)
print cutlist

#for fn in cutlist:
    #x=FileNamesPrepare(fn)
    #filename=os.path.join(filename, dirlist[cutlist.index(fn)])
    #stype='file'
    ##episodeId=x[1]

    ##print str(x)

x=TorrentDB().get_all()
#for l in x:
    #print l['filename']