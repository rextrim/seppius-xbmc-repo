import sys
from urllib import unquote_plus
from urllib2 import Request, URLError, urlopen as urlopen2
from urlparse import parse_qs
try:
    import simplejson as json
except ImportError:
    import json

import urllib2, re
VIDEO_FMT_PRIORITY_MAP = {'121': 1,
 '37': 2,
 '102': 3,
 '120': 4,
 '84': 5,
 '45': 6,
 '45': 7,
 '38': 8,
 '22': 9,
 '85': 10,
 '46': 11,
 '101': 12,
 '44': 13,
 '59': 15,
 '78': 16,
 '100': 17,
 '82': 18,
 '18': 19,
 '83': 20,
 '36': 21,
 '17': 22,
 '26': 23,
 '33': 24}
VIDEO_FMT_NAME = {36: 'mp4 180p',
 17: 'mp4 144p',
 18: 'mp4 360p',
 22: 'mp4 720p',
 26: '26?',
 33: '33?',
 37: 'mp4 1080p',
 38: 'vp8 720p',
 44: 'vp8 480p',
 45: 'vp8 720p',
 46: 'vp8 520p',
 59: 'rtmpe 480',
 78: 'rtmpe 400',
 82: 'h264 360p',
 83: 'h264 240p',
 84: 'h264 720p',
 85: 'h264 520p',
 100: 'vp8 360p',
 101: 'vp8 480p',
 102: 'vp8 720p',
 120: 'mp4 hd720',
 121: 'mm4 hd1080'}

def printDBG(s):
    print s


class CVevoSignAlgoExtractor:
    MAX_REC_DEPTH = 5

    def __init__(self):
        self.algoCache = {}
        self._cleanTmpVariables()

    def _cleanTmpVariables(self):
        self.fullAlgoCode = ''
        self.allLocalFunNamesTab = []
        self.playerData = ''

    def _extractVarLocalFuns(self, match):
        varName, objBody = match.groups()
        output = ''
        for func in objBody.split( '},' ):
            output += re.sub(
                r'^([^:]+):function\(([^)]*)\)',
                r'function %s__\1(\2,*args)' % varName,
                func
            ) + '\n'
        return output

    def _jsToPy(self, jsFunBody):
        print (jsFunBody)
        pythonFunBody = re.sub(r'var ([^=]+)={(.*?)}};', self._extractVarLocalFuns, jsFunBody)
        pythonFunBody = re.sub(r'function (\w*)\$(\w*)', r'function \1_S_\2', pythonFunBody)
        pythonFunBody = pythonFunBody.replace('function', 'def').replace('{', ':\n\t').replace('}', '').replace(';', '\n\t').replace('var ', '')
        pythonFunBody = pythonFunBody.replace('.reverse()', '[::-1]')

        lines = pythonFunBody.split('\n')
        for i in range(len(lines)):
            # a.split("") -> list(a)
            match = re.search('(\w+?)\.split\(""\)', lines[i])
            if match:
                lines[i] = lines[i].replace( match.group(0), 'list(' + match.group(1)  + ')')
            # a.length -> len(a)
            match = re.search('(\w+?)\.length', lines[i])
            if match:
                lines[i] = lines[i].replace( match.group(0), 'len(' + match.group(1)  + ')')
            # a.slice(3) -> a[3:]
            match = re.search('(\w+?)\.slice\((\w+?)\)', lines[i])
            if match:
                lines[i] = lines[i].replace( match.group(0), match.group(1) + ('[%s:]' % match.group(2)) )

            # a.join("") -> "".join(a)
            match = re.search('(\w+?)\.join\(("[^"]*?")\)', lines[i])
            if match:
                lines[i] = lines[i].replace( match.group(0), match.group(2) + '.join(' + match.group(1) + ')' )

            # a.splice(b,c) -> del a[b:c]
            match = re.search('(\w+?)\.splice\(([^,]+),([^)]+)\)', lines[i])
            if match:
                lines[i] = lines[i].replace( match.group(0), 'del ' + match.group(1) + '[' + match.group(2) + ':' + match.group(3) + ']' )

        pythonFunBody = "\n".join(lines)
        pythonFunBody = re.sub(r'(\w+)\.(\w+)\(', r'\1__\2(', pythonFunBody)
        pythonFunBody = re.sub(r'([^=])(\w+)\[::-1\]', r'\1\2.reverse()', pythonFunBody)
        return pythonFunBody

    def _getLocalFunBody(self, funName, playerData):
        # get function body
        funName=funName.replace('$', '\\$')
        match = re.search('(function %s\([^)]+?\){[^}]+?})' % funName, playerData)
        if match:
            # return jsFunBody
            return match.group(1)
        return ''

    def _getAllLocalSubFunNames(self, mainFunBody):
        match = re.compile('[ =(,](\\w+?)\\([^)]*?\\)').findall(mainFunBody)
        if len(match):
            funNameTab = set(match[1:])
            return funNameTab
        return set()

    def _extractLocalVarNames(self, mainFunBody ):
        valid_funcs = ( 'reverse', 'split', 'splice', 'slice', 'join' )
        match = re.compile( r'[; =(,](\w+)\.(\w+)\(' ).findall( mainFunBody )
        local_vars = []
        for name in match:
            if name[1] not in valid_funcs:
                local_vars.append( name[0] )
        print ('Found variable names: ' + str(local_vars))
        return set( local_vars )

    def _getLocalVarObjBody(self, varName, playerData):
        match = re.search( r'var %s={.*?}};' % varName, playerData )
        if match:
            print ('Found variable object: ' + match.group(0))
            return match.group(0)
        return ''

    def decryptSignature(self, s, playerUrl):
        playerUrl = playerUrl[:4] != 'http' and 'http:' + playerUrl or playerUrl
        printDBG('decrypt_signature sign_len[%d] playerUrl[%s]' % (len(s), playerUrl))
        self._cleanTmpVariables()
        if playerUrl not in self.algoCache:
            request = urllib2.Request(playerUrl)
            try:
                playerData = urllib2.urlopen(request).read()
                playerData = playerData.decode('utf-8', 'ignore')
            except:
                printDBG('Unable to download playerUrl webpage')
                return ''

            match = re.search("signature=([$a-zA-Z]+)\([^)]\)", playerData)

            if match:
                mainFunName = match.group(1)
                print ('Main signature function name = "%s"' % mainFunName)
            else:
                print ('Can not get main signature function name')
                return ''

            fullAlgoCode = self._getfullAlgoCode( mainFunName, playerData )

            # wrap all local algo function into one function extractedSignatureAlgo()
            algoLines = fullAlgoCode.split('\n')
            for i in range(len(algoLines)):
                algoLines[i] = '\t' + algoLines[i]
            fullAlgoCode  = 'def extractedSignatureAlgo(param):'
            fullAlgoCode += '\n'.join(algoLines)
            fullAlgoCode += '\n\treturn %s(param)' % mainFunName
            fullAlgoCode += '\noutSignature = extractedSignatureAlgo( inSignature )\n'

            # after this function we should have all needed code in fullAlgoCode

            print ( "---------------------------------------" )
            print ( "|    ALGO FOR SIGNATURE DECRYPTION    |" )
            print ( "---------------------------------------" )
            print ( fullAlgoCode                         )
            print ( "---------------------------------------" )

            try:
                algoCodeObj = compile(fullAlgoCode, '', 'exec')
            except:
                print ('decryptSignature compile algo code EXCEPTION')
                return ''
        else:
            # get algoCodeObj from algoCache
            print('Algo taken from cache')
            algoCodeObj = self.algoCache[playerUrl]

        # for security alow only flew python global function in algo code
        vGlobals = {"__builtins__": None, 'len': len, 'list': list}

        # local variable to pass encrypted sign and get decrypted sign
        vLocals = { 'inSignature': s, 'outSignature': '' }

        # execute prepared code
        try:
            exec( algoCodeObj, vGlobals, vLocals )
        except:
            print ('decryptSignature exec code EXCEPTION')
            #exec( algoCodeObj, vGlobals, vLocals )
            return ''

        print ('Decrypted signature = [%s]' % vLocals['outSignature'])
        # if algo seems ok and not in cache, add it to cache
        if playerUrl not in self.algoCache and '' != vLocals['outSignature']:
            print ('Algo from player [%s] added to cache' % playerUrl)
            self.algoCache[playerUrl] = algoCodeObj

        return vLocals['outSignature']

    def _getfullAlgoCode( self, mainFunName, playerData, recDepth = 0, allLocalFunNamesTab=[], allLocalVarNamesTab=[] ):
        # Max recursion of 5
        if 5 <= recDepth:
            print ('_getfullAlgoCode: Maximum recursion depth exceeded')
            return

        funBody = self._getLocalFunBody( mainFunName, playerData)
        if '' != funBody:
            funNames = self._getAllLocalSubFunNames(funBody)
            if len(funNames):
                for funName in funNames:
                    funName_=funName.replace('$','_S_')
                    if funName not in allLocalFunNamesTab:
                        funBody=funBody.replace(funName,funName_)
                        allLocalFunNamesTab.append(funName)
                        self.common.log("Add local function %s to known functions" % mainFunName)
                        funBody = self._getfullAlgoCode( funName, playerData, recDepth + 1, allLocalFunNamesTab ) + "\n" + funBody

            varNames = self._extractLocalVarNames(funBody)
            if len(varNames):
                for varName in varNames:
                    print ("Found local var object: " + str(varName))
                    print ("Known vars: " + str(allLocalVarNamesTab))
                    if varName not in allLocalVarNamesTab:
                        print ("Adding local var object %s to known objects" % varName)
                        allLocalVarNamesTab.append(varName)
                        funBody = self._getLocalVarObjBody( varName, playerData ) + "\n" + funBody

            # conver code from javascript to python
            funBody = self._jsToPy(funBody)
            return '\n' + funBody + '\n'
        return funBody


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
                    links[VIDEO_FMT_PRIORITY_MAP[str(key)]] = {'fmtid': key,
                     'fmturl': unquote_plus(url)}
                except KeyError:
                    print 'skipping', key, 'fmt not in priority videos'
                    continue

            try:
                if links and len(links):
                    video_key = -1
                    video_tulpe = []
                    film_quality = []
                    while video_key < len(links) - 1:
                        video_key += 1
                        best_video = links[sorted(links.iterkeys())[video_key]]
                        video_url = str(best_video['fmturl'].split(';')[0])
                        video_tulpe.append(video_url)
                        quality = VIDEO_FMT_NAME[links[sorted(links.iterkeys())[video_key]]['fmtid']]
                        film_quality.append(quality)
                video_url = video_tulpe[0]
                print video_url
                return video_url
            except (KeyError, IndexError):
                return url

        return