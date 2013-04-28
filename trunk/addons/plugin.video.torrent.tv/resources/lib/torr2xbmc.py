#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib
import urllib
import urllib2
import re
import sys
import os
import socket
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
import xbmcaddon
import datetime
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from TSCore import TSengine as tsengine
import base64
import time
from database import DataBase

hos = int(sys.argv[1])
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
__addon__ = xbmcaddon.Addon( id = 'plugin.video.torrent.tv' )
__language__ = __addon__.getLocalizedString
addon_icon     = __addon__.getAddonInfo('icon')
addon_fanart  = __addon__.getAddonInfo('fanart')
addon_path     = __addon__.getAddonInfo('path')
addon_type     = __addon__.getAddonInfo('type')
addon_id        = __addon__.getAddonInfo('id')
addon_author  = __addon__.getAddonInfo('author')
addon_name     = __addon__.getAddonInfo('name')
addon_version = __addon__.getAddonInfo('version')
prt_file=__addon__.getSetting('port_path')
adult = __addon__.getSetting('adult')
login = __addon__.getSetting("login")
passw = __addon__.getSetting("password")
aceport=62062
cookie = ""
PLUGIN_DATA_PATH = xbmc.translatePath( os.path.join( "special://profile/addon_data", 'plugin.video.torrent.tv') )


if (sys.platform == 'win32') or (sys.platform == 'win64'):
    PLUGIN_DATA_PATH = PLUGIN_DATA_PATH.decode('utf-8')
    
PROGRAM_SOURCE_PATH = os.path.join( PLUGIN_DATA_PATH , "%s_inter-tv.zip"  % datetime.date.today().strftime("%W") )
    
db_name = os.path.join(PLUGIN_DATA_PATH, 'tvbase.db')
cookiefile = os.path.join(PLUGIN_DATA_PATH, 'cookie.txt')
xbmcplugin.setContent(int(sys.argv[1]), 'episodes')

data = urllib.urlencode({
    'email' : login,
    'password' : passw,
    'remember' : 1,
    'enter' : 'enter'
})

############################
if __addon__.getSetting('fanart') == 'false':xbmcplugin.setContent(int(sys.argv[1]), 'movies')
if __addon__.getSetting('fanart') == 'true':xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
############################

try:
    if prt_file:  
        gf = open(prt_file, 'r')
        aceport=int(gf.read())
        gf.close()
except: prt_file=None
if not prt_file:
    try:
        fpath= os.path.expanduser("~")
        pfile= os.path.join(fpath,'AppData\Roaming\TorrentStream\engine' ,'acestream.port')
        gf = open(pfile, 'r')
        aceport=int(gf.read())
        gf.close()
        __addon__.setSetting('port_path',pfile)
        print aceport
    except: aceport=62062

def construct_request(params):
    return '%s?%s' % (sys.argv[0], urllib.urlencode(params))
 
def GET(target, post=None):
    try:
        req = urllib2.Request(url = target, data = post)
        req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
        global cookie
        if cookie != "":
            req.add_header('Cookie', cookie)
            
        if cookie == "":
            if os.path.exists(cookiefile):
                fgetcook = open(cookiefile, 'r')
                cookie = fgetcook.read()
                del fgetcook
                try:
                    req.add_header('Cookie', cookie)
                    resp = urllib2.urlopen(req)
                    http = resp.read()
                    if not http.find('Вход') > 1:
                        return http
                    else:
                        cookie = UpdCookie()
                        req.add_header('Cookie', cookie)
                        resp = urllib2.urlopen(req)
                        http = resp.read()
                        if not http.find('Вход') > 1:
                            return http
                        else:
                            showMessage('Raketa TV', 'ОШИБКА авторизации', 3000)
                            return http
                    resp.close()
                except:
                    cookie = UpdCookie()
                    req.add_header('Cookie', cookie)
            else:
                cookie = UpdCookie()
                req.add_header('Cookie', cookie)
        resp = urllib2.urlopen(req)
        http = resp.read()
        resp.close()
        return http
    except Exception, e:
        xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
        showMessage('HTTP ERROR', e, 5000)
        
def showMessage(message = '', heading='TorrentTV', times = 3000, pics = addon_icon):
    try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
    except Exception, e:
        xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
        except Exception, e:
            xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )

def GetCookie(target, post=None):
    try:
        req = urllib2.Request(url = target, data = post)
        req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
        resp = urllib2.urlopen(req)
        cookie = resp.headers['Set-Cookie'].split(";")[0]
        http=resp.read()
        if not http.find('Вход') > 1:
            showMessage('Torrent TV', 'Успешная авторизация', 3000)
            return cookie
        else: showMessage('Raketa TV', 'ОШИБКА авторизации', 3000)
    except Exception, e:
        xbmc.log( '[%s]: GET COOKIE EXCEPT [%s]' % (addon_id, e), 4 )
        showMessage('HTTP ERROR: '+str(target), e, 5000)

def UpdCookie():
    if not os.path.exists(PLUGIN_DATA_PATH):
        os.makedirs(PLUGIN_DATA_PATH)
    if os.path.exists(cookiefile):
        os.remove(cookiefile)
    out = open(cookiefile, 'w')
    cookie = ''
    if GetCookie('http://torrent-tv.ru/auth.php', data) == None:
        if GetCookie('http://1ttv.org/auth.php', data) == None:
            return None
        else:
            cookie = GetCookie('http://1ttv.org/auth.php', data)
    else:
        cookie = GetCookie('http://torrent-tv.ru/auth.php', data)
    try:
        out.write(cookie)
        out.close()
        return cookie
    except:
        showMessage('Torrent TV', 'Ошибка подключения')
        return None        

def GetScript(params):
    import time
    xbmc.executebuiltin( "ActivateWindow(%d)" % ( 10147 ) )
    window = xbmcgui.Window( 10147 )


########################
    try:
        import YaTv
        ncl=dx[params['title']]
        #print ncl
        txtProgram=YaTv.GetPrDay(ncl)
        print txtProgram
    except: 
        txtProgram='Нет программы'
#########################
        
        xbmc.sleep(13)
        window.getControl(1).setLabel(ch['name'])
        window.getControl(5).setText(txtProgram)
    
#####################################

dx={
"1+1": "620",
"2+2": "583",
"24 Док": "16",
"24 Техно": "710",
"2x2": "323",
"365 Дней": "250",
"5 канал (Украина)": "586",
"8 канал": "217",
"Amazing Life": "658",
"Animal Planet": "365",
"Animal Planet HD": "990",
"A-One": "680",
"A-ONE UA": "680",
"AXN Sci-Fi": "516",
"SONY Sci-Fi": "516",
"BBC World News": "828",
"Bridge TV": "151",
"Cartoon Network": "601",
"CBS Drama": "911",
"CBS Reality": "912",
"Comedy TV": "51",
"Da Vinci Learning": "410",
"DIVA Universal Russia": "713",
"Dobro TV": "937",
"Discovery Channel": "325",
"Discovery Science": "409",
"Discovery World": "437",
"Investigation Discovery Europe": "19",
"Discovery HD Showcase": "111",
"Discowery HD Showcase": "111",
"Discovery Showcase HD": "111",
"Disney Channel": "150",
"English Club TV": "757",
"Enter Film": "281",
"EuroNews": "23",
"Europa Plus TV": "681",
"Eurosport": "737",
"Eurosport 2": "850",
"Eurosport 2 HD": "850",
"Eurosport HD": "560",
"Extreme Sports": "288",
"Fashion TV": "661",
"Fashion TV HD": "121",
"Fashion HD": "121",
"Fashion One HD": "919",
"Fashion One": "919",
"Fox": "659",
"FOX HD": "659",
"Fox HD": "659",
"Fox Life": "615",
"FOX life HD": "464",
"France 24": "187",
"France24": "187",
"Galaxy TV": "924",
"Gulli": "810",
"HD Life": "415",
"HD Спорт": "429",
"ICTV": "709",
"JimJam": "494",
"Kids co": "598",
"Maxxi-TV": "228",
"MCM Top": "533",
"MGM": "608",
"MGM HD": "934",
"Mezzo": "575",
"Motor TV": "531",
"Motors TV": "531",
"Motors Tv": "531",
"MTV Dance": "332",
"MTV Hits UK": "849",
"MTV Rocks": "388",
"MTV Russia": "430",
"MTV Ukraina": "430",
"MTV live HD": "382",
"MTV Live HD": "382",
"Music Box UA": "25",
"Music Box": "642",
"Russian Music Box": "25",
"myZen.tv HD": "141",
"Nat Geo Wild": "807",
"Nat Geo Wild HD": "807",
"National Geographic": "102",
"National Geographic HD": "389",
"News One": "247",
"Nick Jr.": "917",
"Nickelodeon": "567",
"Nickelodeon HD": "423",
"Ocean-TV": "55",
"O-TV": "167",
"Outdoor HD": "322",
"Paramount Comedy": "920",
"QTV": "280",
"RTVi": "76",
"RU TV": "258",
"Rusong TV": "591",
"Russian Travel Guide": "648",
"SET": "311",
"SET HD": "311",
"S.E.T": "311",
"Sony Turbo": "935",
"Smile of Child": "789",
"STV": "165",
"Style TV": "119",
"Style tv": "119",
"TiJi": "555",
"TLC": "425",
"Tonis": "627",
"TVCI": "435",
"TV 1000": "127",
"TV 1000 Action East": "125",
"TV 1000 Русское кино": "267",
"TV XXI (TV21)": "309",
"Ukrainian Fashion": "939",
"Universal Channel": "213",
"VH1": "491",
"VH1 Classic": "156",
"Viasat Explorer": "521",
"Viasat History": "277",
"Viasat Nature East": "765",
"Viasat Sport": "455",
"World Fashion": "346",
"Zee TV": "626",
"Авто плюс": "153",
"Агро тв": "11",
"Амедиа": "918",
"Астро ТВ": "249",
"Астро": "249",
"Беларусь 24": "851",
"Боец": "454",
"Бойцовский клуб": "986",
"Вопросы и ответы": "333",
"Время": "669",
"Детский": "66",
"Детский мир": "747",
"Дождь": "384",
"Дождь HD": "384",
"Дом кино": "Дом кино",
"Домашние животные": "520",
"Домашний": "304",
"Драйв ТВ": "505",
"Еврокино": "352",
"ЕДА": "931",
"ЕДА HD": "930",
"Живи": "113",
"Звезда": "405",
"Закон ТВ": "178",
"Закон тв": "178",
"Закон-тв": "178",
"Закон ТВ": "178",
"Загородный": "705",
"Загородная жизнь": "21",
"Знание": "201",
"Здоровое ТВ": "595",
"Зоо ТВ": "273",
"Зоопарк": "367",
"Иллюзион+": "123",
"Индия": "798",
"Интер": "677",
"Интер+": "808",
"Интересное ТВ": "24",
"К1": "453",
"Карусель": "740",
"Кинопоказ": "22",
"Комедия ТВ": "821",
"Кто есть кто": "769",
"Кухня ТВ": "614",
"КХЛ ТВ": "481",
"КХЛ HD": "481",
"Ля-минор": "257",
"М1": "632",
"Мега": "788",
"Мир": "726",
"Мир сериала": "145",
"Много ТВ": "799",
"Моя планета": "675",
"Москва 24": "334",
"Москва Доверие": "655",
"Москва доверие": "655",
"Музыка Первого": "715",
"Мужской": "82",
"Мать и дитя": "618",
"Мать и Дитя": "618",
"Мультимания": "31",
"Нано ТВ": "35",
"Наука 2.0": "723",
"Наше любимое кино": "477",
"Новый канал": "128",
"Ностальгия": "783",
"НСТ": "518",
"НТВ": "162",
"НТВ Мир": "422",
"НТВ+ Кино плюс": "644",
"НТВ+ Киноклуб": "462",
"НТВ+ Кинолюкс": "8",
"НТВ+ Киносоюз": "71",
"НТВ+ Кинохит": "542",
"НТВ+ Наше кино": "12",
"НТВ+ Наше новое кино": "485",
"НТВ+ Премьера": "566",
"НТВ+ Баскетбол": "697",
"НТВ+ Наш футбол": "499",
"НТВ+ Спорт": "134",
"НТВ+ Спорт Онлайн": "183",
"НТВ+ Спорт Союз": "306",
"НТВ+ Спорт плюс": "377",
"НТВ+ Теннис": "358",
"НТВ+ Футбол": "664",
"НТВ+ Футбол 2": "563",
"НТВ+ Футбол HD": "664",
"НТВ+ Футбол 2 HD": "563",
"НТН (Украина)": "140",
"О2ТВ": "777",
"О2 ТВ": "777",
"Оружие": "376",
"ОСТ": "926",
"Охота и рыбалка": "617",
"Охотник и рыболов": "132",
"Парк развлечений": "37",
"Первый автомобильный (укр)": "507",
"Первый деловой": "85",
"Первый канал": "146",
"Первый канал (Европа)": "391",
"Первый канал (СНГ)": "391",
"Первый канал HD": "983",
"Первый национальный (Украина)": "773",
"Первый образовательный": "774",
"Перец": "511",
"Пиксель ТВ": "940",
"Подмосковье": "161",
"Про все": "458",
"Просвещение": "685",
"Психология 21": "434",
"Пятый канал": "427",
"Раз ТВ": "363",
"РАЗ ТВ": "363",
"РБК": "743",
"РЕН ТВ": "689",
"РЖД": "509",
"Ретро ТВ": "6",
"Россия 1": "711",
"Россия 2": "515",
"Россия 24": "291",
"Россия К": "187",
"РОССИЯ HD": "984",
"Россия HD": "984",
"РТР-Планета": "143",
"Русский Бестселлер": "994",
"Русский иллюзион": "53",
"Русский роман": "401",
"Русский экстрим": "406",
"Сарафан ТВ": "663",
"Сарафан": "663",
"Спас": "447",
"Спас ТВ": "447",
"Спорт 1": "181",
"Спорт 1 HD": "554",
"Совершенно секретно": "275",
"Союз": "349",
"СТБ": "670",
"СТС": "166",
"Страна": "284",
"ТБН": "576",
"ТДК": "776",
"ТВ 3": "698",
"TBi": "650",
"ТВЦ": "649",
"ТНТ": "353",
"Тонус ТВ": "637",
"Тонус-ТВ": "637",
"Телекафе": "173",
"Телепутешествия": "794",
"Телепутешествия HD": "331",
"ТЕТ": "479",
"ТРК Украина": "326",
"ТРО Союза": "730",
"ТРО": "730",
"Успех": "547",
"Усадьба": "779",
"Феникс+ Кино": "686",
"Футбол": "328",
"Футбол (украина)": "666",
"Футбол+ (украина)": "753",
"Хокей": "702",
"ЧП-Инфо": "315",
"Шансон ТВ": "662",
"Ю": "898",
"Юмор ТВ": "412",
"Юмор тв": "412",
"Юмор BOX": "412",
"Эгоист ТВ": "431"
}

#####################################       
def GetChannelsDB (params):
#########################
    try:
        import YaTv
    except: pass
#########################
    db = DataBase(db_name, cookie)
    channels = None
    if not params.has_key('group'):
        return
    elif params['group'] == '0':
        channels = db.GetChannels(adult = adult)
    elif params['group'] == 'hd':
        channels = db.GetChannelsHD(adult = adult)
    elif params['group'] == 'latest':
        channels = db.GetLatestChannels(adult = adult)
    elif params['group'] == 'new':
        channels = db.GetNewChannels(adult = adult)
    elif params['group'] == 'favourite':
        channels = db.GetFavouriteChannels(adult = adult)
    else:
        channels = db.GetChannels(params['group'], adult = adult)
    import time
    for ch in channels:
        img = ch['imgurl']
        if __addon__.getSetting('logopack') == 'true':
            logo_path = os.path.join(PLUGIN_DATA_PATH, 'logo')
            logo_src = os.path.join(logo_path, ch['name'].decode('utf-8') + '.png')
            if os.path.exists(logo_src):
                img = logo_src
        title = ch['name']
        if params['group'] == '0' or params['group'] == 'hd' or params['group'] == 'latest' or params['group'] == 'new':
            title = '[COLOR FF7092BE]%s:[/COLOR] %s' % (ch['group_name'], title)
 ###################################
        try:
            ni=dx[ch['name']]
            d=YaTv.GetPr(id2=ni)
        except:ni=ch['name']
        try:prog = d[ni]["plot"]
        except:prog =""
        try:
            tbn=d[ni]["img"]
            if tbn == '': tbn = img
        except:tbn = img
        try:genre = d[ni]["genre"]
        except:genre = ch['group_name']
        title =title +chr(10)+prog[:prog.find("[COLOR FF999999]")]
        prog =chr(10)+prog
        prog1 = str(prog[:prog.find("[COLOR FF999999]")]).strip()
        if prog1 == "":
            prog1 = title
        if __addon__.getSetting('fanart') == 'false':
            if __addon__.getSetting('disable') == 'false':
                li = xbmcgui.ListItem("[COLOR FFB77D00]" + title + "[/COLOR]", title, img, img)
                try:li.setProperty('fanart_image', tbn.encode('utf-8'))
                except:li.setProperty('fanart_image', tbn.encode('utf-8'))
            else:
                li = xbmcgui.ListItem("[COLOR FFB77D00]" + title + "[/COLOR]", title, img, img)
                li.setProperty('fanart_image', img)
        else:
            if __addon__.getSetting('disable') == 'false':
                try:li = xbmcgui.ListItem("[COLOR FFB77D00]" + title + "[/COLOR]", title, img, tbn.encode('utf-8'))
                except:li = xbmcgui.ListItem("[COLOR FFB77D00]" + title + "[/COLOR]", title, img, img)
            else:
                li = xbmcgui.ListItem("[COLOR FFB77D00]" + title + "[/COLOR]", title, img, img)
        startTime = time.localtime()#float(item['start'])
        endTime = time.localtime()#item['end']
        li.setInfo(type = "Video", infoLabels = {"Title": ch['name'], 'year': endTime.tm_year, 'genre': genre, 'plot': prog} )
 ###################################           
        uri = construct_request({
            'func': 'play_ch_db',
            'img': img.encode('utf-8'),
            'title': prog1,
            'file': ch['urlstream'],
            'id': ch['id']
        })
        deluri = construct_request({
            'func': 'DelChannel',
            'id': ch['id']
        })
        favouriteuri = construct_request({
            'func': 'FavouriteChannel',
            'id': ch['id']
        })
        delfavouriteuri = construct_request({
            'func': 'DelFavouriteChannel',
            'id': ch['id']
        })
        commands = []
        #commands.append(('Телепрограмма', 'XBMC.RunPlugin(%s?func=GetScript&id=%s&title=%s)' % (sys.argv[0], ch['id'], ch['name']),))
        if params['group'] != 'favourite':
            commands.append(('[COLOR FF669933]Добавить[/COLOR][COLOR FFB77D00] в "ИЗБРАННЫЕ"[/COLOR]', 'XBMC.RunPlugin(%s)' % (favouriteuri),))
        commands.append(('[COLOR FFCC3333]Удалить[/COLOR][COLOR FFB77D00] из "ИЗБРАННЫЕ"[/COLOR]', 'XBMC.RunPlugin(%s)' % (delfavouriteuri),))
        commands.append(('Удалить канал', 'XBMC.RunPlugin(%s)' % (deluri),))
        li.addContextMenuItems(commands, True)
        xbmcplugin.addDirectoryItem(hos, uri, li)
    xbmcplugin.endOfDirectory(hos)
    del db
    
def DelChannel(params):
    db = DataBase(db_name, cookie)
    db.DelChannel(params['id'])
    showMessage(message = 'Канал удален')
    xbmc.executebuiltin("Container.Refresh")
    del db

def FavouriteChannel(params):
    db = DataBase(db_name, cookie)
    db.FavouriteChannel(params['id'])
    showMessage(message = 'Канал добавлен')
    xbmc.executebuiltin("Container.Refresh")
    del db
    
def DelFavouriteChannel(params):
    db = DataBase(db_name, cookie)
    db.DelFavouriteChannel(params['id'])
    showMessage(message = 'Канал удален')
    xbmc.executebuiltin("Container.Refresh")
    del db
    
def GetChannelsWeb(params):
#########################
    try:
        import YaTv
    except: pass
#########################
    http = GET('http://torrent-tv.ru/' + params['file'])
    if http == None:
        http = GET('http://1ttv.org/' + params['file'])
        if http == None:
            showMessage('Torrent TV', 'Сайты не отвечают')
            return
    beautifulSoup = BeautifulSoup(http)
    channels=beautifulSoup.findAll('div', attrs={'class': 'best-channels-content'})
    for ch in channels:
        link =ch.find('a')['href']
        title= ch.find('strong').string.encode('utf-8').replace('\n', '')
        img='http://torrent-tv.ru/'+ch.find('img')['src']
        if __addon__.getSetting('logopack'):
            logo_path = os.path.join(PLUGIN_DATA_PATH, 'logo')
            logo_src = os.path.join(logo_path, ch.find('strong').string.replace('\n', '').replace('  ', '') + '.png')
            if os.path.exists(logo_src):
                img = logo_src
 ###################################
        try:
            ni=dx[title.strip()]
            d=YaTv.GetPr(id2=ni)
        except:ni=title.strip()
        try:prog = d[ni]["plot"]
        except:prog =""
        try:
            tbn=d[ni]["img"]
            if tbn == '': tbn = img
        except:tbn = img
        try:genre = d[ni]["genre"]
        except:genre = ''
        title =title +chr(10)+prog[:prog.find("[COLOR FF999999]")]
        prog =chr(10)+prog
        prog1 = str(prog[:prog.find("[COLOR FF999999]")]).strip()
        if prog1 == "":
            prog1 = title
        if __addon__.getSetting('fanart') == 'false':
            if __addon__.getSetting('disable') == 'false':
                li = xbmcgui.ListItem("[COLOR FFB77D00]" + title + "[/COLOR]", title, img, img)
                try:li.setProperty('fanart_image', tbn.encode('utf-8'))
                except:li.setProperty('fanart_image', tbn.encode('utf-8'))
            else:
                li = xbmcgui.ListItem("[COLOR FFB77D00]" + title + "[/COLOR]", title, img, img)
                li.setProperty('fanart_image', img)
        else:
            if __addon__.getSetting('disable') == 'false':
                try:li = xbmcgui.ListItem("[COLOR FFB77D00]" + title + "[/COLOR]", title, img, tbn.encode('utf-8'))
                except:li = xbmcgui.ListItem("[COLOR FFB77D00]" + title + "[/COLOR]", title, img, img)
            else:
                li = xbmcgui.ListItem("[COLOR FFB77D00]" + title + "[/COLOR]", title, img, img)
        startTime = time.localtime()#float(item['start'])
        endTime = time.localtime()#item['end']
        li.setInfo(type = "Video", infoLabels = {"Title": title, 'year': endTime.tm_year, 'genre': genre, 'plot': prog} )
 ###################################           

                
        uri = construct_request({
                'func': 'play_ch_web',
                'img':img.encode('utf-8'),
                'title':prog1,
                'file':link
        })
        commands = []
        li.addContextMenuItems(commands, True)
        xbmcplugin.addDirectoryItem(hos, uri, li)
    xbmcplugin.endOfDirectory(hos)

def play_ch_db(params):
    url = ''
    if params['file'] == '':
        db = DataBase(db_name, cookie)
        url = db.GetUrlsStream(params['id'])
        if url.__len__() == 0:
            showMessage('Ошибка получения ссылки')
            return
    else:
        url = params['file']
    if url != '':
        TSPlayer = tsengine()
        out = None
        if url.find('http://') == -1:
            out = TSPlayer.load_torrent(url,'PID',port=aceport)
        else:
            out = TSPlayer.load_torrent(url,'TORRENT',port=aceport)
        if out == 'Ok':
            TSPlayer.play_url_ind(0,params['title'],addon_icon,params['img'])
            db = DataBase(db_name, cookie)
            db.IncChannel(params['id'])
            del db
            TSPlayer.end()
            xbmc.executebuiltin('Container.Refresh')
            showMessage('Torrent', 'Stop')
            return
        else:
            #TSPlayer.end()
            #url = ''
            #if params['file'] == '':
            db = DataBase(db_name, cookie)
            showMessage('Torrent', 'Обновление торрент-ссылки')
            url = db.UpdateUrlsStream([params['id']])
            #newlink = UpdateChannelsDB(params['id'])
            #print 'newlink---'+str(newlink)
            #pos = xbmc.getInfoLabel('Container.Position')
            #print 'pos---'+str(pos)
            xbmc.executebuiltin('Container.Refresh')
            return
            #xbmcgui.ListItem.
            #print 'UpdateChannelsDB----' + str(url[0]['urlstream'])
            #if url.__len__() == 0:
                #showMessage('Ошибка получения ссылки')
                #return
            url = url[0]['urlstream']
            #print 'url---'+str(url)
                #del db
            #else:
                #url = params['file']
                #showMessage('Torrent', 'Обновление торрент-ссылки')
                #time.sleep(20)
            if url != '':
                #TSPlayer = tsengine()
                out = None
                if url.find('http://') == -1:
                    print 'TS PID---'+str(url)
                    out = TSPlayer.load_torrent(url,'PID',port=aceport)
                    print 'OUT PID---'+str(out)
                else:
                    print 'TS TORRENT'
                    out = TSPlayer.load_torrent(url,'TORRENT',port=aceport)
                if out == 'Ok':
                    print 'TS OK'
                    TSPlayer.play_url_ind(0,params['title'],addon_icon,params['img'])
                    db = DataBase(db_name, cookie)
                    db.IncChannel(params['id'])
                    del db
                    TSPlayer.end()
                    showMessage('Torrent', 'Stop')
                    return
  
def play_ch_web(params):
    http = GET('http://torrent-tv.ru/' + params['file'])
    if http == None:
        http = GET('http://1ttv.org/' + params['file'])
        if http == None:
            showMessage('Torrent TV', 'Сайты не отвечают')
            return
    beautifulSoup = BeautifulSoup(http)
    tget= beautifulSoup.find('div', attrs={'class':'tv-player'})
    
    m=re.search('http:(.+)"', str(tget))
    if m:
        torr_link= m.group(0).split('"')[0]
        m=re.search('http://[0-9]+.[0-9]+.[0-9]+.[0-9]+:[0-9]+', torr_link)
        TSplayer=tsengine()
        out=TSplayer.load_torrent(torr_link,'TORRENT',port=aceport)
        if out=='Ok':
            TSplayer.play_url_ind(0,params['title'],addon_icon,params['img'])
        TSplayer.end()
        showMessage(message = 'Stop')
    else:
        m = re.search('load.*', str(tget))
        ID = m.group(0).split('"')[1]
        try:
            TSplayer=tsengine()
            out=TSplayer.load_torrent(ID,'PID',port=aceport)
            if out=='Ok':
                TSplayer.play_url_ind(0,params['title'],addon_icon,params['img'])
            TSplayer.end()
        except Exception, e:
            showMessage(message = e)
        xbmc.executebuiltin('Container.Refresh')
        showMessage(message = 'Stop')

def GetParts():
    db = DataBase(db_name, cookie)
    parts = db.GetParts(adult = adult)
    refreshuri = construct_request({
        'func': 'Refreshuri'
    })    
    commands = []
    commands.append(('Обновить список каналов', 'XBMC.RunPlugin(%s)' % (refreshuri),))
    for part in parts:
        li = xbmcgui.ListItem(part['name'])
        li.addContextMenuItems(commands, True)
        uri = construct_request({
            'func': 'GetChannelsDB',
            'group': part['id'],
        })
        xbmcplugin.addDirectoryItem(hos, uri, li, True)

def Refreshuri(params):
    cookie = UpdCookie()
    db = DataBase(db_name, cookie)
    showMessage('Torrent TV', 'Производится обновление плейлиста')
    db.UpdateDB()
    xbmc.executebuiltin('Container.Refresh')
    showMessage('Torrent TV', 'Обновление плейлиста завершено')

def mainScreen(params):
    refreshuri = construct_request({
        'func': 'Refreshuri'
    })    
    commands = []
    commands.append(('Обновить список каналов', 'XBMC.RunPlugin(%s)' % (refreshuri),))
    li = xbmcgui.ListItem('[COLOR FFB77D00]ИЗБРАННЫЕ[/COLOR]')
    li.addContextMenuItems(commands, True)
    uri = construct_request({
        'func': 'GetChannelsDB',
        'title': 'ИЗБРАННЫЕ',
        'group': 'favourite'
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('[COLOR FF00FF00]Все каналы[/COLOR]')
    li.addContextMenuItems(commands, True)
    uri = construct_request({
        'func': 'GetChannelsDB',
        'title': 'Все каналы',
        'group': '0'
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('[COLOR FF00FF00]Последние просмотренные[/COLOR]')
    li.addContextMenuItems(commands, True)
    uri = construct_request({
        'func': 'GetChannelsDB',
        'title': 'Последние просмотренные',
        'group': 'latest'
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('[COLOR FF00FF00]HD Каналы[/COLOR]')
    li.addContextMenuItems(commands, True)
    uri = construct_request({
        'func': 'GetChannelsDB',
        'title': 'HD Каналы',
        'group': 'hd'
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('[COLOR FF00FF00]Новые каналы[/COLOR]')
    li.addContextMenuItems(commands, True)
    uri = construct_request({
        'func': 'GetChannelsDB',
        'title': 'Новые каналы',
        'group': 'new'
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('[COLOR FF0099FF]На модерации[/COLOR]')
    li.addContextMenuItems(commands, True)
    uri = construct_request({
        'func': 'GetChannelsWeb',
        'title': 'На модерации',
        'file': 'on_moderation.php'
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('[COLOR FF0099FF]Трансляции[/COLOR]')
    li.addContextMenuItems(commands, True)
    uri = construct_request({
        'func': 'GetChannelsWeb',
        'title': 'Трансляции',
        'file': 'translations.php'
    })
    li.addContextMenuItems(commands, True)
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    GetParts()
    xbmcplugin.endOfDirectory(hos)
    
from urllib import unquote, quote, quote_plus

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

def addon_main():
    import datetime
    params = get_params(sys.argv[2])
    try:
        func = params['func']
        del params['func']
    except:
        
        db = DataBase(db_name, cookie='')        
        dbver = db.GetDBVer()
        if db.GetDBVer() <> 5:
            del db
            os.remove(db_name)

        db = DataBase(db_name, cookie='')
        lupd = db.GetLastUpdate()
        if lupd == None:
            showMessage('Torrent TV', 'Производится обновление плейлиста')
            #UpdCookie()
            #if os.path.exists(cookiefile):
                #fgetcook = open(cookiefile, 'r')
            cookie = UpdCookie()
            #del fgetcook
            db = DataBase(db_name, cookie)
            db.UpdateDB()
            showMessage('Torrent TV', 'Обновление плейлиста выполнено')
        else:
            nupd = lupd + datetime.timedelta(hours = 7)

            if nupd < datetime.datetime.now():
                showMessage('Torrent TV', 'Производится обновление плейлиста')
                #UpdCookie()
                #if os.path.exists(cookiefile):
                    #fgetcook = open(cookiefile, 'r')
                cookie = UpdCookie()
                #del fgetcook
                db = DataBase(db_name, cookie)
                db.UpdateDB()
                showMessage('Torrent TV', 'Обновление плейлиста выполнено')
        del db
        
        func = None
        xbmc.log( '[%s]: Primary input' % addon_id, 1 )

        mainScreen(params)
    if func != None:
        try:
            pfunc = globals()[func]
        except:
            pfunc = None
            xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
            showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
        if pfunc:
            pfunc(params)
