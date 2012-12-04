import re, os, urllib, urllib2, sys, urlparse
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import HTMLParser
hpar = HTMLParser.HTMLParser()


class XPpod():
    #----------------- init ----------------------------------------------------
    def __init__(self, Addon):
        self.Addon = Addon

    #---------- get web page -------------------------------------------------------
    def get_HTML(self, url, post = None, ref = None):
        request = urllib2.Request(url, post)

        host = urlparse.urlsplit(url).hostname
        if ref==None:
            ref='http://'+host

        request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
        request.add_header('Host',   host)
        request.add_header('Accept', '*/*')
        request.add_header('Accept-Language', 'ru-RU')
        request.add_header('Referer',             ref)

        try:
            f = urllib2.urlopen(request)
        except IOError, e:
            if hasattr(e, 'reason'):
               xbmc.log('We failed to reach a server.')
            elif hasattr(e, 'code'):
               xbmc.log('The server couldn\'t fulfill the request.')

        html = f.read()

        return html

    #-------------------------------------------------------------------------------
    # Юppod decoder (for seasonvar.ru)
    #-------------------------------------------------------------------------------
    def Decode(self, param):
        #-- get hash keys
        f = open(xbmc.translatePath(os.path.join(self.Addon.getAddonInfo('path'), r'resources', r'lib', r'hash.key')), 'r')
        hash_key = f.read()
        f.close()

        rez = self.Decode_String(param, hash_key)
        if not 'html:' in rez:
            #---- get new hash keys
            url = 'http://justpaste.it/1gj7'
            html = self.get_HTML(url)

            code = re.compile('<div id="articleContent">(.+?)<div class="noteFotter">', re.MULTILINE|re.DOTALL).findall(html)[0]

            hash_list = []
            for rec in re.compile('<p>(.+?)<\/p>', re.MULTILINE|re.DOTALL).findall(code):
                hash_list.append(rec)

            #---- save new hash keys
            swf = open(xbmc.translatePath(os.path.join(self.Addon.getAddonInfo('path'), r'resources', r'lib', r'hash.key')), 'w')
            swf.write(hash_list[0]+'\n'+hash_list[1])
            swf.close()

            #---
            hask_key = hash_list[0]+'\n'+hash_list[1]
            rez = self.Decode_String(param, hash_key)

        return rez

    def Decode_String(self, param, hash_key):
        #-- define variables
        loc_3 = [0,0,0,0]
        loc_4 = [0,0,0]
        loc_2 = ''

        #-- define hash parameters for decoding
        dec = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
        hash1 = hash_key.split('\n')[0]
        hash2 = hash_key.split('\n')[1]

        #-- decode
        for i in range(0, len(hash1)):
            re1 = hash1[i]
            re2 = hash2[i]

            param = param.replace(re1, '___')
            param = param.replace(re2, re1)
            param = param.replace('___', re2)

        i = 0
        while i < len(param):
            j = 0
            while j < 4 and i+j < len(param):
                loc_3[j] = dec.find(param[i+j])
                j = j + 1

            loc_4[0] = (loc_3[0] << 2) + ((loc_3[1] & 48) >> 4);
            loc_4[1] = ((loc_3[1] & 15) << 4) + ((loc_3[2] & 60) >> 2);
            loc_4[2] = ((loc_3[2] & 3) << 6) + loc_3[3];

            j = 0
            while j < 3:
                if loc_3[j + 1] == 64:
                    break

                loc_2 += unichr(loc_4[j])

                j = j + 1

            i = i + 4;

        return loc_2
