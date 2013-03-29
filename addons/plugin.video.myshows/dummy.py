# -*- coding: utf-8 -*-

import json, sys, urllib, re, os


def getDirList(path, newl=None):
    l=[]
    if not newl: newl=os.listdir(path)
    for fl in newl:
        match=re.match('.avi|.mp4|.mkV|.flv|.mov|.vob|.wmv|.ogm|.asx|.mpg|mpeg|.avc|.vp3|.fli|.flc|.m4v', fl[int(len(fl))-4:len(fl)], re.I)
        if match:
            l.append(fl)
    return l

def cutFileNames(l):
    from difflib import Differ
    d = Differ()
    i=-1

    text1 = str(l[0])
    text2 = str(l[1])

    seps=['.|:| ', '.|:|x', ' |:|x', ' |:|-', '_|:|',]
    for s in seps:
        sep_file=str(s).split('|:|')[0]
        result=list(d.compare(text1.split(sep_file), text2.split(sep_file)))
        if len(result)>5:
            break

    print list(d.compare(text1.split(sep_file), text2.split(sep_file)))

    start=''
    end=''

    for res in result:
        if str(res).startswith('-') or str(res).startswith('+') or str(res).startswith('.?'):
            break
        start=start+str(res).strip()+sep_file
    result.reverse()
    for res in result:
        if str(res).startswith('-') or str(res).startswith('+') or str(res).startswith('?'):
            break
        end=sep_file+str(res).strip()+end


    newl=l
    l=[]
    print start
    print end
    for fl in newl:
        fl=fl[len(start):len(fl)-len(end)]
        l.append(fl)
    return l

def FileNamesPrepare(filename):
    my_season=None
    my_episode=None

    try:
        if int(filename):
            my_episode=int(filename)
            return [my_season, my_episode, filename]
    except: pass


    urls=['.+?(\d*)x(\d*).+?','.*?s(\d*)e(\d*).*?','.*?(\d*)-(\d*).*?','.*?E(\d*).*?']
    for file in urls:
        match=re.compile(file, re.DOTALL | re.I).findall(filename)
        if match:
            try:
                my_episode=int(match[1])
                my_season=int(match[0])
            except:
                try:
                    my_episode=int(match[0])
                except:
                    try:
                        my_episode=int(match[0][1])
                        my_season=int(match[0][0])
                    except:
                        try:
                            my_episode=int(match[0][0])
                        except: break
            print str([my_season, my_episode, filename])
            return [my_season, my_episode, filename]

x=FileNamesPrepare('S08E11.Max.Jets')

#filenames=['D:\seriez\Suzumiya Haruhi no Yuuutsu S1 720р',u'D:\seriez\The.Newsroom.S01.720p.HDTVRip.2xRus.Eng.HDCLUB',u'D:\seriez\DoctorWho.Season5.RusSub.HDTV.720p',u'D:\seriez\Twilight_Zone_Season_3',u'D:\seriez\Suits\Season 2']

#filename=filenames[0].decode('utf-8')
#dirlist=getDirList(filename)
#print dirlist
#cutlist=cutFileNames(dirlist)
#print cutlist

#for fn in cutlist:
    #x=FileNamesPrepare(fn)
    #filename=os.path.join(filename, dirlist[cutlist.index(fn)])
    #stype='file'
    ##episodeId=x[1]

    ##print str(x)
