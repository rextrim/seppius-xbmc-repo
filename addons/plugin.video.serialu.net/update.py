
import xbmc,xbmcgui
import urllib2, urllib, re, cookielib, sys, time, md5, os
from datetime import date

import HTMLParser
hpar = HTMLParser.HTMLParser()

# load XML library
sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
from ElementTree  import Element, SubElement, ElementTree

today = date.today()
path = os.path.join(os.getcwd(), r'resources', r'data')

#---------- get serials info and save to XML --------------------------------------------------
def Update_Serial_XML(mode):
    #show Dialog
    dp = xbmcgui.DialogProgress()

    if mode == 'UPDATE':
        #load current serial list
        try:
            tree = ElementTree()
            tree.parse(os.path.join(path, r'serials.xml'))
            xml1 = tree.getroot()
            xml1.find("LAST_UPDATE").text = today.isoformat()
            xml  = xml1.find('SERIALS')
            dp.create("Update SERIALU.NET Info")
        except:
            # create XML structure
            xml1 = Element("SERIALU_NET")
            SubElement(xml1, "LAST_UPDATE").text = today.isoformat()
            xml = SubElement(xml1, "SERIALS")
            dp.create("Reload SERIALU.NET Info")
    else:
        # create XML structure
        xml1 = Element("SERIALU_NET")
        SubElement(xml1, "LAST_UPDATE").text = today.isoformat()
        xml = SubElement(xml1, "SERIALS")
        dp.create("Reload SERIALU.NET Info")

    # grab serial's info from site
    url='http://serialu.net'
    count = 0

    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()

    match=re.compile('<div class=".s-name">(.+?)</div><div class="c-content">(.+?)</div>', re.MULTILINE|re.DOTALL).findall(link)

    if len(match) == 0:
		xbmc.log('ПОКАЗАТЬ НЕЧЕГО')
		return False

    for rec in match:
        #xbmc.log(rec[1])
        video=re.compile('<a href="(.+?)">(.+?)</a><br/>', re.MULTILINE).findall(rec[1])
        if len(video) > 0:
            # create serial type in XML
            xml_serial_type_hash = 'st_'+md5.md5(rec[0]).hexdigest()
            # check if type exists
            xml_serial_type = xml.find(xml_serial_type_hash)
            if xml_serial_type is None:
                xml_serial_type = SubElement(xml, xml_serial_type_hash)
                xml_serial_type.text = unescape(rec[0])
            count = 0
            # get info for each serial in type
            for vr in video:
                if (dp.iscanceled()): return
                xml_serial_hash = 's_'+md5.md5(vr[1]).hexdigest()
                #check if serial info exists
                if xml.find(xml_serial_type_hash).find(xml_serial_hash) is not None:
                    count = count + 1
                    percent = min((count*100)/2000, 100)
                    dp.update(0, rec[0], 'Loaded: '+str(count),vr[1])
                    continue
                #get serial detail info
                (i_name, i_year, i_genre, i_director, i_text, i_image, i_season) = Get_Serial_Info(vr[0])
                # create serial record in XML
                xml_serial = SubElement(xml_serial_type, xml_serial_hash)
                xml_serial.text = unescape(vr[1])
                SubElement(xml_serial, "name").text     = i_name
                SubElement(xml_serial, "url").text      = vr[0]
                SubElement(xml_serial, "year").text     = i_year
                SubElement(xml_serial, "genre").text    = i_genre
                SubElement(xml_serial, "director").text = i_director
                SubElement(xml_serial, "text").text     = i_text
                SubElement(xml_serial, "img").text      = i_image
                # update progress bar
                count = count + 1
                #percent = min((count*100)/2000, 100)
                dp.update(0, rec[0], 'Loaded: '+str(count),vr[1])

                # if serial has additional pages
                if len(i_season) > 0:
                    for url1 in i_season:
                        if (dp.iscanceled()): return
                        if url1 != vr[0]:
                            xml_serial_hash = 's_'+md5.md5(url1[1]).hexdigest()
                            #check if serial info exists
                            if xml.find(xml_serial_type_hash).find(xml_serial_hash) is not None:
                                count = count + 1
                                percent = min((count*100)/2000, 100)
                                dp.update(0, rec[0], 'Loaded: '+str(count),vr[1])
                                continue
                            # get serial detail info
                            (i_name, i_year, i_genre, i_director, i_text, i_image, i_season) = Get_Serial_Info(url1[0])
                            # create serial record in XML
                            xml_serial = SubElement(xml_serial_type, xml_serial_hash)
                            xml_serial.text = unescape(url1[1])
                            SubElement(xml_serial, "name").text     = i_name
                            SubElement(xml_serial, "url").text      = url1[0]
                            SubElement(xml_serial, "year").text     = i_year
                            SubElement(xml_serial, "genre").text    = i_genre
                            SubElement(xml_serial, "director").text = i_director
                            SubElement(xml_serial, "text").text     = i_text
                            SubElement(xml_serial, "img").text      = i_image
                            # update progress bar
                            count = count + 1
                            percent = min((count*100)/2000, 100)
                            dp.update(0, rec[0], 'Loaded: '+str(count),url1[1])

    dp.close()
    ElementTree(xml1).write(os.path.join(path, r'\serials.xml'), encoding='utf-8')

#---------- get serial info ----------------------------------------------------
def Get_Serial_Info(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    # get info section
    i_body = re.compile('<div class="content">(.+?)Смотреть.+ онлайн', re.MULTILINE|re.DOTALL).findall(link)
    i_body[0] = i_body[0]+'<'
    # get searial info
    name    =re.compile('<strong>Оригинальное название:</strong>(.+?)<br />', re.MULTILINE|re.DOTALL).findall(i_body[0])
    year    =re.compile('<strong>Год выхода на экран:</strong>(.+?)<br />', re.MULTILINE|re.DOTALL).findall(i_body[0])
    country =re.compile('<strong>Страна:</strong>(.+?)<br />', re.MULTILINE|re.DOTALL).findall(i_body[0])
    genre   =re.compile('<strong>Сериал относится к жанру:</strong>(.+?)<br />', re.MULTILINE|re.DOTALL).findall(i_body[0])
    director=re.compile('<strong>Постановщик</strong>(.+?)<br />', re.MULTILINE|re.DOTALL).findall(i_body[0])
    text    =re.compile('<strong>Краткое описание:</strong>(.+?)<', re.MULTILINE|re.DOTALL).findall(i_body[0].replace('<p>', '').replace('</p>',''))
    img     =re.compile('src="(.+?)"', re.MULTILINE|re.DOTALL).findall(i_body[0])
    # check for extended links (additional seasons located on different pages)
    season  =re.compile('сезон: <a href="(.+?)">(.+?)</a>', re.MULTILINE|re.DOTALL).findall(i_body[0])

    # fill up data to info array
    if len(name)>0:
        i_name=unescape(name[0])
    else:
        i_name=('-').decode('utf-8')

    if len(year)>0:
        y = year[0].replace(' ', '')

        if not unicode(y[0:4]).isnumeric():
            y = country[0].replace(' ', '')

        try:
            i_year = (y[0:4]).decode('utf-8')
        except:
            i_year = ('-').decode('utf-8')
    else:
        i_year = ('-').decode('utf-8')

    if not i_year.isnumeric():
        i_year = ('-').decode('utf-8')

    if len(genre)>0:
        i_genre=(genre[0]).decode('utf-8')
    else:
        i_genre=('-').decode('utf-8')

    if len(director)>0:
        i_director=(director[0]).decode('utf-8')
    else:
        i_director=('-').decode('utf-8')

    if len(text)>0:
        i_text=unescape(text[0])
    else:
        i_text=('-').decode('utf-8')

    if len(img)>0:
        i_image=img[0]
    else:
        i_image='-'

    return i_name, i_year, i_genre, i_director, i_text, i_image, season
#-------------------------------------------------------------------------------

def unescape(text):
    text = hpar.unescape(text.decode('utf8'))
    return text


#-------------------------------------------------------------------------------

if len(sys.argv) > 1:
    mode = sys.argv[1]
else:
    mode = 'UPDATE'

ret = 'NO'

if mode != 'UPDATE' and mode != 'INFO':
    dialog = xbmcgui.Dialog()
    if dialog.yesno('Внимание!', 'Пересоздание списка сериалов требует','значительного времени (0.5-2 часа).', 'Пересоздать список?'):
        ret = 'YES'
    else:
        ret = 'NO'

if mode == 'UPDATE' or ret == 'YES':
    Update_Serial_XML(mode)
else:
    if mode == 'INFO':
        dialog = xbmcgui.Dialog()
        tree = ElementTree()
        tree.parse(os.path.join(path, r'serials.xml'))
        dialog.ok('Информация', sys.version, 'Список сериалов создан: ' + tree.getroot().find('LAST_UPDATE').text)

