# -*- coding: utf-8 -*-
__author__ = 'DiMartino'
import urllib, urllib2, re, sys, os, json, difflib, cookielib
import xbmc
import cPickle
from BeautifulSoup import BeautifulSoup
from functions import Debug,cutFileNames,filename2match

site_url='http://cxz.to'
User_Agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0'
addon_name     = sys.argv[0].replace('plugin://', '')
addon_data_path = xbmc.translatePath(os.path.join("special://profile/addon_data", addon_name))
addon_path = xbmc.translatePath(os.path.join("special://home/addons", addon_name))
if (sys.platform == 'win32') or (sys.platform == 'win64'):
    addon_data_path = addon_data_path.decode('utf-8')
    addon_path      = addon_path
addon_ico = addon_path+'icon.png'
cookie_path =addon_data_path+'cookie'

SCORE_PENALTY_ITEM_ORDER = 10
SCORE_PENALTY_YEAR = 30
SCORE_PENALTY_TITLE = 40

if (sys.platform == 'win32') or (sys.platform == 'win64'):
    addon_data_path = addon_data_path.decode('utf-8')

def Get_url(url, headers={}, Post = None, GETparams={}, JSON=False, Proxy=None, Cookie=False, User_Agent= User_Agent):

    h=[]
    if Proxy:
        (urllib2.ProxyHandler({'http': Proxy}))
    if Cookie:
        if not os.path.exists(os.path.dirname(addon_data_path)):
                os.makedirs(os.path.dirname(addon_data_path))
        cookie = cookielib.LWPCookieJar(cookie_path)
        if os.path.exists(cookie_path):
            cookie.load()
        h.append(urllib2.HTTPCookieProcessor(cookie))
    if h:
        opener = urllib2.build_opener(*h)
        if User_Agent: opener.addheaders = [('User-agent', User_Agent)]
        urllib2.install_opener(opener)

    if GETparams:
        url = "%s?%s" % (url, urllib.urlencode(GETparams))

    if Post:
        Post = urllib.urlencode(Post)

    req = urllib2.Request(url, Post)
    if User_Agent: req.add_header("User-Agent", User_Agent)
    for key, val in headers.items():
        req.add_header(key, val)

    try:
        response = urllib2.urlopen(req)
        Data=response.read()
        if response.headers.get("Content-Encoding", "") == "gzip":
            import zlib
            Data = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(Data)
    except Exception, e:
        print(' ОШИБКА'+str(e))
        return None
    response.close()
    if JSON:
        import json
        try:
            js = json.loads(Data)
        except Exception, e:
            print(' ОШИБКА'+str(e))
            return None
        Data = js
    if Cookie: cookie.save()
    return Data

def Content(params,isFolders=False):
    ctitle=''
    cutfilename=None
    if 'title' in params:
        ctitle=urllib.unquote(params['title'])
    if 'cutfilename' in params:
        cutfilename=urllib.unquote(params['cutfilename'])
    href=urllib.unquote(params['href'])

    url=site_url+href+'?ajax'

    query={}
    rlist=[]
#    query['download']='1'
#    query['view']='1'
#    query['view_embed']='0'
#    query['blocked']='0'
#    query['folder_quality']='null'
#    query['folder_lang']='null'
#    query['folder_translate']='null'
    try:
        query['folder']=params['rel']
        season=params['season']
    except:
        query['folder']='0'
        season='0'

    for qr in query:
        url+='&'+qr+'='+query[qr]

    Data =Get_url(url, Cookie=True)
    Soup = BeautifulSoup(Data)

    li = Soup.findAll('li', 'folder')

    if isFolders==False:
        for l in li:
            a = l.find('a', 'title')
            title= a.string
            if title==None:
                title = l.find('a', 'title').b.string

            results=re.compile('(\d+) сезон', re.IGNORECASE).findall(title.encode('utf-8'))
            if results:
                season=str(int(results[0]))
            elif query['folder']=='0':
                season='0'

            lang = a['class']
            lang = re.compile('\sm\-(\w+)\s').findall(lang)
            if lang:
                lang=lang[0].upper()+' '
            else:
                lang=''

            rel = re.compile('\d+').findall(a['rel'])[0]
            size = l.findAll('span','material-size')
            sz = size[-1].string.replace('&nbsp;', ' ')

            title = lang+title#+chr(10)
            rlist.append({'rel':rel, 'href':href, 'season':season, 'title':title, 'size':sz})

    else:
        li = Soup.findAll('li', 'b-file-new')
        li2=[]
        filelist=[]
        for l in li:
            try:
                title = l.find('span', 'b-file-new__material-filename-text')
                if title == None:
                    title = l.find('span', 'b-file-new__link-material-filename-text')
                title=title.string
                a= l.find('a', 'b-file-new__link-material')
                href= a['href']
                a= l.find('a', 'b-file-new__link-material-download')
                href_dl = a['href']
                size = a.span.string
                li2.append({'href':href,'title':ctitle+' '+size, 'href_dl':href_dl, 'string':title})
                filelist.append(title)
            except:
                continue

        if len(li2)>0:
            li3=[]
            cutfilelist=[]
            i=-1
            if len(filelist)>2:
                try:
                    cutfilelist=cutFileNames(filelist)
                except:
                    pass
            #print str(cutfilelist)
            for la in li2:
                i=i+1
                if cutfilelist:
                    la['cutfilename']=cutfilelist[i]
                else: la['cutfilename']=None
                li3.append(la)


            for lu in li3:
                lu['episode']=0
                lu['season']=0
                results=filename2match(lu['string'],no_date=True)
                if not results and cutfilename:
                    results=filename2match(cutfilename,no_date=True)
                if results:
                    if season in ['0',0,None]:
                        lu['season']=results['season']
                    else:
                        lu['season']=season
                    lu['episode']=results['episode']

                rlist.append(lu)
    return rlist

def isAsciiString(mediaName):
  """ Returns True if all characters of the string are ASCII.
  """
  for index, char in enumerate(mediaName):
    if ord(char) >= 128:
      return False
  return True

def toInteger(maybeNumber):
  """ Returns the argument converted to an integer if it represents a number
      or None if the argument is None or does not represent a number.
  """
  try:
    if maybeNumber is not None and str(maybeNumber).strip() != '':
      return int(maybeNumber)
  except:
    pass
  return None

def computeTitlePenalty(mediaName, title):
  """ Given media name and a candidate title, returns the title result score penalty.
      @param mediaName Movie title parsed from the file system.
      @param title Movie title from the website.
  """
  mediaName = mediaName.lower()
  try:
      mediaName=mediaName.decode('utf-8')
  except:
      pass
  title = title.lower()
  try:
      title=title.decode('utf-8')
  except:
      pass
  if mediaName != title:
    # First approximate the whole strings.
    diffRatio = difflib.SequenceMatcher(None, mediaName, title).ratio()
    penalty = int(SCORE_PENALTY_TITLE * (1 - diffRatio))

    # If the penalty is more than 1/2 of max title penalty, check to see if
    # this title starts with media name. This means that media name does not
    # have the whole name of the movie - very common case. For example, media name
    # "Кавказская пленница" for a movie title "Кавказская пленница, или Новые приключения Шурика".
    if penalty >= 15: # This is so that we don't have to do the 'split' every time.
      # Compute the scores of the
      # First, check if the title starts with media name.
      mediaNameParts = mediaName.split()
      titleParts = title.split()
      if len(mediaNameParts) <= len(titleParts):
        i = 0
        # Start with some small penalty, value of which depends on how
        # many words media name has relative to the title's word count.
        penaltyAlt = max(5, int(round((1.0 - (float(len(mediaNameParts)) / len(titleParts))) * 15 - 5)))
        penaltyPerPart = SCORE_PENALTY_TITLE / len(mediaNameParts)
        for mediaNamePart in mediaNameParts:
          partDiffRatio = difflib.SequenceMatcher(None, mediaNamePart, titleParts[i]).ratio()
          penaltyAlt = penaltyAlt + int(penaltyPerPart * (1 - partDiffRatio))
          i = i + 1
        penalty = min(penalty, penaltyAlt)
#    print '++++++ DIFF("%s", "%s") = %g --> %d' % (mediaName.encode('utf8'), title.encode('utf8'), diffRatio, penalty)
#    Log.Debug('++++++ DIFF("%s", "%s") = %g --> %d' % (mediaName.encode('utf8'), title.encode('utf8'), diffRatio, penalty))
    return penalty
  return 0

def scoreMediaTitleMatch(mediaName, mediaAltTitle, mediaYear, title, year, itemIndex):

  """ Compares page and media titles taking into consideration
      media item's year and title values. Returns score [0, 100].
      Search item scores 100 when:
        - it's first on the list of results; AND
        - it equals to the media title (ignoring case) OR all media title words are found in the search item; AND
        - search item year equals to media year.

      For now, our title scoring is pretty simple - we check if individual words
      from media item's title are found in the title from search results.
      We should also take into consideration order of words, so that "One Two" would not
      have the same score as "Two One". Also, taking into consideration year difference.
  """
  # add logging that works in unit tests.
#  Log.Debug('comparing item %d::: "%s-%s" with "%s-%s" (%s)...' %
#      (itemIndex, str(mediaName), str(mediaYear), str(title), str(year), str(altTitle)))
  # Max score is when both title and year match exactly.
  score = 100

  # Item order penalty (the lower it is on the list or results, the larger the penalty).
  score = score - (itemIndex * SCORE_PENALTY_ITEM_ORDER)

  # Compute year penalty: [equal, diff>=3] --> [0, MAX].
  yearPenalty = SCORE_PENALTY_YEAR
  mediaYear = toInteger(mediaYear)
  year = toInteger(year)
  if mediaYear is not None and year is not None:
    yearDiff = abs(mediaYear - year)
    if not yearDiff:
      yearPenalty = 0
    elif yearDiff == 1:
      yearPenalty = int(SCORE_PENALTY_YEAR / 4)
    elif yearDiff == 2:
      yearPenalty = int(SCORE_PENALTY_YEAR / 3)
  else:
    # If year is unknown, don't penalize the score too much.
    yearPenalty = int(SCORE_PENALTY_YEAR / 3)
  score = score - yearPenalty

  # Compute title penalty.
  titlePenalty = computeTitlePenalty(mediaName, title)
  altTitlePenalty = 100
  if mediaAltTitle not in [None,'']:
    altTitlePenalty = computeTitlePenalty(mediaAltTitle.encode('utf-8'), title)

  titlePenalty = min(titlePenalty, altTitlePenalty)
  score = score - titlePenalty

  # If the score is not high enough, add a few points to the first result -
  # let's give KinoPoisk some credit :-).
  if itemIndex == 0 and score <= 80:
    score = score + 5

  # IMPORTANT: always return an int.
  score = int(score)
#  Log.Debug('***** title scored %d' % score)
  return score

def cxzEpisodeList(title,ruTitle,year,seasonId,episodeId=None):

    showdata=Search(title,ruTitle,year)

    if not showdata: return

    params={
        'href':showdata['href'],
        'rel':'0'
    }

    episode_list,season_list=[],[]
    show=Content(params)
    #Debug('[cxzEpisodeList][show]:'+str(show))
    for seasons in show:
        if int(seasons['season'])==seasonId:
            #Debug('[cxzEpisodeList][seasons]:'+str(seasons))
            variants=Content(seasons)
            #Debug('[cxzEpisodeList][variants]:'+str(variants))
            for filelist in variants:
                episodes=Content(filelist, True)
                #Debug('[cxzEpisodeList][episodes]:'+str(episodes))
                if episodeId==None and episodes:
                    filelist['title']='%s %s (%d)' % (filelist['title'], filelist['size'], len(episodes))
                    season_list.append(filelist)
                    continue

                for episode in episodes:
                    if episodeId and int(episode['episode'])==episodeId:
                        episode['href']=site_url+episode['href']
                        episode_list.append(episode)


    return episode_list, season_list

def cxzEpisodeListByRel(href,rel,season):

    params={
        'href':href,
        'rel':rel,
        'season':season,
    }

    episode_list=[]
    episodes=Content(params, True)
    Debug('[cxzEpisodeListByRel][episodes]:'+str(episodes))

    for episode in episodes:
        episode['href']=site_url+episode['href']
        episode_list.append(episode)

    return episode_list

def DataCheck(Data):
    NewData=[]
    if Data:
        for show in Data:
            if '/serials/' in show['link'] or '/tvshow/' in show['link'] or '/cartoonserials/' in show['link']:
                NewData.append(show)
    return NewData

def Search(title,ruTitle=None,year=None):
    shows=[]

    try:
        urltitle=urllib.quote_plus(title)
    except:
        urltitle=urllib.quote_plus(title.encode('utf-8'))

    url= site_url+'/search.aspx?f=quick_search&limit=100&section=video&search='+urltitle
    Data =json.loads(Get_url(url))

    Data=DataCheck(Data)

    #print str(Data)+str(len(Data))
    if not Data:
        Data=SearchAssist(title)
        Data=DataCheck(Data)

    if not Data and ruTitle not in [None,'']:
        url= site_url+'/search.aspx?f=quick_search&limit=100&section=video&search='+urllib.quote_plus(ruTitle.encode('utf-8'))
        Data =json.loads(Get_url(url))

        Data=DataCheck(Data)

        #print str(Data)+str(len(Data))
        if not Data:
            Data=SearchAssist(ruTitle)
            Data=DataCheck(Data)

    if not Data: return

    itemIndex=0
    for show in Data:
        itemIndex=itemIndex+1
        Shref  = show['link']
        Syear=show['year'][0]

        Stitle =show['title']

        rate=scoreMediaTitleMatch(title,ruTitle,year, Stitle.encode('utf-8'), Syear, itemIndex)
        shows.append({'rate':rate,'href':Shref, 'title' :Stitle, 'year':Syear})

    shows=sorted(shows, key=lambda x: x['rate'], reverse=True)
    #print str(shows)
    if shows:
        return shows[0]

def Search2(title,ruTitle=None,year=None):
    shows=[]

    url= site_url+'/search.aspx?f=quick_search&limit=100&section=video&search='+urllib.quote_plus(title)
    Data =json.loads(Get_url(url))

    Data=DataCheck(Data)

    #print str(Data)+str(len(Data))
    if not Data:
        Data=SearchAssist(title)
        Data=DataCheck(Data)

    if not Data:
        url= site_url+'/search.aspx?f=quick_search&limit=100&section=video&search='+urllib.quote_plus(ruTitle.encode('utf-8'))
        Data =json.loads(Get_url(url))

        Data=DataCheck(Data)

        #print str(Data)+str(len(Data))
        if not Data:
            Data=SearchAssist(ruTitle)
            Data=DataCheck(Data)

        if not Data: return

    itemIndex=0
    for show in Data:
        itemIndex=itemIndex+1
        Shref  = show['link']
        Syear=show['year'][0]

        Stitle =show['title']
        if '/serials/' in Shref or '/tvshow/' in Shref or '/cartoonserials/' in Shref:
            shows.append({'rate':100,'href':Shref, 'title' :Stitle, 'year':Syear})
            break

    if shows:
        return shows[0]

def SearchAssist(title):
    url= site_url+'/search.aspx?search='+urllib.quote_plus(title)

    Data =Get_url(url)
    shows=[]
    Soup = BeautifulSoup(Data)
    try:
        Sresult = Soup.find('div', 'main')
        Sresult =Sresult.findAll('table', recursive=False)
    except:
        #print ('Ничего не найдено')
        return

    for table in Sresult:
        tr_s = table.findAll('tr', recursive=False)
        for tr in tr_s:
            a = tr.find('a', 'title')
            href  = a['href']
            string = a.string
            year=re.compile('\((\d{4})[-|)]').findall(string)
            if year: year=year[-1]
            Stitle=string.split('/')[0].strip()

            shows.append({'link':href,'year':[year],'title':Stitle})

    return shows

def PlayCXZTO(link):
    try:
        with open(addon_data_path+'/playlist','rb') as F:
            LocalPL = cPickle.load(F)
    except:
        if not os.path.exists(os.path.dirname(addon_data_path)):
                os.makedirs(os.path.dirname(addon_data_path))
        LocalPL={}

    file_id = link.split('=')[1]

    try:
        path = LocalPL[file_id]
    except:
        Data = Get_url(link)
        playlist = re.compile("(?s)playlist:\s*\[\s*\{\s*(.+?)\s*\}\s*\]").findall(Data)
        if not playlist: return
        playlist= playlist[0].replace('\n','').replace('\t','').replace(' ','').replace('download_url','')
        urls = re.compile("url:'([^']+).+?file_id:'([^']+)").findall(playlist)
        if not urls:return
        pl={}
        for i in urls:
            pl[i[1]]= site_url+i[0]
        with open(addon_data_path+'/playlist','wb') as F:
            cPickle.dump(pl,F)
        path = pl[file_id]

    return path

#print str(cxzEpisodeList(u'Fridge',u'Грань',u'2008',5,4))
def test():
    dirx='C:\\Users\\Admin\\AppData\\Roaming\\XBMC\\cache\\xbmcup\\plugin.video.myshows\\'
    dirlist=os.listdir(dirx)
    i=0
    j=7*10
    for showId in dirlist:
        i=i+1
        if i>7+j and i<15+j:
            showslisttxt=file(dirx+showId)

            showslist=json.load(showslisttxt)
            print showslist['title']+' ('+str(showslist['year'])+') '+showslist['ruTitle']

            S1=(Search(showslist['title'].encode('utf-8'),showslist['ruTitle'],showslist['year']))
            S2=(Search2(showslist['title'].encode('utf-8'),showslist['ruTitle'],showslist['year']))

            if not S1 or not S2:
                print showslist['title']+' ('+str(showslist['year'])+')'+' '+str(S1)+' '+str(S2)
                continue

            if S1['href']!=S2['href']:
                print showslist['title']+' ('+str(showslist['year'])+')'+' '+S1['href']+' '+S2['href']