import sys
from urllib import unquote_plus
from urllib2 import Request, URLError, urlopen as urlopen2
from urlparse import parse_qs


VIDEO_FMT_PRIORITY_MAP = {'121': 1,
 '37': 2,
 '102': 3,
 '120': 4,
 '84': 5,
 '22': 6,
 '85': 7,
 '101': 8,
 '59': 9,
 '78': 10,
 '100': 11,
 '82': 12,
 '18': 13,
 '83': 14,
 '36': 15}
VIDEO_FMT_NAME = [('36', 'mp4 180p'),
 ('18', 'mp4 360p'),
 ('22', 'mp4 720p'),
 ('37', 'mp4 1080p'),                 
 ('59', 'rtmpe 480'),
 ('78', 'rtmpe 400'),
 ('82', 'h264 360p'),
 ('83', 'h264 240p'),
 ('84', 'h264 720p'),
 ('85', 'h264 520p'),
 ('100', 'vp8 360p'),
 ('101', 'vp8 480p'),
 ('102', 'vp8 720p'),
 ('120', 'mp4 hd720'),
 ('121', 'mp4 hd1080')]

class youtube_url:

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
            try:
                for el in ['&el=embedded',
                     '&el=detailpage',
                     '&el=vevo',
                     '']:
                        watch_url = 'http://www.youtube.com/get_video_info?&video_id=%s%s&sts=16387' % (video_id, el)
                        watchrequest = Request(watch_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1', 'Connection': 'Close'})
                        try:
                            infopage = urlopen2(watchrequest).read()
                            videoinfo = parse_qs(infopage)
                            if ('url_encoded_fmt_stream_map') in videoinfo:
                                found = True
                                break
                        except Exception as ex:
                            print 'YT ERROR ' + ex

                if found:
                    video_tulpe = []
                    film_quality = []
                    tmp = videoinfo['url_encoded_fmt_stream_map'][0].replace('sig%3D', 'signature%3D').replace('sig=', 'signature=').split(',')
                    for string in tmp:
                        string = parse_qs(string)
                        fmturl = fmtid = fmtsig = ''
                        if ('itag') in string:
                            fmtid = string['itag'][0]
                        if ('url') in string:
                            fmturl = unquote_plus(string['url'][0])
                        if ('s') in string:
                            fmtsig = string['s'][0]
                            s =  fmtsig
                            sig = ''
                            ill = len(s)
                            while ill > 0:
                                ill -= 1
                                if ill == 77:
                                    sig = sig + s[53]
                                if ill == 53:
                                    sig = sig + s[77]
                                if ill != 81 and ill != 77 and ill != 53 and ill != 0:
                                    sig = sig + s[ill]
                            fmtsig = sig
                        else:
                            fmtsig = ''

                        if fmtid != '' and fmturl != '' and VIDEO_FMT_PRIORITY_MAP.has_key(fmtid):
                            
                            if fmtsig != '':
                                video_url = fmturl.replace('https', 'http') + '&signature=' + fmtsig
                            else:
                                video_url = fmturl
                        break
                                
            except Exception as ex:
                return 'No Youtube video'
            #print video_url
            return video_url





