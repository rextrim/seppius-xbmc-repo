import urllib2, re
from urlparse import parse_qs
from urllib import unquote_plus
import hashlib
def get_yt(url):
	if url.find('youtube.com') > -1:
		video_priority_map = {'38' : 1,'37' : 2,'22' : 3,'18' : 4,'35' : 5,'34' : 6,}
		video_url = url
		try:
			if url.find('youtube') > -1:
				found = False
				finder = url.find('=')
				video_id = url[finder + 1:]
				for el in ['&el=embedded',
				'&el=detailpage',
				'&el=vevo',
				'']:
					info_url = 'http://www.youtube.com/get_video_info?&video_id=%s%s&ps=default&eurl=&gl=US&hl=en' % (video_id, el)
					request = urllib2.Request(info_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
					'Connection': 'Close'})
					try:
						infopage = urllib2.urlopen(request).read()
						videoinfo = parse_qs(infopage)
						if ('url_encoded_fmt_stream_map' or 'fmt_url_map') in videoinfo:
							found = True
							break
					except Exception as ex:
						print ex

				if found:
					video_fmt_map = {}
					fmt_infomap = {}
					if videoinfo.has_key('url_encoded_fmt_stream_map'):
						tmp_fmtUrlDATA = videoinfo['url_encoded_fmt_stream_map'][0].split(',')
					else:
						tmp_fmtUrlDATA = videoinfo['fmt_url_map'][0].split(',')
					for fmtstring in tmp_fmtUrlDATA:
						fmturl = fmtid = fmtsig = ''
						if videoinfo.has_key('url_encoded_fmt_stream_map'):
							try:
								for arg in fmtstring.split('&'):
									if arg.find('=') >= 0:
										key, value = arg.split('=')
										if key == 'itag':
											if len(value) > 3:
												value = value[:2]
											fmtid = value
										elif key == 'url':
											fmturl = value
										elif key == 'sig':
											fmtsig = value

								if fmtid != '' and fmturl != '' and fmtsig != '' and video_priority_map.has_key(fmtid):
									video_fmt_map[video_priority_map[fmtid]] = {'fmtid': fmtid,
									'fmturl': unquote_plus(fmturl),
									'fmtsig': fmtsig}
									fmt_infomap[int(fmtid)] = '%s&signature=%s' % (unquote_plus(fmturl), fmtsig)
								fmturl = fmtid = fmtsig = ''
							except Exception as ex:
								print ex

						else:
							fmtid, fmturl = fmtstring.split('|')
						if video_priority_map.has_key(fmtid) and fmtid != '':
							video_fmt_map[video_priority_map[fmtid]] = {'fmtid': fmtid,
							'fmturl': unquote_plus(fmturl)}
							fmt_infomap[int(fmtid)] = unquote_plus(fmturl)

					if video_fmt_map and len(video_fmt_map):
						best_video = video_fmt_map[sorted(video_fmt_map.iterkeys())[0]]
						video_url = '%s&signature=%s' % (best_video['fmturl'].split(';')[0], best_video['fmtsig'])
		except Exception as ex:
			print ex

		if video_url != url:
			url = video_url
			print url

	return (url)
