import praw
import spotipy
import spotipy.util as util
import re
import time
import os


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

# Checks to see the song isn't in the playlist already
def check_duplicate_track_id(spotify, id, username, track_id):
    results = spotify.user_playlist_tracks(username, playlist_id=id)
    return (track_id in str(results))


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

# Adds song if not already in playlsit
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
        # Sleep in an attmept to throttle Spotify API request rate
        time.sleep(0.1)
    return unfounds, spotify

def main():
    # All reddit api info
    reddit = praw.Reddit('bot')
    reddit = praw.Reddit(client_id=os.environ['REDDIT_CLIENT_ID'],
                     client_secret=os.environ['REDDIT_CLIENT_SECRET'],
                     password='',
                     user_agent='testscript by /u/fakebot3',
                     username='Reddit Music Bot 0.1')
    subreddit = reddit.subreddit('House')

    # All spotify api info
    scope = 'playlist-modify-public'
    username = os.environ['SPOTIFY_USERNAME']
    spotify_client_id = os.environ['SPOTIFY_CLIENT_ID']
    spotify_client_secret = os.environ['SPOTIFY_CLIENT_SECRET']
    token = util.prompt_for_user_token(username, scope,
                                       client_id=spotify_client_id,
                                       client_secret=spotify_client_secret,
                                       redirect_uri='http://localhost/')
    spotify = spotipy.Spotify(auth=token)
    top_month_id = os.environ['SPOTIFY_MONTHLY_ID']
    top_all_id = os.environ['SPOTIFY_ALL_ID']

    #Main App Loop
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
        unfounds, spotify = spotify_search_and_add(spotify, titles, top_month_id, username)
        # Remove (Date) and [Label] common tags from unfound list
        unfounds = list(map(remove_date, list(map(remove_label, unfounds))))
        unfounds, spotify = spotify_search_and_add(spotify, unfounds, top_month_id, username)
        # Remove (Extra Info) common tags from unfound list
        unfounds = list(map(remove_extra_info, unfounds))
        unfounds, spotify = spotify_search_and_add(spotify, unfounds, top_month_id, username)
        titles = []
        for submission in subreddit.top('all', limit=None):
            if (submission.media is not None
                and valid_artist_and_song(submission.title,
                                          submission.media)
                and submission.score >= 50
                and non_BMP_check(submission.title)
                and track_id_check(submission.title)):

                titles.append(submission.title)
        unfounds, spotify = spotify_search_and_add(spotify, titles, top_all_id, username)
        # Remove (Date) and [Label] common tags from unfound list
        unfounds = list(map(remove_date, list(map(remove_label, unfounds))))
        unfounds, spotify = spotify_search_and_add(spotify, unfounds, top_all_id, username)
        # Remove (Extra Info) common tags from unfound list
        unfounds = list(map(remove_extra_info, unfounds))
        unfounds, spotify = spotify_search_and_add(spotify, unfounds, top_all_id, username)
        # Waits an hour then refreshes
        time.sleep(3600)



if __name__ == '__main__':
  """Boilerplate main function call"""
  main()
