#!/usr/bin/env python3

import argparse
import os
import json
import logging

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client import tools
from apiclient.discovery import build
from httplib2 import Http
import youtube_dl

YOUTUBE_SCOPE = 'https://www.googleapis.com/auth/youtube.force-ssl'

parser = argparse.ArgumentParser(parents=[tools.argparser])
flags = parser.parse_args()

logger = logging.getLogger('auto-yt-dl')


def set_logger():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '[%(asctime)s] [%(name)s / %(levelname)s] %(message)s',
        '%H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
set_logger()


def get_playlist(http, filter_fn):
    logger.debug('Getting playlists from youtube')
    youtube = build('youtube', 'v3', http=http)
    pl_list = youtube.playlists().list
    response = pl_list(part='id,snippet', mine=True).execute()
    result = []

    while 'nextPageToken' in response:
        logger.debug('Have next page token.')
        result += response['items']
        response = pl_list(part='id,snippet', mine=True,
                           pageToken=response['nextPageToken']).execute()
    logger.debug('This is the last page of playlists.')
    result += response['items']

    logger.debug('Get playlists from youtube ends.')
    return filter(filter_fn, result)


def list_playlist(http, playlists):
    """List playlist.
    return: dict. key = playlist title. value = array of ids."""
    logger.debug('Listing playlists.')
    youtube = build('youtube', 'v3', http=http)
    endpoint = youtube.playlistItems().list

    result_id = {}
    result_vid_id = {}

    def map_vid(x):
        return x['snippet']['resourceId']['videoId']

    for playlist in playlists:
        title = playlist['snippet']['title']
        result_id[title] = []
        result_vid_id[title] = []
        logger.debug('Processing playlist: %s', title)

        response = endpoint(part='id,snippet',
                            playlistId=playlist['id']).execute()

        while 'nextPageToken' in response:
            logger.debug('Have next page token.')

            result_id[title] += list(map(lambda x: x['id'], response['items']))
            result_vid_id[title] += list(map(map_vid, response['items']))

            response = endpoint(part='id,snippet', playlistId=playlist['id'],
                                pageToken=response['nextPageToken']).execute()

        result_id[title] += list(map(lambda x: x['id'], response['items']))
        result_vid_id[title] += list(map(map_vid, response['items']))

        logger.debug('Process of playlist "%s" ends', title)

    logger.debug('Playlists listed. Result:')
    logger.debug(result_id)
    return (result_id, result_vid_id)


def remove_playlist(http, playlist):
    if not playlist:
        return

    youtube = build('youtube', 'v3', http=http)
    endpoint = youtube.playlistItems().delete

    for item in playlist:
        endpoint(id=item).execute()


def download_videos(video_ids, dir, options):
    os.chdir(os.path.expanduser(dir))
    video_links = ['http://www.youtube.com/watch?v=' + video_id
                   for video_id in video_ids]
    logger.info('Attempting to download videos. %s', video_links)
    logger.info('Video will be saved to %s', os.path.expanduser(dir))

    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download(video_links)


def main():
    logger.info('Started')
    storage = Storage('credentials')
    creds = storage.get()

    if not creds or creds.invalid:
        flow = flow_from_clientsecrets('client_id.json',
                                       scope=YOUTUBE_SCOPE)
        flow.params['access_type'] = 'offline'
        creds = tools.run_flow(flow, storage, flags)
        storage.put(creds)

    http = creds.authorize(Http())

    with open('config.json') as file:
        config = json.load(file)
    look_playlist = list(config.keys())
    logger.info('I will look for for playlists: {0}'.format(look_playlist))

    playlists = get_playlist(http, lambda x: x['snippet']['title']
                             in look_playlist)
    pl_id, video_id = list_playlist(http, playlists)

    for name, setting in config.items():
        logger.info('Processing video in %s', name)
        if not video_id[name]:
            logger.info('No video found. Passing.')
            continue
        download_videos(video_id[name], setting['dest'], setting['options'])
        logger.info('Done. Cleaning videos from playlist.')
        remove_playlist(http, pl_id[name])
        logger.info('Clean completed.')


if __name__ == '__main__':
    main()
