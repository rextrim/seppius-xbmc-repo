# -*- coding: utf-8 -*-
#

import xbmc
import xbmcaddon
import threading
import time, urllib

import utilities
from utilities import Debug, get_float_setting
#from rating import ratingCheck
try:
    import simplejson as json
except ImportError:
    import json
# read settings
__settings__ = xbmcaddon.Addon("script.myshows")
__myshows__ = xbmcaddon.Addon("plugin.video.myshows")
__language__ = __settings__.getLocalizedString


class Scrobbler(threading.Thread):
    myshowsapi = None
    totalTime = 1
    watchedTime = 0
    startTime = 0
    pausedTime = 0
    curVideo = None
    curVideoData = None
    pinging = False
    playlistLength = 1
    abortRequested = False
    markedAsWatched = []
    traktapi = None
    isPlaying = False
    isPaused = False
    isMultiPartEpisode = False
    lastMPCheck = 0
    curMPEpisode = 0
    videoDuration = 1
    watchedTime = 0
    pausedAt = 0
    curVideo = None
    curVideoInfo = None
    playlistLength = 1
    playlistIndex = 0
    markedAsWatched = []
    traktSummaryInfo = None

    def __init__(self, api):
        threading.Thread.__init__(self)
        self.myshowsapi = api
        self.start()

    def run(self):
        # When requested ping myshows to say that the user is still watching the item
        count = 0
        Debug("[Scrobbler] Starting.")
        while (not (self.abortRequested or xbmc.abortRequested)):
            xbmc.sleep(5000) # sleep for 5 seconds
            if self.pinging and xbmc.Player().isPlayingVideo():
                count += 1
                self.watchedTime = xbmc.Player().getTime()
                self.startTime = time.time()
                if count >= 100:
                    self.watching()
                    count = 0
            else:
                count = 0

        Debug("[Scrobbler] Stopping.")

    def playbackStarted(self, data):
        Debug("[Scrobbler] playbackStarted(data: %s)" % data)
        if self.curVideo != None and self.curVideo != data['item']:
            self.playbackEnded()
        self.curVideo = data['item']
        self.curVideoData = data
        if self.curVideo != None:
            # {"jsonrpc":"2.0","method":"Player.OnPlay","params":{"data":{"item":{"type":"movie"},"player":{"playerid":1,"speed":1},"title":"Shooter","year":2007},"sender":"xbmc"}}
            # {"jsonrpc":"2.0","method":"Player.OnPlay","params":{"data":{"episode":3,"item":{"type":"episode"},"player":{"playerid":1,"speed":1},"season":4,"showtitle":"24","title":"9:00 A.M. - 10:00 A.M."},"sender":"xbmc"}}
            if 'type' in self.curVideo: #and 'id' in self.curVideo:
                Debug("[Scrobbler] Watching: " + self.curVideo['type']) #+" - "+str(self.curVideo['id']))
                try:
                    if not xbmc.Player().isPlayingVideo():
                        Debug("[Scrobbler] Suddenly stopped watching item")
                        return
                    time.sleep(1) # Wait for possible silent seek (caused by resuming)
                    self.watchedTime = xbmc.Player().getTime()
                    self.totalTime = xbmc.Player().getTotalTime()
                    if self.totalTime == 0:
                        if self.curVideo['type'] == 'movie':
                            self.totalTime = 90
                        elif self.curVideo['type'] == 'episode':
                            self.totalTime = 30
                        else:
                            self.totalTime = 1
                    #self.playlistLength = utilities.getPlaylistLengthFromXBMCPlayer(data['player']['playerid'])
                    # playerid 1 is video.
                    self.playlistLength = utilities.getPlaylistLengthFromXBMCPlayer(1)
                    if (self.playlistLength == 0):
                        Debug("[Scrobbler] Warning: Cant find playlist length?!, assuming that this item is by itself")
                        self.playlistLength = 1
                    if self.curVideo["type"] == "episode":
                        if self.curVideo.has_key("multi_episode_count"):
                            self.markedAsWatched = []
                            episode_count = self.curVideo["multi_episode_count"]
                            for i in range(episode_count):
                                self.markedAsWatched.append(False)
                except Exception, e:
                    Debug("[Scrobbler] Suddenly stopped watching item, or error: %s" % e.message)
                    self.curVideo = None
                    self.startTime = 0
                    return
                self.startTime = time.time()
                self.watching()
                self.pinging = True
            else:
                self.curVideo = None
                self.startTime = 0

    def playbackResumed(self):
        Debug("[Scrobbler] playbackResumed()")
        if self.pausedTime != 0:
            p = time.time() - self.pausedTime
            Debug("[Scrobbler] Resumed after: %s" % str(p))
            self.pausedTime = 0
            self.watching()

    def playbackPaused(self):
        Debug("[Scrobbler] playbackPaused()")
        if self.startTime != 0:
            self.watchedTime += time.time() - self.startTime
            Debug("[Scrobbler] Paused after: " + str(self.watchedTime))
            self.startTime = 0
            self.pausedTime = time.time()

    def playbackSeek(self):
        Debug("[Scrobbler] playbackSeek()")
        if self.startTime != 0:
            self.watchedTime = xbmc.Player().getTime()
            self.startTime = time.time()

    def playbackEnded(self):
        Debug("[Scrobbler] playbackEnded()")
        if self.startTime != 0:
            if self.curVideo == None:
                Debug("[Scrobbler] Warning: Playback ended but video forgotten")
                return
            self.watchedTime += time.time() - self.startTime
            self.pinging = False
            self.markedAsWatched = []
            if self.watchedTime != 0:
                if 'type' in self.curVideo: #and 'id' in self.curVideo:
                    self.check()
                #ratingCheck(self.curVideo, self.watchedTime, self.totalTime, self.playlistLength)
                self.watchedTime = 0
            self.startTime = 0
            self.curVideo = None

    def _currentEpisode(self, watchedPercent, episodeCount):
        split = (100 / episodeCount)
        for i in range(episodeCount - 1, 0, -1):
            if watchedPercent >= (i * split):
                return i
        return 0

    def watching(self):
        if not self.isPlaying:
            return

        if not self.curVideoInfo:
            return

        Debug("[Scrobbler] watching()")
        scrobbleMovieOption = utilities.getSettingAsBool('scrobble_movie')
        scrobbleEpisodeOption = utilities.getSettingAsBool('scrobble_episode')

        self.update(True)

        duration = self.videoDuration / 60
        watchedPercent = (self.watchedTime / self.videoDuration) * 100

        if self.isMultiPartEpisode:
            Debug("[Scrobbler] Multi-part episode, watching part %d of %d." % (
                self.curMPEpisode + 1, self.curVideo['multi_episode_count']))
            # recalculate watchedPercent and duration for multi-part
            adjustedDuration = int(self.videoDuration / self.curVideo['multi_episode_count'])
            duration = adjustedDuration / 60
            watchedPercent = ((self.watchedTime - (adjustedDuration * self.curMPEpisode)) / adjustedDuration) * 100

            response = 'yep'
            if response != None:
                if self.curVideoInfo['tvdb_id'] is None:
                    if 'status' in response and response['status'] == "success":
                        if 'show' in response and 'tvdb_id' in response['show']:
                            self.curVideoInfo['tvdb_id'] = response['show']['tvdb_id']
                            if 'id' in self.curVideo and utilities.getSettingAsBool('update_tvdb_id'):
                                req = {"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.SetTVShowDetails",
                                       "params": {"tvshowid": self.curVideoInfo['tvshowid'],
                                                  "imdbnumber": self.curVideoInfo['tvdb_id']}}
                                utils.xbmcJsonRequest(req)
                                # get summary data now if we are rating this episode
                            if utilities.getSettingAsBool('rate_episode') and self.traktSummaryInfo is None:
                                self.traktSummaryInfo = self.traktapi.getEpisodeSummary(self.curVideoInfo['tvdb_id'],
                                                                                        self.curVideoInfo['season'],
                                                                                        self.curVideoInfo['episode'])

                Debug("[Scrobbler] Watch response: %s" % str(response))
                match = utilities.getEpisodeDetailsFromXbmc(self.curMPEpisode, ['showtitle', 'season', 'episode', 'tvshowid', 'uniqueid'])
            else:
                match = utilities.getEpisodeDetailsFromXbmc(self.curVideo['id'], ['showtitle', 'season', 'episode', 'tvshowid', 'uniqueid'])
        elif 'showtitle' in self.curVideoData and 'season' in self.curVideoData and 'episode' in self.curVideoData:
            match = {}
            match['tvdb_id'] = None
            match['year'] = None
            match['showtitle'] = self.curVideoData['showtitle']
            match['season'] = self.curVideoData['season']
            match['episode'] = self.curVideoData['episode']
            match['uniqueid'] = None
            if match == None:
                return


    def stoppedWatching(self):
        Debug("[Scrobbler] stoppedWatching()")
        scrobbleMovieOption = __settings__.getSetting("scrobble_movie")

        if self.curVideo['type'] == 'movie' and scrobbleMovieOption == 'true':
            response = self.myshowsapi.cancelWatchingMovie()
            if response != None:
                Debug("[Scrobbler] Cancel watch response: " + str(response))
        elif self.curVideo['type'] == 'episode':
            response = self.myshowsapi.cancelWatchingEpisode()
            if response != None:
                Debug("[Scrobbler] Cancel watch response: " + str(response))

    def scrobble(self):
        Debug("[Scrobbler] scrobble()")
        Debug("[Scrobbler] self.curVideo:" + unicode(self.curVideo))
        Debug("[Scrobbler] self.curVideoData" + unicode(self.curVideoData))
        if self.curVideo['type']:
            match = None
            if 'id' in self.curVideo:
            #if self.curVideo.has_key("multi_episode_count"):
            #cur_episode = self._currentEpisode((self.watchedTime / self.totalTime) * 100, self.curVideo['multi_episode_count'])
                #	cur_episode = self.curVideo['multi_episode_count'] - 1
                #	Debug("[Scrobbler] Multi-part episode, scrobbling part %d of %d." % (cur_episode + 1, self.curVideo['multi_episode_count']))
                #	match = utilities.getEpisodeDetailsFromXbmc(self.curVideo["multi_episode_data"][cur_episode], ['showtitle', 'season', 'episode', 'tvshowid', 'uniqueid'])
                #else:
                match = utilities.getEpisodeDetailsFromXbmc(self.curVideo['id'],
                                                            ['showtitle', 'season', 'episode', 'tvshowid', 'uniqueid'])
            elif 'showtitle' in self.curVideoData and 'season' in self.curVideoData and 'episode' in self.curVideoData:
                match = {}
                match['tvdb_id'] = None
                match['year'] = None
                match['showtitle'] = self.curVideoData['showtitle']
                match['season'] = self.curVideoData['season']
                match['episode'] = self.curVideoData['episode']
                match['uniqueid'] = self.curVideoData['uniqueid']['unknown']
            elif 'label' in self.curVideo and len(self.curVideo['label']) > 0:
                match = {}
                match['label'] = self.curVideo['label']

            if match == None:
                return

            duration = self.totalTime / 60
            watchedPercent = int((self.watchedTime / self.totalTime) * 100)
            Debug("[Scrobbler] Match for MyShows.ru Plugin: " + str(match))
            xbmc.executebuiltin(
                'xbmc.RunPlugin("plugin://plugin.video.myshows/?mode=70&action=check&title=' + urllib.quote_plus(
                    json.dumps(match)) + '")')
        #response = self.myshowsapi.scrobbleEpisode(match['tvdb_id'], match['showtitle'], match['year'], match['season'], match['episode'], match['uniqueid']['unknown'], duration, watchedPercent)
        #if response != None:
        #Debug("[Scrobbler] Scrobble response: "+str(response))

    def check(self):
        scrobbleMinViewTimeOption = float(__myshows__.getSetting("rate_min_view_time"))

        Debug("[Scrobbler] watched: %s / %s, min=%s" % (
            str(self.watchedTime), str(self.totalTime), str(scrobbleMinViewTimeOption)))
        if ((self.watchedTime / self.totalTime) * 100) >= scrobbleMinViewTimeOption:
            self.scrobble()
        else:
            self.stoppedWatching()

    def update(self, forceCheck = False):
        if not xbmc.Player().isPlayingVideo():
            return

        if self.isPlaying:
            t = xbmc.Player().getTime()
            l = xbmc.PlayList(xbmc.PLAYLIST_VIDEO).getposition()
            if self.playlistIndex == l:
                self.watchedTime = t
            else:
                Debug("[Scrobbler] Current playlist item changed! Not updating time! (%d -> %d)" % (self.playlistIndex, l))

            if 'id' in self.curVideo and self.isMultiPartEpisode:
                # do transition check every minute
                if (time.time() > (self.lastMPCheck + 60)) or forceCheck:
                    self.lastMPCheck = time.time()
                    watchedPercent = (self.watchedTime / self.videoDuration) * 100
                    epIndex = self._currentEpisode(watchedPercent, self.curVideo['multi_episode_count'])
                    if self.curMPEpisode != epIndex:
                        # current episode in multi-part episode has changed
                        Debug("[Scrobbler] Attempting to scrobble episode part %d of %d." % (self.curMPEpisode + 1, self.curVideo['multi_episode_count']))

                        # recalculate watchedPercent and duration for multi-part, and scrobble
                        adjustedDuration = int(self.videoDuration / self.curVideo['multi_episode_count'])
                        duration = adjustedDuration / 60
                        watchedPercent = ((self.watchedTime - (adjustedDuration * self.curMPEpisode)) / adjustedDuration) * 100
                        response = self.traktapi.scrobbleEpisode(self.curVideoInfo, duration, watchedPercent)
                        if response != None:
                            Debug("[Scrobbler] Scrobble response: %s" % str(response))

                        # update current information
                        self.curMPEpisode = epIndex
                        self.curVideoInfo = utilities.getEpisodeDetailsFromXbmc(self.curVideo['multi_episode_data'][self.curMPEpisode], ['showtitle', 'season', 'episode', 'tvshowid', 'uniqueid'])

                        if not forceCheck:
                            self.watching()