import praw
import spotipy
import spotipy.util as util
import re
import time


# Songs should be in the format:
# (Artist) - (Song)
# Therefore splitting at '-' and stripping whitespace
# Should give us a valid song title

def valid_artist_and_song(title, media):
  if '-' in title:
      if len(title) <= 80:
          if 'type' in media.keys():
              if media['type'] == 'youtube.com':
                  return True
  return False

# Function checks for non-BMP range characters
def non_BMP_check(title):
    return all(ord(char) in range(65535) for char in title)

# Checks to see if the title contains a 'Track Id' request
def track_id_check(title):
    return not ('TRACK ID' in title.upper() or 'TRACKID' in title.upper())


def check_duplicate_track_id(spotify, id, username, track_id):
    results = spotify.user_playlist_tracks(username, playlist_id=id)
    return (track_id in str(results))

def last_occurance_index(string, item):
    return len(string) - 1 - string[::-1].index(item)

def next_occurance_index(string, index, item):
    return string[index:].index(item) + 1 + index

# Tracks can not be found based on extra info being added on the end
# Be it dates or just plaintext that can obscure search
def remove_label(title):
    if '[' in title and ']' in title:
        title = re.sub('\[([a-zA-Z0-9]|\W)*\]', '', title)
    return title

def remove_date(title):
    if '(' in title and ')' in title:
        title = re.sub('\([0-9]*\)', '', title)
    return title

# Last case if things can't be found usually because of extra info
def remove_extra_info(title):
    if '(' in title and ')' in title:
        title = re.sub('\(([a-zA-Z0-9]|\W)*\)', '', title)
        title = remove_extra_info(title)
    return title


def spotify_search_and_add(spotify, titles, playlist_id, username):
    unfounds = []
    for title in titles:
        results = spotify.search(q=title, type='track', limit=1)['tracks']['items']
        if len(results) != 0:
            track_id = 'spotify:track:' + str(results).split('spotify:track:')[1].split("'")[0]
            duplicate = check_duplicate_track_id(spotify, playlist_id, username, track_id)
            if not duplicate:
                results = spotify.user_playlist_add_tracks(username, playlist_id, [track_id])
        else:
            unfounds.append(title)
    return unfounds

def main():
    # All reddit api info
    reddit = praw.Reddit('bot')
    subreddit = reddit.subreddit('House')

    # All spotify api info
    scope = 'playlist-modify-public'
    username = 'ry2gg4eh81ep1v42b1r6mubtw'
    token = util.prompt_for_user_token(username, scope,
                                       client_id='1f6597e91b714ae4abe73a175b8a76d2',
                                       client_secret='689d718acb5349ae8856f21bbd518437',
                                       redirect_uri='http://localhost/')
    spotify = spotipy.Spotify(auth=token)
    top_month_id = '4Bb3DFSGOgamSYfnKpVJ8S'
    top_all_id = '3qImki1ZEdujDkcrlCY9QB'
    while True:
        titles = []
        for submission in subreddit.top('month', limit=None):
            if (submission.media is not None
                and valid_artist_and_song(submission.title,
                                          submission.media)
                and submission.score >= 10
                and non_BMP_check(submission.title)
                and track_id_check(submission.title)):

                titles.append(submission.title)
        unfounds = spotify_search_and_add(spotify, titles, top_month_id, username)
        # Remove (Date) and [Label] common tags from unfound list
        unfounds = list(map(remove_date, list(map(remove_label, unfounds))))
        unfounds = spotify_search_and_add(spotify, unfounds, top_month_id, username)
        # Remove (Extra Info) common tags from unfound list
        unfounds = list(map(remove_extra_info, unfounds))
        unfounds = spotify_search_and_add(spotify, unfounds, top_month_id, username)
        for submission in subreddit.top('all', limit=None):
            if (submission.media is not None
                and valid_artist_and_song(submission.title,
                                          submission.media)
                and submission.score >= 50
                and non_BMP_check(submission.title)
                and track_id_check(submission.title)):

                titles.append(submission.title)
        unfounds = spotify_search_and_add(spotify, titles, top_all_id, username)
        # Remove (Date) and [Label] common tags from unfound list
        unfounds = list(map(remove_date, list(map(remove_label, unfounds))))
        unfounds = spotify_search_and_add(spotify, unfounds, top_all_id, username)
        # Remove (Extra Info) common tags from unfound list
        unfounds = list(map(remove_extra_info, unfounds))
        unfounds = spotify_search_and_add(spotify, unfounds, top_all_id, username)
        time.sleep(3600)



if __name__ == '__main__':
  """Boilerplate main function call"""
  main()
