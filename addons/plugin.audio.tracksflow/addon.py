#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   Author(c) 26/12/2012, Dmitry Khrysev, E-mail: x86demon@gmail.com
#
#   This Program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2, or (at your option)
#   any later version.
#
#   This Program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; see the file COPYING.  If not, write to
#   the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#   http://www.gnu.org/licenses/gpl.html

import os
from xbmcswift2 import Plugin,xbmcplugin,ListItem
from resources.lib.tracksflow.api import TracksFlow
import SimpleDownloader as downloader

plugin = Plugin()

@plugin.route('/')
def index():
    menu = [{
        'label': '[My Playlists]',
        'path': plugin.url_for('my_playlists')
    }]
    items = top_playlists('0')
    return menu + items

@plugin.route('/top_playlists/<page>/')
def top_playlists(page = 0):
    playlists = getApi().getTopPlaylists(page, plugin.get_setting('Items per page'), plugin.get_setting('Days'))
    items = processPlaylists(playlists)
    item = {
        'label': '[Next page >]',
        'path': plugin.url_for('top_playlists', page = str(int(page) + 1))
    }
    items.append(item)
    return items

@plugin.route('/my_playlists/')
def my_playlists():
    playlists = getApi().getPlaylists()
    return processPlaylists(playlists)

def processPlaylists(playlists):
    items = []
    for playlist in playlists:
        item = ListItem()
        item.set_label(playlist['name'])
        item.set_thumbnail(playlist['images']['large'])
        item.set_path(plugin.url_for('playlist', playlist_id = str(playlist['playlistId'])))
        item.set_info('music', {
            'Album': playlist['name'],
            'TrackNumber': playlist['itemsCount']
        })
        items.append(item)
    return items

@plugin.route('/playlist/<playlist_id>/')
def playlist(playlist_id):
    playlist = getApi().getPlaylist(playlist_id)
    items = []
    for track in playlist['content']:
        item = ListItem()
        item.set_label('%s - %s' % (track['artistName'], track['trackName']))
        item.set_thumbnail(track['imageLarge'])
        item.set_path(plugin.url_for('play',
            artist = track['artistName'].encode('utf-8'),
            track = track['trackName'].encode('utf-8'))
        )
        item.set_is_playable(True)
        try:
            item.set_info('music', {
                'Duration': track['durationSec'],
                'Title': track['trackName'],
                'Artist': track['artistName'],
                'TrackNumber': track['position'],
            })
        except:
            pass

        # Support Track Downloading
        item.add_context_menu_items([(
            plugin.get_string(30007),
            'XBMC.RunPlugin(' + plugin.url_for('download',
                artist = track['artistName'].encode('utf-8'),
                track = track['trackName'].encode('utf-8')) + ')'
        )])

        items.append(item)
    return items

@plugin.route('/play/<artist>/<track>/')
def play(artist, track):
    data = getTrack(artist, track)
    item = ListItem()
    item.set_label('%s - %s' % (artist, track))
    item.set_path(data['url'])
    item.set_played(True)
    xbmcplugin.setResolvedUrl(plugin.handle, True, item.as_xbmc_listitem())

@plugin.route('/download/<artist>/<track>/')
def download(artist, track):
    data = getTrack(artist, track)
    loader = downloader.SimpleDownloader()
    params = {
        'url': data['url'],
        'download_path': plugin.get_setting('Download Path')
    }
    loader.download('%s - %s.mp3' % (artist, track), params)

def getTrack(artist, track):
    storageKey = '%s - %s' % (artist, track)
    storage = plugin.get_storage('tracks')
    data = storage.get(storageKey)
    if not data:
        data = getApi().getTrack(artist, track)
        storage.update({storageKey: data})
    return data

def getApi():
    cookiepath = os.path.join(plugin.storage_path, plugin.id + '.lwp')
    return TracksFlow(cookiepath, plugin.get_setting('Login'), plugin.get_setting('Password'))

if __name__ == '__main__':
    plugin.run()
