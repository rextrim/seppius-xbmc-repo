#!/usr/bin/python
# -*- coding: utf-8 -*-

import string, xbmc, xbmcgui, xbmcplugin, xbmcaddon, os, sys, urllib, urllib2, cookielib, time, codecs, datetime
import socket
import sqlite3 as db

socket.setdefaulttimeout(35000)

PLUGIN_NAME   = 'YaTv'
siteUrl = 'm.tv.yandex.ru'
httpSiteUrl = 'http://' + siteUrl
sid_file = os.path.join(xbmc.translatePath('special://temp/'), 'script.module.YaTv.cookies.sid')

addon = xbmcaddon.Addon(id='script.module.YaTv')
handle = addon.getAddonInfo('id')
__settings__ = xbmcaddon.Addon(id='script.module.YaTv')
thumb = os.path.join( addon.getAddonInfo('path'), "icon.png" )
fanart = os.path.join( addon.getAddonInfo('path'), "fanart.jpg" )
icon = os.path.join( addon.getAddonInfo('path'), 'icon.png')
db_name = os.path.join( addon.getAddonInfo('path'), "move_info.db" )
c = db.connect(database=db_name)
cu = c.cursor()

def ru(x):return unicode(x,'utf8', 'ignore')
def xt(x):return xbmc.translatePath(x)
#tab="[COLOR 00000000]_[/COLOR]"

def rulower(str):
	str=str.strip()
	str=xt(str).lower()
	str=str.replace('Й','й')
	str=str.replace('Ц','ц')
	str=str.replace('У','у')
	str=str.replace('К','к')
	str=str.replace('Е','е')
	str=str.replace('Н','н')
	str=str.replace('Г','г')
	str=str.replace('Ш','ш')
	str=str.replace('Щ','щ')
	str=str.replace('З','з')
	str=str.replace('Х','х')
	str=str.replace('Ъ','ъ')
	str=str.replace('Ф','ф')
	str=str.replace('Ы','ы')
	str=str.replace('В','в')
	str=str.replace('А','а')
	str=str.replace('П','п')
	str=str.replace('Р','р')
	str=str.replace('О','о')
	str=str.replace('Л','л')
	str=str.replace('Д','д')
	str=str.replace('Ж','ж')
	str=str.replace('Э','э')
	str=str.replace('Я','я')
	str=str.replace('Ч','ч')
	str=str.replace('С','с')
	str=str.replace('М','м')
	str=str.replace('И','и')
	str=str.replace('Т','т')
	str=str.replace('Ь','ь')
	str=str.replace('Б','б')
	str=str.replace('Ю','ю')
	return str
	
from CnlD import *

def CID (id):
	try:YID=CnlDict[rulower(id)]
	except: 
#		try:YID=CnlDict[rulower(id).replace(' (украина)','').replace(' украина','').replace(' ua','').replace(' (россия)','').replace(' russia','').replace(' россия','')]
#		except:
#			try:YID=CnlDict[rulower(id).replace(' тв','').replace(' hd','').replace('.','').replace(' канал','')]
#			except:
#				try:YID=CnlDict[rulower(id).replace(' тв','').replace(' hd','').replace('.','').replace('-',' ').replace(' канал','').replace('  ',' ')]
#				except:
#					try:YID=CnlDict[rulower(id).replace(' тв','').replace(' hd','').replace(' (украина)','').replace(' украина','').replace(' ua','')]
#					except:
						print "КАНАЛ НЕ НАЙДЕН: '"+rulower(id)+"'"
						YID=id
	return YID

def mfindal(http, ss, es):
	L=[]
	while http.find(es)>0:
		s=http.find(ss)
		e=http.find(es)
		i=http[s:e]
		L.append(i)
		http=http[e+2:]
	return L


def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

def htmlEntitiesDecode(string):
	return BeautifulStoneSoup(string, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents[0]

def showMessage(heading, message, times = 3000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))


def GET(target, referer, post=None):
	try:
		req = urllib2.Request(url = target, data = post)
		req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
		resp = urllib2.urlopen(req, timeout=50000)
		http = resp.read()
		resp.close()
		return http
	except Exception, e:
		print 'HTTP ERROR '+ target


def formtext(http):
	dict={}
	ss='title="'
	es='</table><table class="b'
	Lhttp=mfindal(http, ss, es)
	#print "Каналов:"+ str(len(Lhttp))
	for cnl in Lhttp:
		ss='title="'
		es='" alt="'
		nmc=mfindal(cnl, ss, es)[0].replace(ss,"")
		ss="['http://m.tv.yandex.ru"
		es='#end'
		nprg=mfindal(cnl.replace("'",'"').replace('class="time"><a href="',"['http://m.tv.yandex.ru").replace('</a></td><td>',"','").replace('">',"','").replace('</td></tr>',"']#end")+"", ss, es)
		Lprg=[]
		for i in nprg:
			Lprg.append(eval(i))
		dict[nmc]=Lprg
	return dict

def formtext3(http):
	dict={}
	ss='title="'
	es='Выбор каналов'
	Lhttp=mfindal(http, ss, es)
	#print "Каналов:"+ str(len(Lhttp))
	for cnl in Lhttp:
		ss='title="'
		es='" alt="'
		nmc=mfindal(cnl, ss, es)[0].replace(ss,"")
		ss="['http://m.tv.yandex.ru"
		es='#end'
		nprg=mfindal(cnl.replace("'",'"').replace('class="time"><a href="',"['http://m.tv.yandex.ru").replace('</a></td><td>',"','").replace('">',"','").replace('</td></tr>',"']#end")+"", ss, es)
		Lprg=[]
		for i in nprg:
			Lprg.append(eval(i))
		dict[nmc]=Lprg
	return dict

def formtext2(http):
	dict={}
	ss='alt="" title="" src="'
	es='" /><div class="b-broadcast__time'
	try:
		img=mfindal(http, ss, es)[0].replace(ss,"")#.replace("middle","orig")
	except:img=""
	ss='b-broadcast__info"><p>'
	es='</p><'
	try:pl=mfindal(http, ss, es)[0].replace(ss,"")
	except: pl=""
	ss='class="b-icon" src="'
	es='orig" title="'
	try:ico=mfindal(http, ss, es)[0].replace(ss,"")+'orig'
	except: ico=""
	return {"img":img,"pl":pl,"ico":ico}


#RUList={"АСТРО ТВ": "249", "Ля-Минор": "257", "STV": "165", "Комсомольская правда": "852", "Девятый (Орбита)": "237", "MTV European": "270", "Союз": "349", "ТБН": "576", "MTV Live HD": "382", "Нано ТВ": "35", "Закон-ТВ": "178", "Eurosport HD": "560", "ТРО": "730", "BRIDGE TV": "151", "Fox Life HD": "464", "РЖД": "509", "Pro все": "458", "Просвещение": "685", "Раз ТВ": "363", "Nat Geo Wild HD": "807", "Fashion TV HD": "121", "АГРО-ТВ": "11", "Эгоист ТВ": "431", "MTV Music": "430", "Юмор BOX": "412", "Trace Urban": "473", "Motors TV": "531", "Спорт 1 HD": "554", "World Music Channel": "91", "VH1 European": "491", "ТурИнфо": "731", "Телепутешествия HD": "331", "Rusong TV": "591", "Открытый Мир": "39", "Охотник и Рыболов": "132", "NewsOne": "247", "Недвижимость": "552", "myZen.tv": "141", "MusicBox TV": "642", "MusicBox RU": "25", "MCM TOP": "533", "MCM POP": "804", "Luxe.TV": "442", "ЧП.Info": "315", "Первый метео": "59", "HD Медиа": "631", "France 24": "461", "Fine Living Network": "393", "English Club TV": "757", "CNBC": "831", "C Music TV": "319", "BizTV": "797", "BBC Entertainment": "278", "Страна": "284", "О2ТВ": "777", "Музыка Первого": "715", "Luxe HD": "312", "Deutsche Welle": "355", "BBC World": "828", "Ajara TV": "756", "HD КИНО 2": "988", "HD КИНО": "987", "Бойцовский клуб": "986", "ENCYCLO": "989", "Animal Planet HD": "990", "РОССИЯ HD": "984", "ПЕРВЫЙ HD": "983", "CBS Reality": "912", "CBS Drama": "911", "ЕДА HD": "930", "ЕДА": "931", "Paramount Comedy": "920", "Детский мир + Телеклуб": "923", "Беларусь-24": "851", "PRO Business": "214", "Спорт Союз": "306", "Русский роман": "401", "Кинолюкс": "8", "365": "250", "HD Life": "415", "Авто Плюс": "153", "Кухня ТВ": "614", "Комедия ТВ": "821", "Много ТВ": "799", "Интересное ТВ": "24", "8 Канал": "217", "SONY ТВ": "311", "НТВ-ПЛЮС Футбол 2": "563", "НТВ-ПЛЮС Теннис": "358", "НТВ-ПЛЮС Баскетбол": "697", "НТВ-ПЛЮС Спорт Онлайн": "183", "НТВ-ПЛЮС Футбол": "664", "НТВ-ПЛЮС Спорт": "134", "НТВ-ПЛЮС Наш футбол": "499", "НТВ-ПЛЮС Спорт Плюс": "377", "Outdoor Channel": "322", "Europa Plus TV": "681", "Знание": "201", "Шансон-TB": "662", "Discovery HD Showcase": "111", "DIVA Universal": "713", "ЖИВИ!": "113", "Nickelodeon HD": "423", "МИР": "726", "КХЛ": "481", "Eurosport": "737", "Ретро ТВ": "6", "Здоровое ТВ": "595", "Драйв": "505", "Zooпарк": "367", "Спорт": "154", "Наука 2.0": "723", "A-ONE": "680", "National Geographic HD": "389", "Ru.TV": "258", "Первый образовательный": "774", "TLC": "425", "МУЗ-ТВ": "897", "MTV Rocks": "388", "MTV Hits": "849", "MTV Dance": "332", "Baby TV": "308", "TiJi": "555", "TDK": "776", "Совершенно секретно": "275", "РТВ - Любимое кино": "477", "Тонус-ТВ": "637", "Zee-TV": "626", "Загородная жизнь": "21", "Загородный": "705", "Кто есть кто": "769", "Оружие": "376", "Всегда с тобой": "604", "Вопросы и ответы": "333", "Viasat Sport": "455", "VH1 Classic": "156", "Успех": "547", "Улыбка Ребенка": "789", "TV1000 Action": "125", "Style TV": "119", "Russia Today": "313", "Russian Travel Guide": "648", "Дождь": "384", "Психология 21": "434", "Парк развлечений": "37", "КИНО ПЛЮС": "644", "Мультимания": "31", "Футбол": "328", "Nat Geo WILD": "223", "Viasat Nature CEE": "765", "Мужской": "82", "Мир сериала": "145", "Mezzo Live HD": "801", "Man TV": "15", "Кинопоказ HD-2": "741", "Кинопоказ HD-1": "138", "Комеди ТВ": "51", "Киномания": "646", "KidsCo": "598", "JimJam": "494", "Investigation Discovery": "19", "Еврокино": "352", "Домашние животные": "520", "Gulli": "810", "Fox Life": "615", "FOX": "659", "Da Vinci": "410", "BBC": "502", "24 ДОК": "16", "Школьник": "61", "Феникс+ Кино": "686", "Усадьба": "779", "ТНВ": "180", "Тин ТВ": "716", "Телепутешествия": "794", "Телеклуб": "163", "Телекафе": "173", "Спорт 1": "181", "Спас ТВ": "447", "Сарафан": "663", "Русский Экстрим": "406", "Русский Иллюзион": "53", "РБК": "743", "Радость Моя": "638", "Премьера": "566", "Охота и рыбалка": "617", "Ностальгия": "783", "Наше Новое Кино": "485", "Наше кино": "12", "Настоящее Страшное Телевидение": "518", "Моя Планета": "675", "Мать и дитя": "618", "Кинохит": "542", "Киносоюз": "71", "Кинопоказ": "22", "Киноклуб": "462", "Индия ТВ": "798", "Иллюзион +": "123", "Зоо ТВ": "273", "Дом кино": "834", "Детский мир": "747", "Детский": "66", "Время": "669", "Боец": "454", "World Fashion Channel": "346", "Viasat History": "277", "Viasat Explorer": "521", "Universal Channel": "213", "TV5": "589", "TV XXI": "309", "TV1000 Русское кино": "267", "TV1000": "127", "Ocean TV": "55", "Nickelodeon": "567", "National Geographic": "102", "MGM": "608", "Mezzo": "575", "HD Спорт": "429", "Fashion TV": "661", "Extreme Sports": "288", "Eurosport 2": "850", "EuroNews": "23", "ESPN classic": "60", "Discovery World": "437", "Discovery Science": "409", "Discovery Channel": "325", "CNN": "495", "Cartoon Network": "601", "Bloomberg": "463", "AXN Sci-Fi": "516", "Animal Planet": "365", "Amazing Life": "658", "AB Moteurs": "579", "24 Техно": "710", "Sony Turbo": "935", "MGM HD": "934", "ТНВ-планета": "933", "Синергия ТВ": "932", "Boomerang": "929", "Discovery Восточная Европа": "928", "iConcerts": "927", "ОСТ": "926", "Театр": "925", "Galaxy TV": "924", "Первый Интернет Канал": "922", "NHK WORLD TV": "921", "Fashion One": "919", "AMEDIA": "918", "Nick Jr": "917", "ИНВА МЕДИА ТВ": "916", "Москва-24": "334", "Подмосковье": "161", "Семья": "335", "Москва. Доверие": "655", "ВКТ": "421", "Канал Disney": "150", "Ю": "898", "MTV": "557", "2x2": "323", "Карусель": "740", "Россия 24": "291", "ТВ3": "698", "ПЕРЕЦ": "511", "Звезда": "405", "5 канал": "427", "СТС": "79", "РЕН ТВ": "18", "Домашний": "304", "ТНТ": "353", "Россия 2": "515", "Культура": "187", "НТВ": "162", "ТВ Центр": "649", "Россия 1": "711", "Первый": "146", }

#UKList={"Fine Living Network Украина": "393", "АСТРО ТВ Украина": "249", "Ля-Минор Украина": "257", "STV Украина": "165", "Комсомольская правда Украина": "852", "Девятый (Орбита) Украина": "237", "MTV European Украина": "270", "Союз Украина": "349", "ТБН Украина": "576", "MTV Live HD Украина": "382", "Нано ТВ Украина": "35", "Закон-ТВ Украина": "178", "Eurosport HD Украина": "560", "ТРО Украина": "730", "BRIDGE TV Украина": "151", "Fox Life HD Украина": "464", "Pro все Украина": "458", "Просвещение Украина": "685", "Раз ТВ Украина": "363", "Nat Geo Wild HD Украина": "807", "Fashion TV HD Украина": "121", "АГРО-ТВ Украина": "11", "Эгоист ТВ Украина": "431", "MTV Music Украина": "430", "Юмор BOX Украина": "412", "Trace Urban Украина": "473", "Motors TV Украина": "531", "Спорт 1 HD Украина": "554", "Беларусь-24 Украина": "851", "PRO Business Украина": "214", "Спорт Союз Украина": "306", "Русский роман Украина": "401", "Кинолюкс Украина": "8", "365 Украина": "250", "HD Life Украина": "415", "Авто Плюс Украина": "153", "Кухня ТВ Украина": "614", "Комедия ТВ Украина": "821", "Много ТВ Украина": "799", "Интересное ТВ Украина": "24", "8 Канал Украина": "217", "SONY ТВ Украина": "311", "НТВ-ПЛЮС Футбол 2 Украина": "563", "World Music Channel Украина": "91", "НТВ-ПЛЮС Теннис Украина": "358", "НТВ-ПЛЮС Баскетбол Украина": "697", "НТВ-ПЛЮС Спорт Онлайн Украина": "183", "НТВ-ПЛЮС Футбол Украина": "664", "НТВ-ПЛЮС Спорт Украина": "134", "НТВ-ПЛЮС Наш футбол Украина": "499", "VH1 European Украина": "491", "НТВ-ПЛЮС Спорт Плюс Украина": "377", "Outdoor Channel Украина": "322", "Europa Plus TV Украина": "681", "Знание Украина": "201", "Шансон-TB Украина": "662", "ТурИнфо Украина": "731", "Discovery HD Showcase Украина": "111", "DIVA Universal Украина": "713", "Телепутешествия HD Украина": "331", "ЖИВИ! Украина": "113", "Nickelodeon HD Украина": "423", "МИР Украина": "726", "КХЛ Украина": "481", "Eurosport Украина": "737", "Rusong TV Украина": "591", "Ретро ТВ Украина": "6", "Здоровое ТВ Украина": "595", "Драйв Украина": "505", "Zooпарк Украина": "367", "Спорт Украина": "154", "Открытый Мир Украина": "39", "Наука 2.0 Украина": "723", "Охотник и Рыболов Украина": "132", "A-ONE Украина": "680", "National Geographic HD Украина": "389", "Ru.TV Украина": "258", "Первый образовательный Украина": "774", "TLC Украина": "425", "NewsOne Украина": "247", "МУЗ-ТВ Украина": "897", "Недвижимость Украина": "552", "MTV Rocks Украина": "388", "MTV Hits Украина": "849", "myZen.tv Украина": "141", "MTV Dance Украина": "332", "MusicBox TV Украина": "642", "Baby TV Украина": "308", "TiJi Украина": "555", "MusicBox RU Украина": "25", "TDK Украина": "776", "Совершенно секретно Украина": "275", "MCM TOP Украина": "533", "MCM POP Украина": "804", "РТВ - Любимое кино Украина": "477", "Тонус-ТВ Украина": "637", "Zee-TV Украина": "626", "Luxe.TV Украина": "442", "Загородная жизнь Украина": "21", "Загородный Украина": "705", "Кто есть кто Украина": "769", "Оружие Украина": "376", "Всегда с тобой Украина": "604", "Вопросы и ответы Украина": "333", "Viasat Sport Украина": "455", "VH1 Classic Украина": "156", "Успех Украина": "547", "Улыбка Ребенка Украина": "789", "ЧП.Info Украина": "315", "TV1000 Action Украина": "125", "Первый метео Украина": "59", "HD Медиа Украина": "631", "Style TV Украина": "119", "Карусель INT Украина": "465", "France 24 Украина": "461", "Russia Today Украина": "313", "Russian Travel Guide Украина": "648", "Дождь Украина": "384", "English Club TV Украина": "757", "Психология 21 Украина": "434", "Парк развлечений Украина": "37", "КИНО ПЛЮС Украина": "644", "CNBC Украина": "831", "Мультимания Украина": "31", "Футбол Украина": "328", "C Music TV Украина": "319", "Nat Geo WILD Украина": "223", "Viasat Nature CEE Украина": "765", "Мужской Украина": "82", "Мир сериала Украина": "145", "Mezzo Live HD Украина": "801", "Man TV Украина": "15", "Кинопоказ HD-2 Украина": "741", "Кинопоказ HD-1 Украина": "138", "Комеди ТВ Украина": "51", "Киномания Украина": "646", "KidsCo Украина": "598", "JimJam Украина": "494", "Страна Украина": "284", "Investigation Discovery Украина": "19", "Еврокино Украина": "352", "Домашние животные Украина": "520", "Gulli Украина": "810", "Fox Life Украина": "615", "FOX Украина": "659", "Da Vinci Украина": "410", "BBC Украина": "502", "24 ДОК Украина": "16", "RTVI Украина": "76", "О2ТВ Украина": "777", "Феникс+ Кино Украина": "686", "Усадьба Украина": "779", "ТНВ Украина": "180", "Тин ТВ Украина": "716", "Телепутешествия Украина": "794", "Музыка Первого Украина": "715", "Телеклуб Украина": "163", "Телекафе Украина": "173", "Спорт 1 Украина": "181", "Спас ТВ Украина": "447", "Сарафан Украина": "663", "Русский Экстрим Украина": "406", "Русский Иллюзион Украина": "53", "РБК Украина": "743", "Радость Моя Украина": "638", "Премьера Украина": "566", "Охота и рыбалка Украина": "617", "Ностальгия Украина": "783", "Наше Новое Кино Украина": "485", "Наше кино Украина": "12", "Настоящее Страшное Телевидение Украина": "518", "Моя Планета Украина": "675", "Мать и дитя Украина": "618", "Кинохит Украина": "542", "Киносоюз Украина": "71", "Кинопоказ Украина": "22", "Киноклуб Украина": "462", "Индия ТВ Украина": "798", "Иллюзион + Украина": "123", "Зоо ТВ Украина": "273", "Дом кино Украина": "834", "Детский мир Украина": "747", "Детский Украина": "66", "Время Украина": "669", "Боец Украина": "454", "World Fashion Channel Украина": "346", "Viasat History Украина": "277", "Viasat Explorer Украина": "521", "Universal Channel Украина": "213", "TV5 Украина": "589", "Luxe HD Украина": "312", "TV XXI Украина": "309", "TV1000 Русское кино Украина": "267", "TV1000 Украина": "127", "Ocean TV Украина": "55", "Nickelodeon Украина": "567", "National Geographic Украина": "102", "MGM Украина": "608", "Mezzo Украина": "575", "HD Спорт Украина": "429", "Fashion TV Украина": "661", "Deutsche Welle Украина": "355", "Extreme Sports Украина": "288", "Eurosport 2 Украина": "850", "EuroNews Украина": "23", "BBC World Украина": "828", "ESPN classic Украина": "60", "Discovery World Украина": "437", "Discovery Science Украина": "409", "Discovery Channel Украина": "325", "Ajara TV Украина": "756", "CNN Украина": "495", "Cartoon Network Украина": "601", "Bloomberg Украина": "463", "AXN Sci-Fi Украина": "516", "Maксi-TВ Украина": "228", "Amazing Life Украина": "658", "AB Moteurs Украина": "579", "24 Техно Украина": "710", "НТВ-Мир Украина": "422", "ТВ Центр-International Украина": "435", "Россия-Планета Украина": "143", "Первый Украина": "391", "QTV Украина": "280", "СТС International Украина": "166", "Хоккей Украина": "702", "Россия 24 Украина": "291", "Футбол+ Украина": "753", "Футбол Украина": "666", "Первый деловой Украина": "85", "Интер+ Украина": "808", "Первый автомобильный Украина": "507", "ТРК Юнион Украина": "90", "34 телеканал Украина": "561", "ТРК Донбасс Украина": "641", "Киев Украина": "634", "ТВi Украина": "650", "Тонис Украина": "627", "ТК Мега Украина": "788", "Добро ТВ (Украина) Украина": "937", "Ukrainian Fashion (Украина) Украина": "939", "Animal Planet Украина": "607", "РЕН ТВ Украина": "689", "O-TV Украина": "167", "М1 Украина": "632", "Пиксель Украина": "940", "5 канал Украина": "586", "Enter-фильм Украина": "281", "К1 Украина": "453", "ТЕТ Украина": "479", "2+2 Украина": "583", "Первый национальный Украина Украина": "773", "Новый канал Украина": "128", "НТН Украина": "140", "ICTV Украина": "709", "СТБ Украина": "670", "Украина Украина": "326", "1+1 Украина": "620", "Интер Украина": "677", }


def upd1(rg, ch):
	categoryUrl = 'http://m.tv.yandex.ru/213/?when=1&channel=146%2C711%2C649%2C162%2C187%2C515%2C353%2C304%2C18%2C79%2C427%2C405%2C511%2C698%2C291%2C740%2C323%2C557%2C898%2C150%2C421%2C655%2C335%2C161%2C334%2C916%2C917%2C918%2C919%2C921%2C922%2C924%2C925%2C926%2C927%2C928%2C929%2C932%2C933%2C934%2C935%2C710%2C579%2C658%2C365%2C516%2C463%2C601%2C495%2C325%2C409%2C437%2C60%2C23%2C850%2C288%2C661%2C429%2C575%2C608%2C102%2C567%2C55%2C127%2C267%2C309%2C589%2C213%2C521%2C277%2C346%2C454%2C669%2C66%2C747%2C834%2C273%2C123%2C798%2C462%2C22%2C71%2C542%2C618%2C675%2C518%2C12%2C485%2C783%2C617%2C566%2C638%2C743%2C53%2C406%2C663%2C447%2C181%2C173%2C163%2C794%2C716%2C180%2C779%2C686%2C61%2C16%2C502%2C410%2C659%2C615%2C810%2C520%2C352%2C19%2C494%2C598%2C646%2C51%2C138%2C741%2C15%2C801%2C145%2C82%2C765%2C223%2C328%2C31%2C644%2C37%2C434%2C384%2C648%2C313%2C119%2C125%2C789%2C547%2C156%2C455%2C333%2C604%2C376%2C769%2C705%2C21%2C626%2C637%2C477%2C275%2C776%2C555%2C308%2C332%2C849%2C388%2C897%2C425%2C774%2C258%2C389%2C680%2C723%2C154%2C367%2C505%2C595%2C6%2C737%2C481%2C726%2C423%2C113%2C713%2C111%2C662%2C201%2C681%2C322%2C377%2C499%2C134%2C664%2C183%2C697%2C358%2C563%2C311%2C217%2C24%2C799%2C821%2C614%2C153%2C415%2C250%2C8%2C401%2C306%2C214%2C851%2C923%2C920%2C931%2C930%2C911%2C912%2C983%2C984%2C990%2C989%2C986%2C987%2C988%2C756%2C828%2C355%2C312%2C715%2C777%2C284%2C278%2C797%2C319%2C831%2C757%2C393%2C461%2C631%2C59%2C315%2C442%2C804%2C533%2C25%2C642%2C141%2C552%2C247%2C132%2C39%2C591%2C331%2C731%2C491%2C91%2C554%2C531%2C473%2C412%2C430%2C431%2C11%2C121%2C807%2C363%2C685%2C458%2C509%2C464%2C151%2C730%2C560%2C178%2C35%2C382%2C576%2C349%2C270%2C237%2C852%2C165%2C257%2C249%2C994'

	http = GET(categoryUrl, categoryUrl)
	if http == None:
		showMessage('YaTV:', 'Сервер не отвечает', 1000)
		return None
	else:
		d=formtext(http)
		#return d
	#Украина
	categoryUrl = 'http://m.tv.yandex.ru/187/?when=1&channel=677%2C620%2C326%2C670%2C709%2C140%2C128%2C773%2C583%2C479%2C453%2C281%2C586%2C940%2C632%2C167%2C689%2C607%2C939%2C937%2C788%2C627%2C650%2C634%2C641%2C561%2C90%2C808%2C85%2C666%2C753%2C702%2C166%2C280%2C143%2C435%2C422%2C710%2C228%2C516%2C325%2C409%2C437%2C60%2C828%2C23%2C850%2C288%2C355%2C661%2C429%2C575%2C608%2C102%2C567%2C55%2C127%2C267%2C309%2C312%2C589%2C213%2C521%2C277%2C346%2C454%2C669%2C66%2C747%2C834%2C273%2C123%2C798%2C462%2C22%2C71%2C542%2C618%2C675%2C518%2C12%2C485%2C783%2C617%2C566%2C638%2C743%2C53%2C406%2C663%2C447%2C181%2C173%2C163%2C715%2C794%2C716%2C180%2C779%2C686%2C777%2C76%2C16%2C502%2C410%2C659%2C615%2C810%2C520%2C352%2C19%2C284%2C494%2C598%2C646%2C51%2C138%2C741%2C15%2C801%2C145%2C82%2C765%2C223%2C319%2C328%2C31%2C831%2C644%2C37%2C434%2C757%2C384%2C648%2C313%2C461%2C465%2C119%2C631%2C59%2C125%2C315%2C789%2C547%2C156%2C455%2C333%2C604%2C376%2C769%2C705%2C21%2C442%2C626%2C637%2C477%2C804%2C533%2C275%2C776%2C25%2C555%2C308%2C642%2C332%2C141%2C849%2C388%2C552%2C897%2C247%2C425%2C774%2C258%2C389%2C680%2C132%2C723%2C39%2C154%2C367%2C505%2C595%2C6%2C591%2C737%2C481%2C726%2C423%2C113%2C331%2C713%2C111%2C731%2C662%2C201%2C681%2C322%2C377%2C491%2C499%2C134%2C664%2C183%2C697%2C358%2C91%2C563%2C311%2C217%2C24%2C799%2C821%2C614%2C153%2C415%2C250%2C8%2C401%2C306%2C214%2C851%2C554%2C531%2C473%2C412%2C430%2C431%2C11%2C121%2C807%2C363%2C685%2C458%2C464%2C151%2C730%2C560%2C178%2C35%2C382%2C576%2C349%2C270%2C237%2C852%2C165%2C257%2C249%2C393'
	http = GET(categoryUrl, categoryUrl)
	if http == None:
		showMessage('YaTV:', 'Сервер не отвечает', 1000)
		return None
	else:
		d2=formtext(http)
		for i in d2:
			d[i+" Украина"]=d2[i]
	save_cache(repr(d))

def upd12(rg, ch):
    start=str(int(time.time())*1000)
    region='213'
    channel='146%2C711%2C649%2C162%2C187%2C515%2C353%2C304%2C18%2C79%2C427%2C405%2C511%2C698%2C291%2C740%2C323%2C557%2C898%2C150%2C421%2C655%2C335%2C161%2C334%2C916%2C917%2C918%2C919%2C921%2C922%2C924%2C925%2C926%2C927%2C928%2C929%2C932%2C933%2C934%2C935%2C710%2C579%2C658%2C365%2C516%2C463%2C601%2C495%2C325%2C409%2C437%2C60%2C23%2C850%2C288%2C661%2C429%2C575%2C608%2C102%2C567%2C55%2C127%2C267%2C309%2C589%2C213%2C521%2C277%2C346%2C454%2C669%2C66%2C747%2C834%2C273%2C123%2C798%2C462%2C22%2C71%2C542%2C618%2C675%2C518%2C12%2C485%2C783%2C617%2C566%2C638%2C743%2C53%2C406%2C663%2C447%2C181%2C173%2C163%2C794%2C716%2C180%2C779%2C686%2C61%2C16%2C502%2C410%2C659%2C615%2C810%2C520%2C352%2C19%2C494%2C598%2C646%2C51%2C138%2C741%2C15%2C801%2C145%2C82%2C765%2C223%2C328%2C31%2C644%2C37%2C434%2C384%2C648%2C313%2C119%2C125%2C789%2C547%2C156%2C455%2C333%2C604%2C376%2C769%2C705%2C21%2C626%2C637%2C477%2C275%2C776%2C555%2C308%2C332%2C849%2C388%2C897%2C425%2C774%2C258%2C389%2C680%2C723%2C154%2C367%2C505%2C595%2C6%2C737%2C481%2C726%2C423%2C113%2C713%2C111%2C662%2C201%2C681%2C322%2C377%2C499%2C134%2C664%2C183%2C697%2C358%2C563%2C311%2C217%2C24%2C799%2C821%2C614%2C153%2C415%2C250%2C8%2C401%2C306%2C214%2C851%2C923%2C920%2C931%2C930%2C911%2C912%2C983%2C984%2C990%2C989%2C986%2C987%2C988%2C756%2C828%2C355%2C312%2C715%2C777%2C284%2C278%2C797%2C319%2C831%2C757%2C393%2C461%2C631%2C59%2C315%2C442%2C804%2C533%2C25%2C642%2C141%2C552%2C247%2C132%2C39%2C591%2C331%2C731%2C491%2C91%2C554%2C531%2C473%2C412%2C430%2C431%2C11%2C121%2C807%2C363%2C685%2C458%2C509%2C464%2C151%2C730%2C560%2C178%2C35%2C382%2C576%2C349%2C270%2C237%2C852%2C165%2C257%2C249%2C777%2C984%2C412%2C382%2C178%2C655%2C119%2C994'
    Url = 'http://tv.yandex.ru/actions/getSchedule.xml?start='+start+'&channels='+channel+'&region='+region
    http = GET(Url, Url)
    if http == None:
        showMessage('YaTV:', 'Сервер не отвечает', 1000)
        http = GET(Url, Url)
        if http == None:
            http = GET(Url, Url)
            if http == None:
                return None
            else:
                d=http.replace("\\/","/").replace("}}]}}}","}}]}")
        else:
            d=http.replace("\\/","/").replace("}}]}}}","}}]}")
    else:
        d=http.replace("\\/","/").replace("}}]}}}","}}]}")
    #Украина
    region='187'
    channel= '620%2C583%2C586%2C680%2C937%2C281%2C709%2C228%2C430%2C167%2C280%2C76%2C627%2C939%2C677%2C808%2C453%2C632%2C788%2C128%2C422%2C140%2C507%2C85%2C773%2C940%2C143%2C181%2C670%2C650%2C479%2C326%2C90%2C666%2C753%2C702%2C315%2C435%2C689%2C391%2C166'
    Url = 'http://tv.yandex.ru/actions/getSchedule.xml?start='+start+'&channels='+channel+'&region='+region
    http = GET(Url, Url)
    if http == None:
        showMessage('YaTV:', 'Сервер не отвечает', 1000)
        http = GET(Url, Url)
        if http == None:
            http = GET(Url, Url)
            if http == None:
                return None
            else:
                d2=http.replace("\\/","/").replace('{"channels":{',",")
                d3=d+d2
        else:
            d2=http.replace("\\/","/").replace('{"channels":{',",")
            d3=d+d2
    else:
        d2=http.replace("\\/","/").replace('{"channels":{',",")
        d3=d+d2
    save_cache(d3)
    return d3




def upd3(rg, ch):
	categoryUrl = 'http://m.tv.yandex.ru/213/?when=1&channel=146%2C711%2C649%2C162%2C187%2C515%2C353%2C304%2C18%2C79%2C427%2C405%2C511%2C698%2C291%2C740%2C323%2C557%2C898%2C150%2C421%2C655%2C335%2C161%2C334%2C916%2C917%2C918%2C919%2C921%2C922%2C924%2C925%2C926%2C927%2C928%2C929%2C932%2C933%2C934%2C935%2C710%2C579%2C658%2C365%2C516%2C463%2C601%2C495%2C325%2C409%2C437%2C60%2C23%2C850%2C288%2C661%2C429%2C575%2C608%2C102%2C567%2C55%2C127%2C267%2C309%2C589%2C213%2C521%2C277%2C346%2C454%2C669%2C66%2C747%2C834%2C273%2C123%2C798%2C462%2C22%2C71%2C542%2C618%2C675%2C518%2C12%2C485%2C783%2C617%2C566%2C638%2C743%2C53%2C406%2C663%2C447%2C181%2C173%2C163%2C794%2C716%2C180%2C779%2C686%2C61%2C16%2C502%2C410%2C659%2C615%2C810%2C520%2C352%2C19%2C494%2C598%2C646%2C51%2C138%2C741%2C15%2C801%2C145%2C82%2C765%2C223%2C328%2C31%2C644%2C37%2C434%2C384%2C648%2C313%2C119%2C125%2C789%2C547%2C156%2C455%2C333%2C604%2C376%2C769%2C705%2C21%2C626%2C637%2C477%2C275%2C776%2C555%2C308%2C332%2C849%2C388%2C897%2C425%2C774%2C258%2C389%2C680%2C723%2C154%2C367%2C505%2C595%2C6%2C737%2C481%2C726%2C423%2C113%2C713%2C111%2C662%2C201%2C681%2C322%2C377%2C499%2C134%2C664%2C183%2C697%2C358%2C563%2C311%2C217%2C24%2C799%2C821%2C614%2C153%2C415%2C250%2C8%2C401%2C306%2C214%2C851%2C923%2C920%2C931%2C930%2C911%2C912%2C983%2C984%2C990%2C989%2C986%2C987%2C988%2C756%2C828%2C355%2C312%2C715%2C777%2C284%2C278%2C797%2C319%2C831%2C757%2C393%2C461%2C631%2C59%2C315%2C442%2C804%2C533%2C25%2C642%2C141%2C552%2C247%2C132%2C39%2C591%2C331%2C731%2C491%2C91%2C554%2C531%2C473%2C412%2C430%2C431%2C11%2C121%2C807%2C363%2C685%2C458%2C509%2C464%2C151%2C730%2C560%2C178%2C35%2C382%2C576%2C349%2C270%2C237%2C852%2C165%2C257%2C249'

	http = GET(categoryUrl, categoryUrl)
	if http == None:
		showMessage('RuTor:', 'Сервер не отвечает', 1000)
		return None
	else:
		d=formtext(http)
	#Украина
	categoryUrl = 'http://m.tv.yandex.ru/187/?when=1&channel=677%2C620%2C326%2C670%2C709%2C140%2C128%2C773%2C583%2C479%2C453%2C281%2C586%2C940%2C632%2C167%2C689%2C607%2C939%2C937%2C788%2C627%2C650%2C634%2C641%2C561%2C90%2C808%2C85%2C666%2C753%2C702%2C166%2C280%2C143%2C435%2C422%2C710%2C228%2C516%2C325%2C409%2C437%2C60%2C828%2C23%2C850%2C288%2C355%2C661%2C429%2C575%2C608%2C102%2C567%2C55%2C127%2C267%2C309%2C312%2C589%2C213%2C521%2C277%2C346%2C454%2C669%2C66%2C747%2C834%2C273%2C123%2C798%2C462%2C22%2C71%2C542%2C618%2C675%2C518%2C12%2C485%2C783%2C617%2C566%2C638%2C743%2C53%2C406%2C663%2C447%2C181%2C173%2C163%2C715%2C794%2C716%2C180%2C779%2C686%2C777%2C76%2C16%2C502%2C410%2C659%2C615%2C810%2C520%2C352%2C19%2C284%2C494%2C598%2C646%2C51%2C138%2C741%2C15%2C801%2C145%2C82%2C765%2C223%2C319%2C328%2C31%2C831%2C644%2C37%2C434%2C757%2C384%2C648%2C313%2C461%2C465%2C119%2C631%2C59%2C125%2C315%2C789%2C547%2C156%2C455%2C333%2C604%2C376%2C769%2C705%2C21%2C442%2C626%2C637%2C477%2C804%2C533%2C275%2C776%2C25%2C555%2C308%2C642%2C332%2C141%2C849%2C388%2C552%2C897%2C247%2C425%2C774%2C258%2C389%2C680%2C132%2C723%2C39%2C154%2C367%2C505%2C595%2C6%2C591%2C737%2C481%2C726%2C423%2C113%2C331%2C713%2C111%2C731%2C662%2C201%2C681%2C322%2C377%2C491%2C499%2C134%2C664%2C183%2C697%2C358%2C91%2C563%2C311%2C217%2C24%2C799%2C821%2C614%2C153%2C415%2C250%2C8%2C401%2C306%2C214%2C851%2C554%2C531%2C473%2C412%2C430%2C431%2C11%2C121%2C807%2C363%2C685%2C458%2C464%2C151%2C730%2C560%2C178%2C35%2C382%2C576%2C349%2C270%2C237%2C852%2C165%2C257%2C249%2C393'
	http = GET(categoryUrl, categoryUrl)
	if http == None:
		showMessage('YaTV:', 'Сервер не отвечает', 1000)
		return None
	else:
		d2=formtext(http)
		for i in d2:
			d[i+" Украина"]=d2[i]
	
	return d


def upd2(categoryUrl):#(rg, pr, ev):
	http = GET(categoryUrl, categoryUrl)
	if http == None:
		print "НЕТ ОТВЕТА ОТ YANDEX"
		return None
	else:
		d=formtext2(http)
		return d
		
def upd22(d):#(rg, pr, ev):
	program=d["program"]["id"]
	event=d["eventId"]
	Url = 'http://tv.yandex.ru/actions/getShortProgramInfo.xml?program='+program+'&event='+event
	http = GET(Url, Url)
	if http == None:
		xbmc.sleep(250)
		http = GET(Url, Url)
		d=http.replace("\\/","//")
		return d
		if http == None:
			print "НЕТ ОТВЕТА ОТ YANDEX"
			return None
	else:
		d=http.replace("\\/","//")
		return d

def updday(ncl):
	try:
		ch=RUList[ncl]
		rg="213"
		print "RU"
	except:
		try:
			ch=UKList[ncl]
			rg="187"
			print "UC"
		except:
			rg=0
	if rg!=0:
		categoryUrl = 'http://m.tv.yandex.ru/'+rg+'/?when=2&channel='+ch
		print categoryUrl
		http = GET(categoryUrl, categoryUrl)
		if http == None:
			showMessage('YaTV:', 'Сервер не отвечает', 1000)
			return None
		else:
			d=formtext3(http)
			print d
			return d
	return []

def GetPr_off():
		#print "запрос стр"
		d=get_cache()#upd1("193", "146")
		rez={}
		#print "обработка"
		for i in d:
			title = d[i]["title"]
			logo  = d[i]["logo"]["src"]
			prlist= d[i]["schedule"]
			plot = []
			k=0
			for j in prlist:
				k+=1
				if k==1:
					id=j[0].replace("http://m.tv.yandex.ru/","").replace("/program/","").replace("/event/","")
					try:
						dd=get_inf_db(id)[0][0].replace("#z","\\").replace("#y",'"')
						d2=eval(dd)
						img=d2["img"].replace("middle","orig")
						pl=d2["pl"]
						ico=d2["ico"]
						plot = plot +"[B][COLOR FF0084FF]"+ j[1]+"[/COLOR] [COLOR FFFFFFFF]"+j[2]+"[/COLOR][/B][COLOR FF999999]"+chr(10)+pl+"[/COLOR]"+chr(10)
					except: 
						img=""
						pl=""
						ico=""
						plot = plot +"[B][COLOR FF0084FF]"+ j[1]+"[/COLOR] [COLOR FFFFFFFF]"+j[2]+"[/COLOR][/B]"+chr(10)
				else:
					plot = plot +"[B][COLOR FF0084FF]"+ j[1]+"[/COLOR] [COLOR FFFFFFFF]"+j[2]+"[/COLOR][/B]"+chr(10)
			rez[i]={"plot":plot, "img":img, "ico":ico}
		#print "возврат"
		return rez


def GetPr(id2,format=None):
        #print "запрос"
        try:
            import torr2xbmc
            d=get_cache()["channels"][id2]
        except Exception, e:
            #print e
            return {}
        rez={}
        title      = d["title"]
        idch       = d["id"]
        try:logo   = d["logo"]["src"]
        except:logo=""
        prlist= d["schedule"]
        plot = []
        k=0
        plt=""
        p_list=[]
        for j in prlist:
            program = j["id"]
            event   = j["eventId"]
            finish_t= float(j["finish"])/1000
            if finish_t > time.time() and finish_t < (time.time()+60000):
                start_t = float(j["start"])/1000
                finish  = time.localtime(float(j["finish"])/1000)
                start   = time.localtime(float(j["start"])/1000)
                try:title_pr_1= j["program"]["title"] + ". "
                except:title_pr_1=''
                title_pr_2= j["title"]
                title_pr = title_pr_1 + title_pr_2
                try:type2= j["program"]["type"]
                except: type2=""
                try:age = j["program"]["age"]
                except: age="0"
                if finish.tm_min<10: f_time = str(finish.tm_hour)+":0"+str(finish.tm_min)
                else:                f_time = str(finish.tm_hour)+":"+str(finish.tm_min)
                if start.tm_min <10: s_time  = str(start.tm_hour)+":0"+str(start.tm_min)
                else:                s_time  = str(start.tm_hour)+":"+str(start.tm_min)
                k+=1
                if k==1:
                    id=program+event
                    try:
                        dd=eval(get_inf_db(id)[0][0].replace("#z","\\").replace("#y",'"'))#eval()
                        try:type=dd["program"]["type"]
                        except: type="другое"
                        try:age=dd["program"]["age"]
                        except: age="0"
                        try:
                            d2=dd["program"]["media"]
                            img = d2["img"].replace("middle","orig").replace(" http:////","//").replace("//",'/')
                        except:
                            img=""
                        if torr2xbmc.__addon__.getSetting('description') == 'false':
                            if d2["description"] == "":description = ""
                            else:description = d2["description"] + chr(10)
                        else:
                            description = ""
                        plt = plt +"[B][COLOR FF0084FF]"+ s_time+"[/COLOR] [COLOR FFFFFFFF]"+"[B][COLOR FF0084FF]"+"-"+"[/COLOR] [COLOR FFFFFFFF]"+"[B][COLOR FF0084FF]"+ f_time+"[/COLOR] [COLOR FFFFFFFF]"+title_pr+"[/COLOR][/B][COLOR FF999999]"+chr(10)+description+"[/COLOR]"
                    except Exception, e:
                        type=""
                        img=""
                        description=""
                        plt = plt +"[B][COLOR FF0084FF]"+ s_time+"[/COLOR] [COLOR FFFFFFFF]"+"[B][COLOR FF0084FF]"+"-"+"[/COLOR] [COLOR FFFFFFFF]"+"[B][COLOR FF0084FF]"+ f_time+"[/COLOR] [COLOR FFFFFFFF]"+title_pr+"[/COLOR][/B][COLOR FF999999]"+chr(10)+description+"[/COLOR]"
                else:
                    plt = plt +"[B][COLOR FF0084FF]"+ s_time+"[/COLOR] [COLOR FFFFFFFF]"+"[B][COLOR FF0084FF]"+"-"+"[/COLOR] [COLOR FFFFFFFF]"+"[B][COLOR FF0084FF]"+ f_time+"[/COLOR] [COLOR FFFFFFFF]"+ title_pr +"[/COLOR][/B]"+chr(10)
                p_list.append({"start": start_t, "finish": finish_t, "s_time": s_time, "f_time": f_time, title_pr: title_pr, "type":type2, "age":age})
        try:
            rez[idch]={"plot":plt, "img":img, "ico":logo, "genre": type, "year":finish.tm_year, "mpaa":str(age)+"+","p_list":p_list}
        except Exception, e:
            print e
            pass
        return rez
    
def GetPrDay(ncl):
        #print "запрос стр"
        d=updday(ncl)
        rez={}
        #print "обработка"
        for i in d:
            Title = i
            plot = ""
            k=0
            for j in d[i]:
                k+=1
                if k==1:
                    id=j[0].replace("http://m.tv.yandex.ru/","").replace("/program/","").replace("/event/","")
                    try:
                        dd=get_inf_db(id)[0][0].replace("#z","\\").replace("#y",'"')
                        d2=eval(dd)
                        img=d2["img"].replace("middle","orig")
                        pl=d2["pl"]
                        ico=d2["ico"]
                        plot = plot +"[B][COLOR FF0084FF]"+ j[1]+"[/COLOR] [COLOR FFFFFFFF]"+j[2]+"[/COLOR][/B][COLOR FF999999]"+chr(10)+pl+"[/COLOR]"+chr(10)
                    except: 
                        img=""
                        pl=""
                        ico=""
                        plot = plot +"[B][COLOR FF0084FF]"+ j[1]+"[/COLOR] [COLOR FFFFFFFF]"+j[2]+"[/COLOR][/B]"+chr(10)
                else:
                    plot = plot +"[B][COLOR FF0084FF]"+ j[1]+"[/COLOR] [COLOR FFFFFFFF]"+j[2]+"[/COLOR][/B]"+chr(10)
            rez[i]={"plot":plot, "img":img, "ico":ico}
        #print "возврат"
        return rez


def GetLastUpdate():
    c = db.connect(database=db_name)
    cu = c.cursor()
    cu.execute("CREATE TABLE IF NOT EXISTS table1 (db_item VARCHAR(250), i VARCHAR(30), t TIME);")
    c.commit()
    cu.execute("CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, lastupdate  datetime);")
    c.commit()
    cu.execute('SELECT lastupdate FROM settings WHERE id = 1')
    res = cu.fetchone()
    if res == None:
        c.close()
        return None
    else:
        try:
            dt = datetime.datetime.fromtimestamp(time.mktime(time.strptime(res[0], '%Y-%m-%d %H:%M:%S.%f')))
            c.close()
            return dt
        except:
            dt = datetime.datetime.now()- datetime.timedelta(hours = 23)
            c.close()
            return dt
    return None


def GetUpdateProg():
    lupd = GetLastUpdate()
    global c
    global cu
    if lupd == None:
        try:
            cu.execute('INSERT INTO settings (id, lastupdate) VALUES (1, "%s");' % datetime.datetime.now())
            c.commit()
        except Exception, e:
            print e
    else:
        nupd = lupd + datetime.timedelta(hours = 12)
        if nupd < datetime.datetime.now():
            print 'remove db'
            try:
                try:
                    c.close()
                    os.remove(db_name)
                except Exception, e:
                    print 'Не удалось удалить старую БД программы: '+ str(e)
                    return
                c = db.connect(database=db_name)
                cu = c.cursor()
                cu.execute("CREATE TABLE IF NOT EXISTS table1 (db_item VARCHAR(250), i VARCHAR(30), t TIME);")
                c.commit()
                cu.execute("CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, lastupdate  datetime);")
                c.commit()
                cu.execute('INSERT INTO settings (id, lastupdate) VALUES (1, "%s");' % datetime.datetime.now())
                c.commit()
            except Exception, e:
                print 'Ошибка: ' + str(e)
                return

def add_to_db2(n, item):
		tor_id="n"+n
		cu.execute('INSERT INTO table1 (db_item, i, t) VALUES ("'+item+'", "'+tor_id+'", "'+str(time.time())+'");')
		c.commit()

def clean_db():
	tm=str(time.time()-(5*3600))
	cu.execute('SELECT * FROM table1 WHERE t < '+tm+';')
	c.commit()
	L=cu.fetchall()
	for i in L:
		#print i[1]
		id=i[1]
		cu.execute("DROP TABLE IF EXISTS "+id+";")
		c.commit()
	cu.execute("DELETE FROM table1 WHERE t < "+tm+";")
	c.commit()
	cu.execute("VACUUM")
	c.commit()


def save_cache(item):
	print "save cache"
	s="YAcache="+item
	path=ru(os.path.join(addon.getAddonInfo('path'),"lib"))
	fl = open(os.path.join( path ,"cache.py"), "w")
	fl.write("# -*- coding: utf-8 -*-"+chr(10))
	fl.write(s)
	fl.close()

def save_cache_off(item):
		item=item.replace("\\","#z").replace('"',"#y")
		cu.execute("DROP TABLE IF EXISTS table2;")
		c.commit()
		cu.execute("CREATE TABLE IF NOT EXISTS table2 (db_item VARCHAR(250), t TIME);")
		c.commit()
		cu.execute('INSERT INTO table2 (db_item, t) VALUES ("'+item+'", "'+str(time.time())+'");')
		c.commit()

def get_cache_off():
	try:
		cu.execute(str('SELECT db_item FROM table2;'))
		c.commit()
		print "читаем"
		infos = cu.fetchall()[0][0]
		print "замена"
		infos = infos.replace("#z","\\").replace("#y",'"')
		print "преобразуем"
		info  = eval(infos)
		
	except: 
		info = None
		print "get_cache err"
	print "передача из бд"
	return info

from cache import*
def get_cache():
	return YAcache

def add_to_db(n, item):
		err=0
		tor_id="n"+n
		litm=str(len(item))
		try:
			cu.execute("CREATE TABLE "+tor_id+" (db_item VARCHAR("+litm+"), i VARCHAR(1));")
			c.commit()
		except: err=1
			#print "Ошибка БД"
		if err==0:
			cu.execute('INSERT INTO '+tor_id+' (db_item, i) VALUES ("'+item+'", "1");')
			c.commit()
			cu.execute('INSERT INTO table1 (db_item, i, t) VALUES ("'+tor_id+'", "'+tor_id+'", "'+str(time.time())+'");')
			c.commit()
			#c.close()
			
def get_inf_db(n):
		tor_id="n"+n
		cu.execute(str('SELECT db_item FROM '+tor_id+';'))
		c.commit()
		info = cu.fetchall()
		#c.close()
		return info
		


def updb_fast_off():
		#print "---Начинаем обновление ---"
		d=upd3("193", "146")
		for i in d:
					j = d[i][0]
					id=j[0].replace("http://m.tv.yandex.ru/","").replace("/program/","").replace("/event/","")
					try: d2=eval(get_inf_db(id)[0][0].replace("#z","\\").replace("#y",'"'))
					except:
						d2=upd2(j[0])
						xbmc.sleep(300)
						#print repr(d2).replace("\\","#z").replace('"',"#y")
						add_to_db(id, repr(d2).replace("\\","#z").replace('"',"#y"))
		#print "---Быстрое обновление завершено---"
		clean_db()

def updb_fast(n=0):
        try:
            d=get_cache()["channels"]
            print 'upd_fast_on: ' + str(n)
        except: return {}
        for i in d:
            try:
                d2=d[i]
                d3=d2["schedule"][n]# 0 - только 1 передачу
                program=d3["id"]#["program"]
                event=d3["eventId"]
                id=program+event
                if xbmc.abortRequested: break
                else:
                    try:
                        d4=eval(get_inf_db(id)[0][0].replace("#z","\\").replace("#y",'"'))
                        #print "есть в базе"
                    except:
                        d4=upd22(d3)
                        xbmc.sleep(250)
                        try:
                            add_to_db(id, d4.replace("\\","#z").replace('"',"#y"))
                            #print "добавлен"
                        except Exception, e:
                            print "ошибка: "+str(e)
            except:pass

                
def updb():
		try:d=get_cache()["channels"]
		except: return {}
		for i in d:
			try:
				d2=d[i]
				dd=d2["schedule"]
				for d3 in dd:
					#d3=d2["schedule"][0]# 0 - только 1 передачу
					program=d3["id"]#["program"]
					event=d3["eventId"]
					id=program+event
					#print id
					try: 
						d4=eval(get_inf_db(id)[0][0].replace("#z","\\").replace("#y",'"'))
						print "есть в базе"
					except:
						d4=upd22(d3)
						xbmc.sleep(250)
						add_to_db(id, d4.replace("\\","#z").replace('"',"#y"))
						print "добавлен"
			except: pass

def updb_off():
		d=upd3("193", "146")
		n=0
		for i in d:
			n+=1
			#if n==30: print "ОБНОВЛЕНО 20%"
			#if n==120: print "ОБНОВЛЕНО 40%"
			#if n==180: print "ОБНОВЛЕНО 60%"
			#if n==240: print "ОБНОВЛЕНО 80%"
			for j in d[i]:
					id=j[0].replace("http://m.tv.yandex.ru/","").replace("/program/","").replace("/event/","")
					try: d2=eval(get_inf_db(id)[0][0].replace("#z","\\").replace("#y",'"'))
					except: 
						d2=upd2(j[0])
						xbmc.sleep(400)
						add_to_db(id, repr(d2).replace("\\","#z").replace('"',"#y"))
		#print "---Обновление завершено---"

#upd12(0, 0)