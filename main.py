import praw
import spotipy
import spotipy.util as util
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

def non_BMP_check(title):
    return all(ord(char) in range(65535) for char in title)



def main():
    reddit = praw.Reddit('bot')

    subreddit = reddit.subreddit('House')


    scope = 'user-library-read'
    #token = util.prompt_for_user_token('ry2gg4eh81ep1v42b1r6mubtw', scope,
                                       #client_id='1f6597e91b714ae4abe73a175b8a76d2',
                                       #client_secret='689d718acb5349ae8856f21bbd518437')
    spotify = spotipy.Spotify()

    
    titles = []
    for submission in subreddit.top('month', limit=None):
        if (submission.media is not None
            and valid_artist_and_song(submission.title,
                                      submission.media)
            and submission.score >= 5
            and non_BMP_check(submission.title)):

            titles.append(submission.title)

    results = spotify.search(q=titles[0], type='track')
    print(results)
    


if __name__ == '__main__':
    main()
