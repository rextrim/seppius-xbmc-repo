# -*- coding: utf-8 -*-

import urllib, re, sys, socket, json, os
import xbmcplugin, xbmcgui, xbmc, xbmcaddon, xbmcvfs

try:
    from hashlib import md5
except ImportError:
    from md5 import md5

from functions import *
from torrents import *
from app import Handler, Link
from rating import *

__version__ = "1.8.3"
__plugin__ = "MyShows.ru " + __version__
__author__ = "DiMartino"
__settings__ = xbmcaddon.Addon(id='plugin.video.myshows')
__language__ = __settings__.getLocalizedString
login=__settings__.getSetting("username")
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
striplist=['the', 'tonight', 'show', 'with', '(2005)', '(2009)', '(2012)', '  ', '  ', '  ', '  ', '  ', '  ', '  ']
Debug('[SYS ARGV]: '+str(urllib.unquote_plus(sys.argv[2]))[1:])

check_login = re.search('='+login+';', cookie_auth)
if not check_login:
    cookie_auth=auth()

class Main(Handler):
    def __init__(self):
        self.menu=[]
        menu_style=__settings__.getSetting("menu_style")
        top=ontop()
        if top: self.menu.append(top)
        if menu_style=='1':
            self.menu.extend([{"title":__language__(30111),"mode":"41"},{"title":__language__(30100),"mode":"10"},
                              {"title":__language__(30102),"mode":"17"},{"title":__language__(30150),"mode":"18"},
                              {"title":__language__(30103),"mode":"14"},{"title":__language__(30104),"mode":"15"},
                              {"title":__language__(30105),"mode":"16"},{"title":__language__(30106),"mode":"27"},
                              {"title":__language__(30107),"mode":"28"}, {"title":__language__(30108),"mode":"100"},
                              {"title":__language__(30112),"mode":"40"}, {"title":__language__(30101),"mode":"19"},
                              {"title":__language__(30149),"mode":"62"},])
        else:
            self.menu.extend([{"title":__language__(30111),"mode":"41"},{"title":__language__(30139),"mode":"13"},
                       {"title":__language__(30106),"mode":"27"},
                       {"title":__language__(30107),"mode":"28"}, {"title":__language__(30108),"mode":"100"},
                       {"title":__language__(30112),"mode":"40"}, {"title":__language__(30136),"mode":"50"},
                       {"title":__language__(30137),"mode":"60"}, {"title":__language__(30101),"mode":"19"},
                       {"title":__language__(30146),"mode":"61"}, {"title":__language__(30141),"mode":"510"}])
        if __settings__.getSetting("debug")=='true':
            self.menu.append({"title":"TEST","mode":"999"})
        self.handle()
        if __settings__.getSetting("autoscan")=='true':
            auto_scan()

    def handle(self):
        for self.i in self.menu:
            try: argv=self.i['argv']
            except: argv={'content': 'videos'}
            self.item(Link(self.i['mode'], argv), title=unicode(self.i['title']))

class ExtraFunction(Main):
    def __init__(self):
        self.menu=[]
        self.menu.extend([{"title":__language__(30136),"mode":"50"},
                          {"title":__language__(30137),"mode":"60"},
                          {"title":__language__(30146),"mode":"61"},
                          {"title":__language__(30141),"mode":"510"},
                          ])
        self.handle()

def Shows(mode):
    try: syncshows=SyncXBMC()
    except: syncshows=False
    saveCheckPoint()
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    #lockView('info')
    if mode==19:
        KB = xbmc.Keyboard()
        KB.setHeading(__language__(30203))
        KB.doModal()
        if (KB.isConfirmed()):
            data= Data(cookie_auth, 'http://api.myshows.ru/shows/search/?q='+urllib.quote_plus(KB.getText()))
    else:
        data=Data(cookie_auth, 'http://api.myshows.ru/profile/shows/')

    jload=data.get()
    if jload:
        jdata = json.loads(jload)
    else: return

    if mode==13:
        menu=[{"title":TextBB(__language__(30100), 'b'),"mode":"10", "argv":{}},
              {"title":TextBB(__language__(30102), 'b'),"mode":"17", "argv":{}},
              {"title":TextBB(__language__(30150), 'b'),"mode":"18", "argv":{}},
              {"title":TextBB(__language__(30103), 'b'),"mode":"14", "argv":{}},
              {"title":TextBB(__language__(30104), 'b'),"mode":"15", "argv":{}},
              {"title":TextBB(__language__(30105), 'b'),"mode":"16", "argv":{}}]

        for i in menu:
            link=Link(i['mode'], i['argv'])
            h=Handler(int(sys.argv[1]), link)
            h.item(link, title=unicode(i['title']))


    for showId in jdata:
        if ruName=='true' and jdata[showId]['ruTitle']:
            title=jdata[showId]['ruTitle']
        else:
            title=jdata[showId]['title']

        if mode!=10 and mode!=19:
            if mode!=18 and jdata[showId]['watchStatus']=="watching" and jdata[showId]['totalEpisodes']-jdata[showId]['watchedEpisodes']==0:
                continue
            elif mode not in (13,17) and jdata[showId]['watchStatus']=="watching" and jdata[showId]['totalEpisodes']-jdata[showId]['watchedEpisodes']!=0:
                continue
            elif mode!=14 and jdata[showId]['watchStatus']=="later":
                continue
            elif mode!=15 and jdata[showId]['watchStatus']=="finished":
                continue
            elif mode!=16 and jdata[showId]['watchStatus']=="cancelled":
                continue

        if mode==19:
            rating=int(jdata[showId]['watching'])
        else:
            rating=float(jdata[showId]['rating'])*2
        pre=prefix(showId=int(showId))

        item = xbmcgui.ListItem(pre+title, iconImage='DefaultFolder.png', thumbnailImage=str(jdata[showId]['image']))
        info={'title': title, 'tvshowtitle': jdata[showId]['title'], 'rating': rating, } #'playcount':jdata[showId]['watchedEpisodes'], 'episode':jdata[showId]['totalEpisodes'] НЕ ХОЧУ ГАЛКИ
        try:
            info['plot']='\r\n'+__language__(30265) % (str(jdata[showId]['watchedEpisodes']), str(jdata[showId]['totalEpisodes']))+'\r\n'+__language__(30266)+' '+str(jdata[showId]['rating'])+'\r\n'
        except:info['plot']=''
        item.setInfo( type='Video', infoLabels=info )
        if syncshows: item=syncshows.shows(jdata[showId]['title'], item, info)
        stringdata={"showId":int(showId), "seasonId":None, "episodeId":None, "id":None}
        refresh_url='&refresh_url='+urllib.quote_plus('http://api.myshows.ru/profile/shows/')
        sys_url = sys.argv[0] + '?stringdata='+makeapp(stringdata)+refresh_url+'&showId=' + str(showId) + '&mode=20'
        item.addContextMenuItems(ContextMenuItems(sys_url, refresh_url), True )
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=True)

def Seasons(showId):
    data= Data(cookie_auth, 'http://api.myshows.ru/shows/'+showId)
    try: syncshows=SyncXBMC()
    except: syncshows=False
    saveCheckPoint()
    seasons, epdict=[], {}
    jdata = json.loads(data.get())
    for id in jdata['episodes']:
        seasonNumber=jdata['episodes'][id]['seasonNumber']
        if seasonNumber not in seasons:
            seasons.append(seasonNumber)
            epdict[str(jdata['episodes'][id]['seasonNumber'])]=str(jdata['episodes'][id]['id'])
        else:
            epdict[str(jdata['episodes'][id]['seasonNumber'])]=epdict[str(jdata['episodes'][id]['seasonNumber'])]+','+str(jdata['episodes'][id]['id'])
    seasons.sort()
    watched_data= Data(cookie_auth, 'http://api.myshows.ru/profile/shows/'+showId+'/')
    try:watched_jdata = json.loads(watched_data.get())
    except: watched_jdata=None
    if watched_jdata: epdict=sortcomma(epdict, watched_jdata)
    for sNumber in seasons:
        pre=prefix(showId=int(showId), seasonId=int(sNumber))
        title=pre+__language__(30138)+' '+str(sNumber)
        stringdata={"showId":int(showId), "seasonId":int(sNumber), "episodeId":None, "id":None}
        sys_url = sys.argv[0] + '?stringdata='+makeapp(stringdata)+'&showId=' + str(showId) + '&seasonNumber=' + str(sNumber) + '&mode=25'
        item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage='')
        if syncshows: item=syncshows.episodes(jdata['title'], item)
        if epdict[str(sNumber)]=='': playcount=1
        else: playcount=0
        item.setInfo( type='Video', infoLabels={'Title': title, 'playcount': playcount} )
        refresh_url='&refresh_url='+urllib.quote_plus(str(watched_data.url))
        item.addContextMenuItems(ContextMenuItems(sys_url, refresh_url), True )
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=True)

def Episodes(showId, seasonNumber):
        #lockView('info')
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        data= Data(cookie_auth, 'http://api.myshows.ru/shows/'+showId)
        watched_data= Data(cookie_auth, 'http://api.myshows.ru/profile/shows/'+showId+'/')
        jdata = json.loads(data.get())
        try: syncshows=SyncXBMC()
        except: syncshows=False
        saveCheckPoint()
        try:watched_jdata = json.loads(watched_data.get())
        except: watched_jdata=[]

        for id in jdata['episodes']:
            if jdata['episodes'][id]['seasonNumber']==int(seasonNumber):
                if id in watched_jdata:
                    playcount=1
                else:
                    playcount=0
                pre=prefix(showId=int(showId),seasonId=jdata['episodes'][id]['seasonNumber'], id=int(id), stype=None, episodeNumber=jdata['episodes'][id]['episodeNumber'])
                if not pre and syncshows.episode(jdata['title'], jdata['episodes'][id]['seasonNumber'], jdata['episodes'][id]['episodeNumber']): pre='[B][XBMC][/B]'
                title=pre+jdata['episodes'][id]['title']+' ['+jdata['episodes'][id]['airDate']+']'
                item = xbmcgui.ListItem('%s. %s' % (str(jdata['episodes'][id]['episodeNumber']), title), iconImage=str(jdata['episodes'][id]['image']), thumbnailImage=str(jdata['episodes'][id]['image']))
                item.setInfo( type='Video', infoLabels={'Title': title,
                                                        'year': jdata['year'],
                                                        'episode': jdata['episodes'][id]['episodeNumber'],
                                                        'season': jdata['episodes'][id]['seasonNumber'],
                                                        'tracknumber': jdata['episodes'][id]['sequenceNumber'],
                                                        'playcount': playcount,
                                                        'tvshowtitle': jdata['title'],
                                                        'premiered': jdata['started'],
                                                        'status': jdata['status'],
                                                        'code': jdata['imdbId'],
                                                        'aired': jdata['episodes'][id]['airDate'],
                                                        'votes': jdata['voted']} )
                if syncshows: item=syncshows.episodes(jdata['title'], item)
                stringdata={"showId":int(showId), "episodeId":jdata['episodes'][id]['episodeNumber'], "id":int(id), "seasonId":jdata['episodes'][id]['seasonNumber']}
                sys_url = sys.argv[0] + '?stringdata='+makeapp(stringdata)+'&seasonNumber='+seasonNumber+'&showId='+showId+'&episodeId='+str(jdata['episodes'][id]['episodeNumber'])+'&id=' + str(id) + '&playcount=' + str(playcount) + '&mode=30'
                refresh_url='&refresh_url='+urllib.quote_plus(str(watched_data.url))
                item.addContextMenuItems(ContextMenuItems(sys_url, refresh_url), True )
                sys_url=sys_url+refresh_url
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=False)

def EpisodeMenu(id, playcount, refresh_url):
    if change_onclick=='true':
        xbmc.executebuiltin("Action(ToggleWatched)")
        Change_Status_Episode(id, playcount, refresh_url)
    else:
        xbmc.executebuiltin("Action(ContextMenu)")

def MyTorrents():
    myt=TorrentDB()
    if  sort!='shows' and showId==None:
        menu=[{"title":TextBB(__language__(30114), 'b'),    "mode":"50",    "argv":{'sort':'shows'}},
              {"title":TextBB(__language__(30287), 'b'),             "mode":"52",   "argv":{}},
              {"title":TextBB(__language__(30140), 'b'),             "mode":"51",   "argv":{}},
              {"title":TextBB(__language__(30141), 'b'), "mode":"510",   "argv":{}}]
        for i in menu:
            link=Link(i['mode'], i['argv'])
            h=Handler(int(sys.argv[1]), link)
            h.item(link, title=unicode(i['title']))

    data=Data(cookie_auth, 'http://api.myshows.ru/profile/shows/').get()
    jdata = json.loads(data)

    if sort=='shows':
        showlist=[]
        listdict=myt.get_all()
        for x in listdict:
            try:
                str_showId=str(x['showId'])
                try:
                    if ruName=='true' and jdata[str_showId]['ruTitle']: show_title=jdata[str_showId]['ruTitle']
                    else: show_title=jdata[str_showId]['title']
                except: show_title=json.loads(Data(cookie_auth, 'http://api.myshows.ru/shows/'+str_showId).get())['title']
                title=show_title
                if str_showId not in showlist:
                    showlist.append(str_showId)
                    item = xbmcgui.ListItem(title+' (%s)'%(str(myt.countshowId(str_showId))), iconImage='DefaultFolder.png', thumbnailImage='')
                    item.setInfo( type='Video', infoLabels={'Title': title } )
                    stringdata={"showId":x['showId'], "seasonId":None, "episodeId":None, "id":None}
                    sys_url = sys.argv[0] + '?stringdata='+makeapp(stringdata)+'&sort=&showId='+str_showId+'&mode=50'
                    item.addContextMenuItems(ContextMenuItems(sys_url, refresh_url), True )
                    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=True)
            except:
                Debug('[MyTorrents] Something went wrong with showId %s' % (str_showId), True)
        xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_TITLE)
    else:
        if showId==None: listdict=myt.get_all()
        else: listdict=myt.get_all(showId=int(showId))

        for x in listdict:
            try:
                str_showId=str(x['showId'])
                str_seasonId=str(x['seasonId'])
                str_episodeId=str(x['episodeId'])
                str_id=str(x['id'])
                str_filename=unicode(x['filename'])
                try:
                    if ruName=='true' and jdata[str_showId]['ruTitle']: show_title=jdata[str_showId]['ruTitle']
                    else: show_title=jdata[str_showId]['title']
                except: show_title=json.loads(Data(cookie_auth, 'http://api.myshows.ru/shows/'+str_showId).get())['title']
                title=''
                if prefix(stype=x['stype']): title=prefix(stype=x['stype'])

                if str_seasonId!='None': title=title+' S'+int_xx(str_seasonId)
                if str_episodeId!='None': title=title+'E'+int_xx(str_episodeId)
                title+=' '+show_title
                item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage='')
                item.setInfo( type='Video', infoLabels={'Title': title } )
                stringdata={"showId":x['showId'], "episodeId":x['episodeId'], "id":x['id'], "seasonId":x['seasonId']}
                sys_url = sys.argv[0] + '?stringdata='+makeapp(stringdata)+'&action='+urllib.quote_plus(str_filename.encode('utf-8'))+'&id='+str_id+'&mode=3020'
                item.addContextMenuItems(ContextMenuItems(sys_url, refresh_url), True )
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=False)
            except:
                Debug('[MyTorrents] Something went wrong with %s' % (str({"showId":x['showId'], "episodeId":x['episodeId'], "id":x['id'], "seasonId":x['seasonId']})), True)

def MyScanList():
    myscan=ScanDB()

    data=Data(cookie_auth, 'http://api.myshows.ru/profile/shows/').get()
    jdata = json.loads(data)


    listdict=myscan.get_all()
    for x in listdict:
        str_showId=str(x['showId'])
        str_seasonId=str(x['seasonId'])
        str_filename=unicode(x['filename'])
        try:
            if ruName=='true' and jdata[str_showId]['ruTitle']: show_title=jdata[str_showId]['ruTitle']
            else: show_title=jdata[str_showId]['title']
        except: show_title=json.loads(Data(cookie_auth, 'http://api.myshows.ru/shows/'+str_showId).get())['title']
        ifstat=myscan.isfilename(str_filename)
        if ifstat: title=TextBB('+', 'b')
        else: title=TextBB('-', 'b')
        if prefix(stype=x['stype']): title+=prefix(stype=x['stype'])
        if str_seasonId!='None': title+=' S'+int_xx(str_seasonId)
        title+=' '+show_title
        item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage='')
        item.setInfo( type='Video', infoLabels={'Title': title } )
        stringdata={"showId":x['showId'], "episodeId":x['episodeId'], "id":x['id'], "seasonId":x['seasonId']}
        sys_url = sys.argv[0] + '?stringdata='+makeapp(stringdata)+'&action='+urllib.quote_plus(str_filename.encode('utf-8'))+'&mode=3020'
        item.addContextMenuItems(ContextMenuItems(sys_url, refresh_url, ifstat), True )
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=False)

def TopShows(action):
    saveCheckPoint()
    if action=='all':
        item = xbmcgui.ListItem(TextBB(__language__(30109), 'b'), iconImage='DefaultFolder.png', thumbnailImage='')
        item.setInfo( type='Video', infoLabels={'Title': 'Male Top'} )
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=str(sys.argv[0] + '?action=male&mode=100'), listitem=item, isFolder=True)
        item = xbmcgui.ListItem(TextBB(__language__(30110), 'b'), iconImage='DefaultFolder.png', thumbnailImage='')
        item.setInfo( type='Video', infoLabels={'Title': 'Female Top'} )
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=str(sys.argv[0] + '?action=female&mode=100'), listitem=item, isFolder=True)

    tdata=Data(cookie_auth, 'http://api.myshows.ru/shows/top/'+action+'/')
    get_data= tdata.get()
    dat=re.compile('{(.+?)}').findall(get_data)
    for data in dat:
        jdata=json.loads('{'+data+'}')
        if ruName=='true' and jdata['ruTitle']:
            title=jdata['ruTitle']
        else:
            title=jdata['title']

        item = xbmcgui.ListItem(str(jdata['place'])+'. '+title+' ('+str(jdata['year'])+')', iconImage='DefaultFolder.png', thumbnailImage=str(jdata['image']))
        item.setInfo( type='Video', infoLabels={'Title': title,
                                                'year': jdata['year'],
                                                'tvshowtitle': jdata['title'],
                                                'status': jdata['status'],
                                                'votes': jdata['voted'],
                                                'rating': float(jdata['rating'])} )

        stringdata={"showId":int(jdata['id']), "seasonId":None, "episodeId":None, "id":None}
        refresh_url='&refresh_url='+urllib.quote_plus('http://api.myshows.ru/profile/shows/')
        sys_url = sys.argv[0] + '?stringdata='+makeapp(stringdata)+'&showId=' + str(jdata['id']) + '&mode=20'
        item.addContextMenuItems(ContextMenuItems(sys_url, refresh_url), True )
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=True)

def EpisodeList(action):
    saveCheckPoint()
    item = xbmcgui.ListItem(' '+__language__(30114), iconImage='DefaultFolder.png', thumbnailImage='')
    item.setInfo( type='Video', infoLabels={'Title': __language__(30114), 'date': today_str()} )
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=str(sys.argv[0] + '?action='+action+'&sort=shows&mode='+str(mode)), listitem=item, isFolder=True)

    show_data= Data(cookie_auth, 'http://api.myshows.ru/profile/shows/')
    data= Data(cookie_auth, 'http://api.myshows.ru/profile/episodes/'+action+'/')
    show_jdata = json.loads(show_data.get())
    jdata = json.loads(data.get())

    for id in jdata:
        str_showId=str(jdata[id]["showId"])
        if ruName=='true' and show_jdata[str_showId]['ruTitle']: show_title=show_jdata[str_showId]['ruTitle']
        else: show_title=show_jdata[str_showId]['title']
        pre=prefix(id=int(id))
        left=dates_diff(str(jdata[id]["airDate"]), 'today')
        title=pre+(__language__(30113) % (int_xx(str(jdata[id]['seasonNumber'])), int_xx(str(jdata[id]['episodeNumber'])), left, show_title, jdata[id]['title']))
        item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage=show_jdata[ str_showId ]['image'] )
        item.setInfo( type='Video', infoLabels={'Title': title,
                                                'episode': jdata[id]['episodeNumber'],
                                                'season': jdata[id]['seasonNumber'],
                                                'date': jdata[id]['airDate'] } )
        stringdata={"showId":int(str_showId), "episodeId":int(jdata[id]['episodeNumber']), "id":int(id), "seasonId":int(jdata[id]['seasonNumber'])}
        sys_url = sys.argv[0] + '?stringdata='+makeapp(stringdata)+'&showId=' + str_showId + '&id='+str(id)+'&seasonNumber=' + str(jdata[id]['seasonNumber']) + '&playcount=0&mode=30'
        refresh_url='&refresh_url='+urllib.quote_plus(str(data.url))
        item.addContextMenuItems(ContextMenuItems(sys_url, refresh_url), True )
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url+refresh_url, listitem=item, isFolder=False)

def ShowList(action):
    show_data= Data(cookie_auth, 'http://api.myshows.ru/profile/shows/')
    data= Data(cookie_auth, 'http://api.myshows.ru/profile/episodes/'+action+'/')
    show_jdata = json.loads(show_data.get())
    jdata = json.loads(data.get())

    num_eps=dict()
    last_date=dict()
    first_date=dict()
    shows=dict()
    images=dict()

    for id in jdata:
        str_showId=str(jdata[id]["showId"])
        str_date=str(jdata[id]["airDate"])
        if ruName=='true' and show_jdata[str_showId]['ruTitle']: show_title=show_jdata[str_showId]['ruTitle']
        else: show_title=show_jdata[str_showId]['title']
        if num_eps.get(str_showId)==None:
            num_eps[str_showId]=1
            shows[str_showId]=show_title.encode('utf-8')
            last_date[str_showId]=str_date
            first_date[str_showId]=str_date
            images[str_showId]=show_jdata[str_showId]['image']
        else: num_eps[str_showId]=int(num_eps[str_showId])+1

        if fdate_bigger_ldate(last_date[str_showId],str_date)==False: last_date[str_showId]=str_date
        elif fdate_bigger_ldate(first_date[str_showId],str_date)==True: first_date[str_showId]=str_date

    for str_showId in num_eps:
        if num_eps[str_showId]==1:
            title=__language__(30115).encode('utf-8') % (last_date[str_showId], shows[str_showId], num_eps[str_showId])
        else:
            title=__language__(30116).encode('utf-8') % (last_date[str_showId], first_date[str_showId], shows[str_showId], num_eps[str_showId])

        item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage=str(images[str_showId]) )
        item.setInfo( type='Video', infoLabels={'Title': shows[str_showId], 'date': str(last_date[str_showId]) } )
        stringdata={"showId":int(str_showId), "seasonId":None, "episodeId":None, "id":None}
        refresh_url='&refresh_url='+urllib.quote_plus(str(show_data.url))
        sys_url = sys.argv[0] + '?stringdata='+makeapp(stringdata)+refresh_url+'&showId=' + str_showId + '&mode=20'
        item.addContextMenuItems(ContextMenuItems(sys_url, refresh_url), True )
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=True)

def FriendsNews():
    data= Data(cookie_auth, 'http://api.myshows.ru/profile/').get()
    jfr, avatars=json.loads(data), {}
    for i in jfr["friends"]:
        avatars[i["login"]]=i["avatar"]+"0"
    get_data= get_url(cookie_auth, 'http://api.myshows.ru/profile/news/')
    jx=json.loads(get_data)
    for u in jx:
        for jdata in jx[u]:
            if jdata['gender']=='m': title_str=__language__(30117)
            else: title_str=__language__(30118)
            if jdata['episodeId']>0:
                title=__language__(30119) % (jdata['login'], title_str, str(jdata['episode']), jdata['show'])
            else:
                title=__language__(30120) % (jdata['login'], title_str, str(jdata['episodes']), jdata['show'])
            try:item = xbmcgui.ListItem(title, iconImage=avatars[jdata["login"]], thumbnailImage=avatars[jdata["login"]])
            except:item = xbmcgui.ListItem(title, iconImage='', thumbnailImage='')
            item.setInfo( type='Video', infoLabels={'Title': title,
                                                    'tvshowtitle': jdata['title'] })
            refresh_url='&refresh_url='+urllib.quote_plus('http://api.myshows.ru/profile/shows/')
            sys_url = sys.argv[0] + '?showId=' + str(jdata['showId'])+'&mode=20'
            item.addContextMenuItems(ContextMenuItems(sys_url, refresh_url), True )
            sys_url=sys.argv[0] + '?action=' + jdata['login'] + '&mode=41'
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=True)

def Profile(action, sort='profile'):
    data= Data(cookie_auth, 'http://api.myshows.ru/profile/'+action).get()
    jdata=json.loads(data)

    if sort!='profile':
        if sort=='friends':
            try:
                friends=jdata['friends']
                for arr in friends:
                    if arr['gender']=='m': title_str=__language__(30121)
                    else: title_str=__language__(30122)
                    days=arr['wastedTime']/24
                    title=__language__(30123) % (arr['login'], title_str, str(days), str(arr['wastedTime']))
                    avatar=arr['avatar']+'0'
                    item = xbmcgui.ListItem(title, iconImage=avatar, thumbnailImage=avatar)
                    item.setInfo( type='Video', infoLabels={'Title': title })
                    sys_url=sys.argv[0] + '?action=' + arr['login'] + '&mode=41&sort=profile'
                    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=True)
            except KeyError: showMessage(__language__(30206), __language__(30222))
        elif sort=='followers':
            try:
                followers=jdata['followers']
                for arr in followers:
                    if arr['gender']=='m': title_str=__language__(30121)
                    else: title_str=__language__(30122)
                    days=arr['wastedTime']/24
                    title=__language__(30123) % (arr['login'], title_str, str(days), str(arr['wastedTime']))
                    avatar=arr['avatar']+'0'
                    item = xbmcgui.ListItem(title, iconImage=avatar, thumbnailImage=avatar)
                    item.setInfo( type='Video', infoLabels={'Title': title })
                    sys_url=sys.argv[0] + '?action=' + arr['login'] + '&mode=41&sort=profile'
                    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=True)
            except KeyError: showMessage(__language__(30206), __language__(30221))
    else:

        if action==login:
            menu=[__language__(30124)+"|:|%s" % (sys.argv[0] + '?mode=41&sort=friends'),
                  __language__(30125)+"|:|%s" % (sys.argv[0] + '?mode=41&sort=followers')]
        else:
            action=unicode(urllib.unquote_plus(action),'utf-8','ignore')
            menu=[__language__(30126) % (action, sys.argv[0] + '?action='+action+'&mode=41&sort=friends'),
                  __language__(30127) % (urllib.unquote_plus(action), sys.argv[0] + '?action='+urllib.unquote_plus(action)+'&mode=41&sort=followers')]
        for temmp in menu:
            sys_url=temmp.encode('utf-8').split('|:|')[1]
            title=temmp.encode('utf-8').split('|:|')[0]

            item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage=str(jdata['avatar']+'0'))
            item.setInfo( type='Video', infoLabels={'Title': title} )
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=True)

        if jdata['gender']=='m':
            stats=[__language__(30128) % (str(jdata['stats']['watchedDays'])),
                   __language__(30129) % (str(jdata['stats']['watchedEpisodes'])),
                   __language__(30130) % (str(jdata['stats']['watchedHours'])),
                   __language__(30131) % (str(jdata['stats']['remainingEpisodes']))]
        else:
            stats=[__language__(30132) % (str(jdata['stats']['watchedDays'])),
                   __language__(30133) % (str(jdata['stats']['watchedEpisodes'])),
                   __language__(30134) % (str(jdata['stats']['watchedHours'])),
                   __language__(30135) % (str(jdata['stats']['remainingEpisodes']))]


        for temmp in stats:
            title=temmp.encode('utf-8')
            item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage=str(jdata['avatar']+'0'))
            item.setInfo( type='Video', infoLabels={'Title': title} )
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='', listitem=item, isFolder=False)

def Change_Status_Episode(id, playcount, refresh_url):
    if str(action)!='None':
        status_url='http://api.myshows.ru/profile/episodes/'+action+'/'+str(id)
    else:
        if playcount=='0': status_url='http://api.myshows.ru/profile/episodes/check/'+str(id)
        else: status_url='http://api.myshows.ru/profile/episodes/uncheck/'+str(id)
    Data(cookie_auth, status_url, refresh_url).get()
    showMessage(__language__(30208), status_url.strip('http://api.myshows.ru/profile/episodes/'), 70)

def Change_Status_Show(showId, action, refresh_url):
    if action=='remove':
        dialog = xbmcgui.Dialog()
        ret=dialog.yesno(__language__(30209), __language__(30210))
    else:
        ret=True
    if ret:
        Data(cookie_auth, 'http://api.myshows.ru/profile/shows/'+showId+'/'+action, refresh_url).get()
        showMessage(__language__(30208), showId+'/'+action)

def Change_Status_Season(showId, seasonNumber, action, refresh_url):
    showMessage(__language__(30211), __language__(30212))
    data= get_url(cookie_auth, 'http://api.myshows.ru/shows/'+showId)
    eps_string=''
    jdata = json.loads(data)
    for id in jdata['episodes']:
        sNum=str(jdata['episodes'][id]['seasonNumber'])
        if seasonNumber==sNum:
            eps_string=eps_string+str(id)+','
    Data(cookie_auth, 'http://api.myshows.ru/profile/shows/'+showId+'/episodes?'+action+'='+eps_string.rstrip(','), refresh_url).get()
    showMessage(__language__(30208), showId+'/episodes?'+action+'='+eps_string)

def Rate(showId, id, refresh_url):
    ratewindow=__settings__.getSetting("ratewindow")
    rate=['5', '4', '3', '2', '1', unicode(__language__(30205))]
    if id=='0':
        rate_item=__language__(30213)+' '+showId
    else:
        rate_item=__language__(30214)+' '+id
    if ratewindow=='true':
        dialog = xbmcgui.Dialog()
        ret = dialog.select(__language__(30215) % rate_item, rate)
    else:
        ret=rateMedia(showId, id, __language__(30215) % rate_item)
        if ret:
            ret=int(ret)-1
    if ret>-1 and ret<5:
        if id=='0':
            rate_url=('http://api.myshows.ru/profile/shows/'+showId+'/rate/'+rate[ret])
        else:
            rate_url=('http://api.myshows.ru/profile/episodes/rate/'+rate[ret]+'/'+id)
        Data(cookie_auth, rate_url, refresh_url).get()
        showMessage(__language__(30208), rate_url.strip('http://api.myshows.ru/profile/'))
        if getSettingAsBool('ratekinopoisk') and id=='0':
                jload=Data(cookie_auth, 'http://api.myshows.ru/shows/'+str(showId)).get()
                if jload:
                    jdata = json.loads(jload)
                    title=jdata['title'].encode('utf-8')
                    year=jdata['year']
                    kinopoiskId=jdata['kinopoiskId']
                    kinorate(title,year,kinopoiskId)
        return True

def Favorite(id, refresh_url):
    dialog = xbmcgui.Dialog()
    items=[__language__(30217), __language__(30218), __language__(30219), __language__(30220), unicode(__language__(30205))]
    actions_fi=['favorites', 'favorites', 'ignored', 'ignored', '']
    actions_ar=['add', 'remove', 'add', 'remove', '']
    ret = dialog.select(__language__(30216) % id, items)
    if ret!=items.index(unicode(__language__(30205))):
        fav_url=actions_fi[ret]+'/'+actions_ar[ret]+'/'+str(id)
        Data(cookie_auth, 'http://api.myshows.ru/profile/episodes/'+fav_url, refresh_url).get()
        showMessage(__language__(30208), fav_url)

def ContextMenuItems(sys_url, refresh_url, ifstat=None):
    myshows_dict=[]
    #Debug('[ContextMenuItems] '+unicode(sys.argv))
    if mode >= 10 and mode <=19 or mode==100 or sort and mode in (27,28):
        menu=[__language__(30227)+'|:|'+sys_url+'4',
              __language__(30300)+'|:|'+sys_url+'0&action=watching'+refresh_url,
              __language__(30301)+'|:|'+sys_url+'0&action=later'+refresh_url,
              __language__(30302)+'|:|'+sys_url+'0&action=cancelled'+refresh_url,
              __language__(30315)+'|:|'+sys_url+'5',
              __language__(30303)+'|:|'+sys_url+'1&id=0',
              __language__(30304)+'|:|'+sys_url+'0&action=remove'+refresh_url]
    elif mode==20:
        menu=[__language__(30227)+'|:|'+sys_url+'4',
              __language__(30311)+'|:|'+sys_url+'9',
              __language__(30305)+'|:|'+sys_url+'0&action=check'+refresh_url,
              __language__(30306)+'|:|'+sys_url+'0&action=uncheck'+refresh_url,
              __language__(30315)+'|:|'+sys_url+'5',
              __language__(30310)+'|:|'+sys_url+'201',
              __language__(30318)+'|:|'+sys_url+'71',
              __language__(30228)+'|:|'+sys_url+'7',
              __language__(30314)+'|:|'+sys_url+'8',]
    elif mode==40:
        menu=[__language__(30300)+'|:|'+sys_url+'0&action=watching'+refresh_url,
              __language__(30301)+'|:|'+sys_url+'0&action=later'+refresh_url,
              __language__(30302)+'|:|'+sys_url+'0&action=cancelled'+refresh_url]
    elif mode==25 or not sort and mode in (27,28):
        menu=[__language__(30227)+'|:|'+sys_url+'4',
              __language__(30305)+'|:|'+sys_url+'0&action=check'+refresh_url,
              __language__(30306)+'|:|'+sys_url+'0&action=uncheck'+refresh_url,
              __language__(30317)+'|:|'+sys_url+'2',
              __language__(30308)+'|:|'+sys_url+'1'+refresh_url,
              __language__(30318)+'|:|'+sys_url+'71',
              __language__(30310)+'|:|'+sys_url+'201',
              __language__(30228)+'|:|'+sys_url+'200',]
    elif mode in (50,) and not sort:
        menu=[__language__(30227)+'|:|'+sys_url,
              __language__(30310)+'|:|'+sys_url+'1',
              __language__(30311)+'|:|'+sys_url+'2',
              __language__(30318)+'|:|'+sys_url+'71',
              __language__(30228)+'|:|'+sys_url+'0']
    elif mode==50 and sort:
        menu=[__language__(30314)+'|:|'+sys_url+'0']
    elif mode in (51,):
        menu=[]
        if ifstat==True: menu.append(__language__(30312)+'|:|'+sys_url+'02')
        elif ifstat==False: menu.append(__language__(30313)+'|:|'+sys_url+'01')
        menu.extend([__language__(30227)+'|:|'+sys_url,
                    __language__(30311)+'|:|'+sys_url+'2',
                    __language__(30318)+'|:|'+sys_url+'71',
                    __language__(30228)+'|:|'+sys_url+'0'])

    for s in menu: myshows_dict.append([s.split('|:|')[0],'XBMC.RunPlugin('+s.split('|:|')[1]+')'])
    return myshows_dict

class SyncXBMC():
    def __init__(self):
        self.menu=self.GetFromXBMC()
        #print self.xbmc_shows
        self.action=action
        self.jloadshows=Data(cookie_auth, 'http://api.myshows.ru/profile/shows/').get()
        if self.jloadshows:
            self.jdatashows = json.loads(self.jloadshows)
        else: return
        if self.action in ['check']:
            self.match=json.loads(title)
            self.doaction()

    def doaction(self):
        if self.action=='check':
            id=None
            showId=None
            if __settings__.getSetting("label")=='true':
                idlist=[]
                if 'label' in self.match and re.search('.*?\.avi|mp4|mkv|flv|mov|vob|wmv|ogm|asx|mpg|mpeg|avc|vp3|fli|flc|m4v$', self.match['label'], re.I | re.DOTALL):
                    self.match['label']=self.match['label'].strip(os.path.dirname(self.match['label'])).encode('utf-8','ignore')
                    Debug('[doaction] Trying to find filename on myshows.ru: '+self.match['label'])
                    data=Data(cookie_auth, 'http://api.myshows.ru/shows/search/file/?q='+urllib.quote_plus(self.match['label'])).get()
                    if data:
                        jdata=json.loads(data)
                        showId=jdata['show']['id']
                        ids=jdata['show']['episodes']
                        for x in ids:
                            idlist.append(x)
                        if len(idlist)==1:
                            id=idlist[0]
                    else:
                        self.match=filename2match(self.match['label'])
                        Debug('[doaction] [filename2match] '+unicode(self.match))
            if self.match and not showId and 'showtitle' in self.match:
                try:showId=self.showtitle2showId(self.match['showtitle'], self.match['tvdb_id'])
                except:showId=self.showtitle2showId(self.match['showtitle'])
            if self.match and 'date' in self.match and not 'episode' in self.match:
                id, self.match['season'],self.match['episode']=date2SE(showId, self.match['date'])
            Debug('[doaction][showId]: '+str(showId)+' [doaction][id]: '+str(id))
            if showId:
                if not id and 'season' in self.match and 'episode' in self.match:
                    Debug('[doaction] Getting the id of S%sE%s' % (str(self.match['season']),str(self.match['episode'])))
                    id=self.getid(showId, self.match['season'],self.match['episode'],self.match['label'])
                if id:
                    rateOK, scrobrate, rateandcheck=False, __settings__.getSetting("scrobrate"), __settings__.getSetting("rateandcheck")
                    if scrobrate=='true':
                        rateOK=Rate(str(showId), str(id), 'http://api.myshows.ru/profile/shows/'+str(showId)+'/')
                    else:rateOK=True
                    if rateOK or rateandcheck=='false':
                        if str(showId) not in self.jdatashows or self.jdatashows[str(showId)]['watchStatus']!='watching':
                            Debug('[doaction] New show! Marking as watching')
                            Change_Status_Show(str(showId), 'watching', 'http://api.myshows.ru/profile/shows/')
                            xbmc.sleep(500)
                        Change_Status_Episode(str(id), '0', 'http://api.myshows.ru/profile/shows/'+str(showId)+'/')

    def showtitle2showId(self, showtitle, tvdb_id=None):
        try:showtitle=showtitle.decode('utf-8','ignore')
        except:pass
        for showId in self.jdatashows:
            if showtitle==self.jdatashows[showId]['ruTitle'] or showtitle==self.jdatashows[showId]['title']:
                return int(showId)
        Debug('[showtitle2showId] '+unicode(showtitle))
        jload=Data(cookie_auth, 'http://api.myshows.ru/shows/search/?q=%s' % urllib.quote_plus(showtitle.encode('utf-8', 'ignore'))).get()
        if jload:
            jdata = json.loads(jload)
            Debug('[showtitle2showId] Search '+unicode(jload))
        else:
            if tvdb_id:
                html=get_html_source("http://thetvdb.com/api/33DBB309BB2B0ADB/series/%s/en.xml" % tvdb_id)
                if re.findall('<SeriesName>(.+?)</SeriesName>', html, re.DOTALL)[0]:
                    showtitle=re.findall('<SeriesName>(.+?)</SeriesName>', html, re.DOTALL)[0]
            Debug('[showtitle2showId] After [tvdb_id] '+showtitle)
            jload=Data(cookie_auth, 'http://api.myshows.ru/shows/search/?q=%s' % urllib.quote_plus(showtitle.encode('utf-8', 'ignore'))).get()
            if jload: jdata = json.loads(jload)
            else: return
        select_show=[]
        showIds=[]
        for showId in jdata:
            select_show.append((jdata[showId]['title'], showId, int(jdata[showId]['watching'])))
            if unicode(showtitle).lower()==unicode(jdata[showId]['ruTitle']).lower() or unicode(showtitle).lower()==unicode(jdata[showId]['title']).lower():
                showIds.append(showId)
                theshowId=showId
        if len(showIds)==1:
            return int(theshowId)
        select_show=sorted(select_show, key=lambda x: x[2], reverse=True)
        showtitles=[]
        showIds=[]
        showId=None
        for x in select_show:
            showtitles.append(x[0])
            showIds.append(x[1])
        if len(showIds)==1:
            showId=int(showIds[0])
        else:
            dialog = xbmcgui.Dialog()
            ret = dialog.select(unicode(__language__(30289)), showtitles)
            if ret!=-1:
                showId=int(showIds[ret])
        if showId:
            return showId

    def getid(self, showId, seasonNumber, episodeId, lable=None):
        data= Data(cookie_auth, 'http://api.myshows.ru/shows/'+str(showId))
        jdata = json.loads(data.get())
        if seasonNumber and int(seasonNumber)>0 and episodeId:
            for id in jdata['episodes']:
                if jdata['episodes'][id]['seasonNumber']==int(seasonNumber) and jdata['episodes'][id]['episodeNumber']==int(episodeId):
                    return int(id)
        episodes=[]
        for id in jdata['episodes']:
            episodes.append((id, jdata['episodes'][id]['title'], jdata['episodes'][id]['seasonNumber']))
            if lable and jdata['episodes'][id]['title']==lable:
                return int(id)
        if len(episodes)==1:
            return int(episodes)
        episodes=sorted(episodes, key=lambda x: x[0], reverse=True)
        eptitles=[]
        ids=[]
        for x in episodes:
            eptitles.append('S'+int_xx(x[2])+' '+x[1])
            ids.append(x[0])
        dialog = xbmcgui.Dialog()
        ret = dialog.select(unicode(__language__(30289)), eptitles)
        if ret!=-1:
            return int(ids[ret])

    def list(self):
        for i in self.menu:
            item = xbmcgui.ListItem(i['title'], iconImage='DefaultFolder.png', thumbnailImage=i['thumbnail'])
            #item.setInfo( type='Video', infoLabels=i )
            #print i
            #item.setProperty('fanart_image', i['fanart'])
            item=self.shows(i['title'],item)
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='', listitem=item, isFolder=True)

    def shows(self, title, item, info=None):
        if not self.menu:
            return item
        for i in range(len(self.menu)):
            if title in self.menu[i]['title']:
                item.setProperty('fanart_image', self.menu[i]['fanart'])

                for studio_info in self.menu[i]['studio']:
                    try: studio+=', '+studio_info
                    except: studio=studio_info
                self.menu[i]['studio']=studio.encode('utf-8')

                for genre_info in self.menu[i]['genre']:
                    try: genre+=', '+genre_info
                    except: genre=genre_info
                self.menu[i]['genre']=genre.encode('utf-8')

                if info:
                    self.menu[i]['title']=info['title']
                    self.menu[i]['playcount']=0
                    self.menu[i]['plot']=info['plot']+self.menu[i]['plot']
                    #self.menu[i]['VideoResolution']=720
                item.setInfo( type='Video', infoLabels=self.menu[i] )
                break
        return item

    def episodes(self, title, item):
        if not self.menu:
            return item
        for i in range(len(self.menu)):
            if title in self.menu[i]['title']:
                #Debug('episodes:'+title+' '+str(self.menu[i]['title']))
                item.setProperty('fanart_image', self.menu[i]['fanart'])
                break
        return item

    def episode(self, title, seasonId, episodeNumber):
        if not self.menu:
            return False
        for i in range(len(self.menu)):
            if title in self.menu[i]['title']:
                for episode in self.menu[i]['episodes']:
                    if episode['episode']==episodeNumber and episode['season']==seasonId:
                        return True
        return False

    def GetFromXBMC(self):
        from utilities import xbmcJsonRequest
        Debug('[Episodes Sync] Getting episodes from XBMC')

        shows = xbmcJsonRequest({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetTVShows', 'params': {'properties': ['title', 'originaltitle', 'genre', 'year', 'rating', 'plot', 'studio', 'mpaa', 'cast', 'imdbnumber', 'premiered', 'votes', 'fanart', 'thumbnail', 'episodeguide', 'playcount', 'season', 'episode', 'tag']}, 'id': 0})

        # sanity check, test for empty result
        if not shows:
            Debug('[Episodes Sync] xbmc json request was empty.')
            return

        # test to see if tvshows key exists in xbmc json request
        if 'tvshows' in shows:
            shows = shows['tvshows']
            #Debug("[Episodes Sync] XBMC JSON Result: '%s'" % str(shows))
        else:
            Debug("[Episodes Sync] Key 'tvshows' not found")
            return

        for show in shows:
            show['episodes'] = []

            episodes = xbmcJsonRequest({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetEpisodes', 'params': {'tvshowid': show['tvshowid'], 'properties': ['season', 'episode', 'playcount', 'uniqueid', 'file']}, 'id': 0})
            if 'episodes' in episodes:
                episodes = episodes['episodes']

                show['episodes'] = [x for x in episodes if type(x) == type(dict())]

        self.xbmc_shows = [x for x in shows if x['episodes']]
        return shows

def Test():
    #SyncXBMC()
    #RunPlugin='{"mode": "60", "argv": {"content": "videos"}}'
    #xbmc.executebuiltin('XBMC.RunPlugin('+sys.argv[0]+'?'+urllib.quote_plus(RunPlugin)+')')
    #print Rate('9237', '2031031', 'http://api.myshows.ru/profile/shows/9237/', True)
    #PluginStatus().use('myshows')
    '''
    import libtorrent
    for filename in xbmcvfs.listdir(r'D:\torrents')[1]:
        filelist=[]
        tor=os.path.join('D:\\','torrents',filename)
        torrentFileInfo = libtorrent.torrent_info(tor)
        s=torrentFileInfo.files()
        for f in s:
            if '\\' not in f.path[f.path.find('\\')+1:]:
                filelist.append(f.path[f.path.find('\\')+1:])
        print 'filelist.append('+str(filelist)+')'
    pass'''
    kinorate('The Job',2001)

params = get_params()
try: apps=get_apps()
except: pass


showId          = None
title           = None
mode            = None
seasonNumber    = None
id              = None
action          = None
playcount       = None
sort            = None
episodeId       = None
refresh_url     = None
stringdata      = None


try:    title = urllib.unquote_plus(params['title'])
except: pass
try:    showId = urllib.unquote_plus(params['showId'])
except: pass
try:    seasonNumber = urllib.unquote_plus(params['seasonNumber'])
except: pass
try:    mode = int(params['mode'])
except: pass
try:    mode = int(apps['mode'])
except: pass
try:    id = urllib.unquote_plus(str(params['id']))
except: pass
try:    episodeId = urllib.unquote_plus(str(params['episodeId']))
except: pass
try:    playcount = str(params['playcount'])
except: pass
try:    action = urllib.unquote_plus(params['action'])
except: pass
try:    sort = str(params['sort'])
except: pass
try:    refresh_url = urllib.unquote_plus(params['refresh_url'])
except: pass
try:    stringdata = urllib.unquote_plus(params['stringdata'])
except: pass

try:    title = urllib.unquote_plus(apps['title'])
except: pass
try:    showId = str(urllib.unquote_plus(apps['argv']['showId']))
except: pass
try:    seasonNumber = str(urllib.unquote_plus(apps['argv']['seasonNumber']))
except: pass
try:    mode = int(apps['mode'])
except: pass
try:    id = urllib.unquote_plus(str(apps['argv']['id']))
except: pass
try:    episodeId = urllib.unquote_plus(str(apps['argv']['episodeId']))
except: pass
try:    playcount = str(apps['argv']['playcount'])
except: pass
try:    action = urllib.unquote_plus(apps['argv']['action'])
except: pass
try:    sort = str(apps['argv']['sort'])
except: pass
try:    refresh_url = urllib.unquote_plus(apps['argv']['refresh_url'])
except: pass
try:    stringdata = urllib.unquote_plus(apps['argv']['stringdata'])
except: pass

if mode == None:
    Main()
elif mode >= 10 and mode <19:
    Shows(mode)
    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_TITLE)
elif mode == 19:
    Shows(mode)
    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING)
elif mode == 20:
    Seasons(showId)
elif mode == 25:
    Episodes(showId, seasonNumber)
    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_EPISODE)
elif mode == 27:
    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_DATE)
    if not sort:
        EpisodeList('unwatched')
    else:
        ShowList('unwatched')
elif mode == 28:
    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_DATE)
    if not sort:
        EpisodeList('next')
    else:
        ShowList('next')
elif mode == 30:
    EpisodeMenu(id, playcount, refresh_url)
elif mode == 40:
    FriendsNews()
elif mode == 41:
    if action==None: action=login
    if sort==None: sort='profile'
    Profile(action, sort)
elif mode == 50:
    MyTorrents()
elif mode == 51:
    MyScanList()
elif mode == 52:
    uTorrentBrowser()
elif mode == 60:
    ClearCache()
elif mode == 61:
    PluginStatus().menu()
elif mode == 62:
    ExtraFunction()
elif mode == 70:
    SyncXBMC()
elif mode in (2571,5171,302071,3071):
    MoveToXBMC()
elif mode == 610:
    PluginStatus().install(action)
elif mode == 611:
    PluginStatus().install_plugin(action)
elif mode == 100:
    if not action: action='all'
    TopShows(action)
elif mode == 200:
    Change_Status_Show(showId, action, refresh_url)
elif mode == 250:
    Change_Status_Season(showId, seasonNumber, action, refresh_url)
elif mode in (251,201,302):
    Rate(showId, id, refresh_url)
elif mode == 300:
    Change_Status_Episode(id, playcount, refresh_url)
elif mode == 3000 or mode == 2500:
    VKSearch(showId, id)
elif mode == 3010:
    Source().addsource()
    jdata=get_apps(stringdata)
    if not sort:AskPlay()
    elif sort=='activate':
        gotoCheckPoint()
        if action=='download':
            DownloadSource()
        elif not jdata['id']:
            ScanSource().scanone()
elif mode == 3011:
    Source().addjson()
elif mode == 3012:
    Serialu().add()
elif mode == 3013:
    gotoCheckPoint()
elif mode == 3020:
    PlayFile()
elif mode == 3090:
    AskPlay()
elif mode == 301 or mode == 252:
    Favorite(id, refresh_url)
elif mode in (500,258):
    DeleteSourses()
elif mode == 510:
    ScanAll()
elif mode in (30202,259):
    ScanSource().scanone()
elif mode == 302001:
    ScanSource().add()
elif mode == 302002:
    ScanSource().delete()
elif mode in (30200,257):
    DeleteSource()
elif mode in (30201,25201):
    DownloadSource(stringdata)
elif mode == 303 or mode==203 or mode==253:
    AddSource()
elif mode == 304 or mode==204 or mode==254:
    PlaySource()
elif mode in (205,255):
    ontop('update', stringdata)
elif mode == 999:
    Test()

xbmcplugin.endOfDirectory(int(sys.argv[1]))