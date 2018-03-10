"""
Automatically download youtube video from given playlist.

See README.md for setup details.
"""

import json
import logging
import os
import sys

import youtube_dl
from apiclient.discovery import build
from httplib2 import Http
from youtube_dl.utils import DEFAULT_OUTTMPL

from autodl import auth

LOCK_FILE = 'auto-yt-dl.lock'
YOUTUBE_SCOPE = 'https://www.googleapis.com/auth/youtube.force-ssl'
THIS_DIR = os.getcwd()

logger = logging.getLogger('auto-yt-dl')


def set_logger():
    """Set up logger handlers."""
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '[%(asctime)s] [%(name)s / %(levelname)s] %(message)s', '%H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def get_playlist(http, filter_fn):
    """
    Get playlist items from youtube.

    Param:
        http - urllib http object that is authorized
        filter_fn - Filter function for list
    """
    logger.debug('Getting playlists from youtube')
    youtube = build('youtube', 'v3', http=http)
    pl_list = youtube.playlists().list
    response = pl_list(part='id,snippet', mine=True).execute()
    result = []

    while 'nextPageToken' in response:
        logger.debug('Have next page token.')
        result += response['items']
        response = pl_list(
            part='id,snippet', mine=True,
            pageToken=response['nextPageToken']).execute()
    logger.debug('This is the last page of playlists.')
    result += response['items']

    logger.debug('Get playlists from youtube ends.')
    return filter(filter_fn, result)


def list_playlist(http, playlists):
    """
    List playlist.

    Returns:
        dict. key = playlist title. value = array of ids.

    """
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

        response = endpoint(
            part='id,snippet', playlistId=playlist['id']).execute()

        while 'nextPageToken' in response:
            logger.debug('Have next page token.')

            result_id[title] += list(map(lambda x: x['id'], response['items']))
            result_vid_id[title] += list(map(map_vid, response['items']))

            response = endpoint(
                part='id,snippet',
                playlistId=playlist['id'],
                pageToken=response['nextPageToken']).execute()

        result_id[title] += list(map(lambda x: x['id'], response['items']))
        result_vid_id[title] += list(map(map_vid, response['items']))

        logger.debug('Process of playlist "%s" ends', title)

    logger.debug('Playlists listed. Result:')
    logger.debug(result_id)
    return result_id, result_vid_id


def remove_playlist(http, playlist):
    """
    Clean up videos inside a youtube playlist.

    Param:
        playlist - Playlist id to be cleaned
    """
    if not playlist:
        return

    youtube = build('youtube', 'v3', http=http)
    endpoint = youtube.playlistItems().delete

    for item in playlist:
        endpoint(id=item).execute()


def normalize_path(path):
    """Normalize a path."""
    p = os.path.expanduser(path)
    p = os.path.normpath(p)
    p = os.path.join(p, '')
    return p


def download_videos(video_ids, dir_, options):
    """
    Download videos from youtube.

    Param:
        video_ids - ID of videos to download
        dir_ - Target directory
        options - Options for youtube-dl
    """
    options['outtmpl'] = os.path.join(
        normalize_path(dir_), options.get('outtmpl', DEFAULT_OUTTMPL))
    video_links = [
        'http://www.youtube.com/watch?v=' + video_id for video_id in video_ids
    ]
    logger.info('Attempting to download videos. %s', video_links)
    logger.info('Video will be saved as %s', options['outtmpl'])

    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download(video_links)


def main():
    """Entry point of the script."""
    set_logger()

    logger.info('Started')

    creds = auth.get_cred()
    http = creds.authorize(Http())

    with open('config.json') as file:
        config = json.load(file)
    look_playlist = list(config.keys())
    logger.info('I will look for for playlists: {0}'.format(look_playlist))

    playlists = get_playlist(http,
                             lambda x: x['snippet']['title'] in look_playlist)
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
    if LOCK_FILE in os.listdir():
        logger.info('Lock file found. Exiting.')
        sys.exit(0)
    open(LOCK_FILE, 'a').close()
    try:
        main()
    finally:
        logger.info('Cleaning up lock file.')
        os.remove(os.path.join(THIS_DIR, LOCK_FILE))

