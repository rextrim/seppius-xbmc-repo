
import xbmc,xbmcgui
import urllib2, urllib, re, cookielib, sys, time, md5, os
from datetime import date

import HTMLParser
hpar = HTMLParser.HTMLParser()

import traceback
def formatExceptionInfo(maxTBlevel=5):
     cla, exc, trbk = sys.exc_info()
     excName = cla.__name__
     try:
         excArgs = exc.__dict__["args"]
     except KeyError:
         excArgs = "<no args>"
     excTb = traceback.format_tb(trbk, maxTBlevel)
     return (excName, excArgs, excTb)

# load XML library
sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
from ElementTree  import Element, SubElement, ElementTree

today = date.today()
path = os.path.join(os.getcwd(), r'resources', r'data')

#---------- get movies info and save to XML --------------------------------------------------
def Update_Movie_XML(mode):
    #show Dialog
    dp = xbmcgui.DialogProgress()

    if mode == 'UPDATE':
        #load current serial list
        try:
            tree = ElementTree()
            tree.parse(os.path.join(path, r'movies.xml'))
            xml1 = tree.getroot()
            xml1.find("LAST_UPDATE").text = today.isoformat()
            movies  = xml1.find('MOVIES')
            types   = xml1.find('TYPES')
            dp.create("Update IGRU.NET.UA Info")
        except:
            # create XML structure
            xml1 = Element("IGRU_NET_UA")
            SubElement(xml1, "LAST_UPDATE").text = today.isoformat()
            movies  = SubElement(xml1, "MOVIES")
            types   = SubElement(xml1, "TYPES")
            dp.create("Reload IGRU.NET.UA Info")
    else:
        # create XML structure
        xml1 = Element("IGRU_NET_UA")
        SubElement(xml1, "LAST_UPDATE").text = today.isoformat()
        movies  = SubElement(xml1, "MOVIES")
        types   = SubElement(xml1, "TYPES")
        dp.create("Reload IGRU.NET.UA Info")

    # grab serial's info from site
    url='http://igru.net.ua/'
    count = 0

    # get all movie types
    Get_Type(url, types)

    # get all movies for each movie type
    for rec in types:
        if (dp.iscanceled()): return
        movie_found = 0
        page_num = Get_Type_Page_Number(rec.find('url').text)
        for count in range(1, page_num+1):
            movie_found = Get_Film_Info(rec.find('url').text+'/page/'+str(count)+'/', movies, rec, dp, movie_found)

    # order sort movies by names
    movies[:] = sorted(movies, key=getkey)

    dp.close()
    ElementTree(xml1).write(os.path.join(path, r'\movies.xml'), encoding='utf-8')

#--- get movies categories -----------------------------------------------------
def Get_Type(url, types):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()

    ret = 1

    match=re.compile('<h2 class="widgettitle">Рубрики</h2>.+<div class="textwidget"><ul>(.+?)</div>', re.MULTILINE|re.DOTALL).findall(link)

    page=re.compile('<a href="(.+?)" title="(.+?)">(.+?)</a>', re.MULTILINE|re.DOTALL).findall(match[0])

    for rec in page:
        is_retro   = len(re.compile('/category/retro-onlajn/.+/', re.MULTILINE|re.DOTALL).findall(rec[0]))
        is_film    = len(re.compile('/category/filmy-onlajn/.+/', re.MULTILINE|re.DOTALL).findall(rec[0]))
        is_doc     = len(re.compile('/dokumentalnoe-kino/', re.MULTILINE|re.DOTALL).findall(rec[0]))

        if is_retro > 0 or is_film > 0 or is_doc > 0:
            if is_retro > 0:
                name = ('Ретро: ')+ rec[2]
            else:
                name = rec[2]

            #-- store movie's category in XML
            xml_type_hash = 'st_'+md5.md5(name).hexdigest()
            # check if type exists
            if types.find(xml_type_hash) is None:
                type = SubElement(types, xml_type_hash)
                SubElement(type, "name").text = unescape(name)
                SubElement(type, "url").text  = unescape(rec[0])

#--- get number of pages for selected category ---------------------------------
def Get_Type_Page_Number(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()

    ret = 1

    match=re.compile('<div class="wp-pagenavi">(.+?)</div>', re.MULTILINE|re.DOTALL).findall(link)

    page=re.compile('<a href="(.+?)/page/(.+?)</a>', re.MULTILINE|re.DOTALL).findall(match[0])

    for rec in page:
        v = re.compile('(.+?)/" title="(.+?)"', re.MULTILINE|re.DOTALL).findall(rec[1])
        if len(v) > 0:
            if ret < int(v[0][0]):
                ret = int(v[0][0])

    return ret

#--- get movie info for selected page in category ------------------------------
def Get_Film_Info(url, movies, cur_type, dp, movie_found):
    cur_type_hash = cur_type.tag
    cur_type_name = cur_type.find('name').text

    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    try:
        link=response.read()
    except:
        time.sleep(5)
        link=response.read()

    response.close()

    match=re.compile('<h2><a href="(.+?)" rel="bookmark"(.+?)<div class="tags">', re.MULTILINE|re.DOTALL).findall(link)

    for rec in match:
        if (dp.iscanceled()): return
        try:
            i_url         = rec[0]
            rec = rec[1]+'</end>'
            #get genre
            genre = ''
            genre_body = re.compile('<div class="cat">Категория (.+?)</div>', re.MULTILINE|re.DOTALL).findall(rec)
            genre_list = re.compile('<a href="(.+?)" title="(.+?)" rel="category tag">(.+?)</a>', re.MULTILINE|re.DOTALL).findall(genre_body[0])
            for g in genre_list:
                if len(re.compile('Фильмы онлайн').findall(g[2])) == 0 and len(re.compile('Ретро онлайн').findall(g[2])) == 0:
                    if genre != '':
                        genre = genre +', '
                    genre = genre + g[2]
            # get movie info
            image_body  = re.compile('<img (.+?)/>', re.MULTILINE|re.DOTALL).findall(rec)
            image_img   = re.compile('src="(.+?)"', re.MULTILINE|re.DOTALL).findall(image_body[0])
            if len(image_img) == 0:
                image_img   = re.compile('SRC="(.+?)"', re.MULTILINE|re.DOTALL).findall(image_body[0])
            image_name  = re.compile('title="(.+?)".*</h2>', re.MULTILINE|re.DOTALL).findall(rec)
            if len(image_name) == 0:
                image_name  = re.compile('alt="(.+?)"', re.MULTILINE|re.DOTALL).findall(image_body[0])
                if len(image_name) == 0:
                    image_name  = re.compile('ALT="(.+?)"', re.MULTILINE|re.DOTALL).findall(image_body[0])
            image_name1 = re.compile('Просмотр фильма (.+?) онлайн', re.MULTILINE|re.DOTALL).findall(image_name[0])
            if len(image_name1)>0:
                image_name = image_name1
            image_name1 = re.compile('Просмотр мультфильма (.+?) онлайн', re.MULTILINE|re.DOTALL).findall(image_name[0])
            if len(image_name1)>0:
                image_name = image_name1
            image_name1 = re.compile('ссылка на (.+?) онлайн', re.MULTILINE|re.DOTALL).findall(image_name[0])
            if len(image_name1)>0:
                image_name = image_name1


            origin_name = re.compile('<strong>Оригинальное название:</strong> (.+?)<br />', re.MULTILINE|re.DOTALL).findall(rec)
            year        = re.compile('<strong>Год выхода на экран:</strong> (.+?)<br />', re.MULTILINE|re.DOTALL).findall(rec)
            director    = re.compile('<strong>Постановщик.*</strong> (.+?)<br />', re.MULTILINE|re.DOTALL).findall(rec)
            actors      = re.compile('<strong>Актеры, принявшие участие в съемках:</strong> (.+?)</p>', re.MULTILINE|re.DOTALL).findall(rec)
            text        = re.compile('<strong>Краткое описание:</strong> (.+?)Скачать фильм можно здесь', re.MULTILINE|re.DOTALL).findall(rec)
            if len(text) == 0:
                text        = re.compile('<strong>Краткое описание:</strong> (.+?)Смотреть .+ онлайн', re.MULTILINE|re.DOTALL).findall(rec)
                if len(text) == 0:
                    text = re.compile('<strong>Краткое описание:</strong> (.+?)</end>', re.MULTILINE|re.DOTALL).findall(rec)

            # parse movie info
            if len(image_name)>0:
                i_name  = unescape(image_name[0])
                i_image = image_img[0]
            else:
                i_name  = ('').decode('utf-8')
                i_image = ('').decode('utf-8')

            if len(origin_name)>0:
                o_name=unescape(origin_name[0])
            else:
                o_name=('').decode('utf-8')

            if len(year)>0:
                i_year=unescape(year[0])
            else:
                i_year=('').decode('utf-8')

            if len(director)>0:
                i_director=unescape(director[0])
            else:
                i_director=('').decode('utf-8')

            if len(actors)>0:
                i_actors=unescape(actors[0])
            else:
                i_actors=('').decode('utf-8')

            if len(text)>0:
                i_text=unescape(text[0])
            else:
                i_text=('').decode('utf-8')

            full_text = i_text.replace('<p>', '').replace('</p>', '')
            if o_name != '':
                full_text = full_text+('\nОригинальное название: ').decode('utf-8')+o_name
            if i_actors != '':
                full_text = full_text+('\nАктеры: ').decode('utf-8')+i_actors

            # add info to XML
            if len(image_name) > 0:
                xml_movie_hash = 'mov_'+md5.md5(image_name[0] + i_year.encode('utf-8')).hexdigest()
                #check if movie info exists
                xml_movie = movies.find(xml_movie_hash)
                if xml_movie is None:   #-- create new record
                    # create serial record in XML
                    xml_movie = SubElement(movies, xml_movie_hash)
                    xml_movie.text = i_name
                    SubElement(xml_movie, "name").text     = i_name
                    SubElement(xml_movie, "url").text      = i_url
                    SubElement(xml_movie, "year").text     = i_year
                    SubElement(xml_movie, "genre").text    = unescape(genre)
                    SubElement(xml_movie, "director").text = i_director
                    SubElement(xml_movie, "text").text     = full_text
                    SubElement(xml_movie, "img").text      = i_image
                    SubElement(xml_movie, "categories")
                    # update found movies counter
                    movie_found = movie_found + 1
                # add movie category info
                cat = xml_movie.find("categories")
                if cat.find(cur_type_hash) is None:
                    SubElement(cat, cur_type_hash)
                # update info in progress dialog
                dp.update(0, cur_type_name, 'Loaded: '+str(movie_found), i_name)
        except:
            xbmc.log(formatExceptionInfo())

    return movie_found

#-------------------------------------------------------------------------------

def unescape(text):
    text = hpar.unescape(text.decode('utf8'))
    return text

def getkey(elem):
    return elem.findtext("name")


#-------------------------------------------------------------------------------

if len(sys.argv) > 1:
    mode = sys.argv[1]
else:
    mode = 'UPDATE'

ret = 'NO'

if mode != 'UPDATE' and mode != 'INFO':
    dialog = xbmcgui.Dialog()
    if dialog.yesno('Внимание!', 'Пересоздание списка фильмов требует','значительного времени (0.5-2 часа).', 'Пересоздать список?'):
        ret = 'YES'
    else:
        ret = 'NO'

if mode == 'UPDATE' or ret == 'YES':
    Update_Movie_XML(mode)
else:
    if mode == 'INFO':
        dialog = xbmcgui.Dialog()
        tree = ElementTree()
        tree.parse(os.path.join(path, r'movies.xml'))
        dialog.ok('Информация', ' ', 'Список фильмов создан: ' + tree.getroot().find('LAST_UPDATE').text)


