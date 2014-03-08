import sys
import urllib
from urllib import unquote_plus
from urllib2 import Request, URLError, urlopen as urlopen2
from urlparse import parse_qs
try:
    import simplejson as json
except ImportError:
    import json

import urllib2, re

VIDEO_FMT_PRIORITY_MAP = {
        '121': 1, #"hd1080"
        '37' : 2, #"1080p h264 mp4 container"
        '120': 3, #"hd720"
        '102': 4, #"720p vp8 webm stereo"
        '84' : 5, #"720p h264 stereo"
        '45' : 6, #"720p vp8 webm container"
        '45' : 7, #"720p vp8 webm container"
        '38' : 8, #"720p vp8 webm container"
        '22' : 9, #"720p h264 mp4 container"
        '85' : 10, #"520p h264 stereo"
        '46' : 11, #"520p vp8 webm stereo"
        '101': 12, #"480p vp8 webm stereo"
        '44' : 13, #"480p vp8 webm container"
        '100': 17, #"360p vp8 webm stereo"
        '82' : 18, #"360p h264 stereo"
        '18' : 19, #"360p h264 mp4 container"
        '83' : 20, #"240p h264 stereo"
        '36' : 21, #MP4 180p
        '17' : 22, #MP4 144p
}

VIDEO_FMT_NAME = {
        36 : "mp4 180p",
        17 : "mp4 144p",
        18: "mp4 360p",
        22: "mp4 720p",
        37: "mp4 1080p",
        38: "vp8 720p",
        44: "vp8 480p",
        45: "vp8 720p",
        46: "vp8 520p",
        82: "h264 360p",
        83: "h264 240p",
        84: "h264 720p",
        85: "h264 520p",
        100: "vp8 360p",
        101: "vp8 480p",
        102: "vp8 720p",
        120: "mp4 hd720",
        121: "mm4 hd1080"
 }

def printDBG(s):
    print s

class CVevoSignAlgoExtractor():
    MAX_REC_DEPTH = 5

    def __init__(self):
        self.algoCache = {}
        self._cleanTmpVariables()

    def _cleanTmpVariables(self):
        self.fullAlgoCode = ''
        self.allLocalFunNamesTab = []
        self.playerData = ''

    def _jsToPy(self, jsFunBody):
        pythonFunBody = jsFunBody.replace('function', 'def').replace('{', ':\n\t').replace('}', '').replace(';', '\n\t').replace('var ', '')
        pythonFunBody = pythonFunBody.replace('.reverse()', '[::-1]')
        lines = pythonFunBody.split('\n')
        for i in range(len(lines)):
            match = re.search('(\\w+?)\\.split\\(""\\)', lines[i])
            if match:
                lines[i] = lines[i].replace(match.group(0), 'list(' + match.group(1) + ')')
            match = re.search('(\\w+?)\\.length', lines[i])
            if match:
                lines[i] = lines[i].replace(match.group(0), 'len(' + match.group(1) + ')')
            match = re.search('(\\w+?)\\.slice\\(([0-9]+?)\\)', lines[i])
            if match:
                lines[i] = lines[i].replace(match.group(0), match.group(1) + '[%s:]' % match.group(2))
            match = re.search('(\\w+?)\\.join\\(("[^"]*?")\\)', lines[i])
            if match:
                lines[i] = lines[i].replace(match.group(0), match.group(2) + '.join(' + match.group(1) + ')')

        return '\n'.join(lines)

    def _getLocalFunBody(self, funName):
        match = re.search('(function %s\\([^)]+?\\){[^}]+?})' % funName, self.playerData)
        if match:
            return match.group(1)
        return ''

    def _getAllLocalSubFunNames(self, mainFunBody):
        match = re.compile('[ =(,](\\w+?)\\([^)]*?\\)').findall(mainFunBody)
        if len(match):
            funNameTab = set(match[1:])
            return funNameTab
        return set()

    def decryptSignature(self, s, playerUrl):
        printDBG('decrypt_signature sign_len[%d] playerUrl[%s]' % (len(s), playerUrl))
        self._cleanTmpVariables()
        if playerUrl not in self.algoCache:
            request = urllib2.Request(playerUrl)
            try:
                self.playerData = urllib2.urlopen(request).read()
                self.playerData = self.playerData.decode('utf-8', 'ignore')
            except:
                printDBG('Unable to download playerUrl webpage')
                return ''

            match = re.search('signature=(\\w+?)\\([^)]\\)', self.playerData)
            if match:
                mainFunName = match.group(1)
                printDBG('Main signature function name = "%s"' % mainFunName)
            else:
                printDBG('Can not get main signature function name')
                return ''
            self._getfullAlgoCode(mainFunName)
            algoLines = self.fullAlgoCode.split('\n')
            for i in range(len(algoLines)):
                algoLines[i] = '\t' + algoLines[i]

            self.fullAlgoCode = 'def extractedSignatureAlgo(param):'
            self.fullAlgoCode += '\n'.join(algoLines)
            self.fullAlgoCode += '\n\treturn %s(param)' % mainFunName
            self.fullAlgoCode += '\noutSignature = extractedSignatureAlgo( inSignature )\n'
            printDBG('---------------------------------------')
            printDBG('|    ALGO FOR SIGNATURE DECRYPTION    |')
            printDBG('---------------------------------------')
            printDBG(self.fullAlgoCode)
            printDBG('---------------------------------------')
            try:
                algoCodeObj = compile(self.fullAlgoCode, '', 'exec')
            except:
                printDBG('decryptSignature compile algo code EXCEPTION')
                return ''

        else:
            printDBG('Algo taken from cache')
            algoCodeObj = self.algoCache[playerUrl]
        vGlobals = {'__builtins__': None,
         'len': len,
         'list': list}
        vLocals = {'inSignature': s,
         'outSignature': ''}
        try:
            exec (algoCodeObj, vGlobals, vLocals)
        except:
            printDBG('decryptSignature exec code EXCEPTION')
            return ''

        printDBG('Decrypted signature = [%s]' % vLocals['outSignature'])
        if playerUrl not in self.algoCache and '' != vLocals['outSignature']:
            printDBG('Algo from player [%s] added to cache' % playerUrl)
            self.algoCache[playerUrl] = algoCodeObj
        self._cleanTmpVariables()
        return vLocals['outSignature']

    def _getfullAlgoCode(self, mainFunName, recDepth = 0):
        if self.MAX_REC_DEPTH <= recDepth:
            printDBG('_getfullAlgoCode: Maximum recursion depth exceeded')
            return
        funBody = self._getLocalFunBody(mainFunName)
        if '' != funBody:
            funNames = self._getAllLocalSubFunNames(funBody)
            if len(funNames):
                for funName in funNames:
                    if funName not in self.allLocalFunNamesTab:
                        self.allLocalFunNamesTab.append(funName)
                        printDBG('Add local function %s to known functions' % mainFunName)
                        self._getfullAlgoCode(funName, recDepth + 1)

            funBody = self._jsToPy(funBody)
            self.fullAlgoCode += '\n' + funBody + '\n'

decryptor = CVevoSignAlgoExtractor()

class get_yt:

    def removeAdditionalEndingDelimiter(self, data):
        pos = data.find('};')
        if pos != -1:
            data = data[:pos + 1]
        return data

    def extractFlashVars(self, data, assets):
        flashvars = {}
        found = False
        for line in data.split('\n'):
            if line.strip().find(';ytplayer.config = ') > 0:
                found = True
                p1 = line.find(';ytplayer.config = ') + len(';ytplayer.config = ') - 1
                p2 = line.rfind(';')
                if p1 <= 0 or p2 <= 0:
                    continue
                data = line[p1 + 1:p2]
                break

        data = self.removeAdditionalEndingDelimiter(data)
        if found:
            data = json.loads(data)
            if assets:
                flashvars = data['assets']
            else:
                flashvars = data['args']
        return flashvars

    def get_youtube_link2(self, url):
        video_url = url
        error = None
        ret = None
        if url.find('youtube') > -1:
            split = url.split('=')
            ret = split.pop()
            if ret.startswith('youtube_gdata'):
                tmpval = split.pop()
                if tmpval.endswith('&feature'):
                    tmp = tmpval.split('&')
                    ret = tmp.pop(0)
            video_id = ret
            video_url = None
            links = {}
            watch_url = 'http://www.youtube.com/watch?v=%s&safeSearch=none' % video_id
            watchrequest = Request(watch_url, None, {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2',
                                                     'Accept-Charset': 'windows-1251,utf-8;q=0.7,*;q=0.7',
                                                     'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
                                                     'Accept-Language': 'ru,en-us;q=0.7,en;q=0.3'})
            try:
                print 'Youtube parser trying to find avalable Stream', watch_url
                result = urlopen2(watchrequest).read()
            except (URLError, HTTPException, socket.error) as err:
                print 'Youtube parser Error: - Error code: ', str(err)
                return video_url

            flashvars = self.extractFlashVars(result, 0)
            if not flashvars.has_key('url_encoded_fmt_stream_map'):
                return video_url
            else:
                for url_desc in flashvars['url_encoded_fmt_stream_map'].split(','):
                    url_desc_map = parse_qs(url_desc)
                    if not (url_desc_map.has_key('url') or url_desc_map.has_key('stream')):
                        continue
                    key = int(url_desc_map['itag'][0])
                    url = ''
                    if url_desc_map.has_key('url'):
                        url = unquote_plus(url_desc_map['url'][0])
                    elif url_desc_map.has_key('conn') and url_desc_map.has_key('stream'):
                        url = unquote_plus(url_desc_map['conn'][0])
                        if url.rfind('/') < len(url) - 1:
                            url = url + '/'
                        url = url + unquote_plus(url_desc_map['stream'][0])
                    elif url_desc_map.has_key('stream') and not url_desc_map.has_key('conn'):
                        url = unquote_plus(url_desc_map['stream'][0])
                    if url_desc_map.has_key('sig'):
                        url = url + '&signature=' + url_desc_map['sig'][0]
                    elif url_desc_map.has_key('s'):
                        sig = url_desc_map['s'][0]
                        flashvars = self.extractFlashVars(result, 1)
                        js = flashvars['js']
                        url = url + '&signature=' + decryptor.decryptSignature(sig, js)
                    try:
                        links[VIDEO_FMT_PRIORITY_MAP[str(key)]] = {'fmtid': key, 'fmturl': unquote_plus(url)}
                    except KeyError:
                        print 'skipping', key, 'fmt not in priority videos'
                        continue

                try:
                    if links and len(links):
                        video_key = -1
                        video_tulpe = []
                        film_quality = []
                        while video_key < len(links)-1:
                            video_key += 1
                            best_video = links[sorted(links.iterkeys())[video_key]]
                            video_url = str(best_video['fmturl'].split(';')[0])
                            video_tulpe.append(video_url)
                    video_url = video_tulpe[0]
                    print video_url
                    return video_url
                except (KeyError, IndexError):
                    return url


#url = 'http://www.youtube.com/watch?v=HvSaBVSAkz4'
#url = 'http://www.youtube.com/watch?v=CdBf-tfnWZY'
#url = 'http://www.youtube.com/watch?v=PlGfyc-qP_c'
#url = 'http://www.youtube.com/watch?v=jmIeIKmWsX0'
#url = 'http://www.youtube.com/watch?v=eDdI7GhZSQA'
#url = 'http://www.youtube.com/watch?v=PlGfyc-qP_c'
#youtube_url().get_youtube_link2(url)

