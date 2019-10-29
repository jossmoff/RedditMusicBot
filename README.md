# RedditMusicBot
[![MIT Licence](https://badges.frapsoft.com/os/mit/mit.png?v=103)](https://opensource.org/licenses/mit-license.php)
<a target="_blank" href="https://www.python.org/downloads/" title="Python version"><img src="https://img.shields.io/badge/python-%3E=_3.6-green.svg"></a>
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/88f50911dac94ce1bd113cff6dd1b379)](https://www.codacy.com/app/JossMoff/RedditMusicBot?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=JossMoff/RedditMusicBot&amp;utm_campaign=Badge_Grade)

🤖📻 A Reddit Music Bot template built for Heroku that automatically adds songs from subreddits to Spotify. It was built for subreddits like [r/House](https://www.reddit.com/r/House/) in order to automatically maintain a public spotify playlist under the community post guidlines.


## Setup

```bash
# Clone the repo
joss@moff:~$: git clone https://github.com/JossMoff/RedditMusicBot.git
```

Now you need to deploy in your Heroku Dashboard - I would **personally** recommend setting it up with GitHub and then enable automatic deploys for ease.

## Setting Heroku Enviroment Variables

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

You must set the values of these config vars in order for the deployment to work.
All you need to do is

 1. [Create A Reddit Developer Application](https://www.reddit.com/prefs/apps/)
 2. [Create a Spotify Developer Account and Project](https://developer.spotify.com/)
 3. Create 2 playlists 1 for All-Time and 1 for Monthly/Weekly
 4. Note down both API ID and Secret Keys aswell as the URI's for the playlists you have created.
 5. Follow [arska](https://github.com/arska)'s [tutorial](https://github.com/arska/srf2spotify#usage) for filling in the SPOTIPY_CACHE detials.
 6. Fill all these details in at  Heroku Dashboard > Settings

![enter image description here](https://lh3.googleusercontent.com/-JoMxbhxvUmBPMhRg-8WdjPXn0exa_sAALH7__m-UGT6egnN1hZit7mF2hUhAxRL_e-J86DI4rDo)
## How it works - Valid Title and Media
We work under the premise that every post that is a track submission contains the artist and track name in the title, usually in this format:
> (Artist) - (Title)

Hence we check if the title returned from the Reddit API contains a '-' and if it does is likely to be a song aslong as it has a media link associated with it aswell.

```python
def valid_artist_and_song(title, media):
  if '-' in title:
      if len(title) <= 80:
          if 'type' in media.keys():
              if media['type'] == 'youtube.com':
                  return True
  return False
```
## How it works - No Non-BMP characters
We cannot search using NON-BMP characters therefore we loop over the entirety of the title and do a range check to see if the Unicode code point of a given character is within the Basic Multilingual Plane range. If all of the are it is a valid title.
```python
    # Function checks for non-BMP range characters
    def non_BMP_check(title):
	    return all(ord(char) in range(65535) for char in title)
```

## How it works - Removing Extra Title Data
We do an inital search for all the initial titles that seem valid and then if we find the song on Spotify **GREAT!** However we are left with a bunch of titles that couldn't have songs associated with them. This can be down to a few things:

 - Addition Label ID usually of the form [J055]
 - Additional Year usually of the form (2001)
 - Any extra info e.g (USA, 2018)(Jossmoff Remix)

The first two are easily removed with a simple double function mapping as we would **always** want these removed

```python
def remove_label(title):
	if '[' in title and ']' in title:
		title = re.sub('\[([a-zA-Z0-9]|\W)*\]', '', title)
	return title

def remove_date(title):
	if '(' in title and ')' in title:
		title = re.sub('\([0-9]*\)', '', title)
	return title

unfounds = list(map(remove_date, list(map(remove_label, unfounds))))
```


 However the last one, if the info in the brackets e.g (Four Tet Remix) this is important as the user is specifically looking for the specific remix of the track. Therefore we apply the first two functions **seperately** and **before** we apply the last one so that we can identify as many songs as possible before having to remove potentially important data.

```python
def remove_extra_info(title):
    if '(' in title and ')' in title:
        title = re.sub('\(([a-zA-Z0-9]|\W)*\)', '', title)
        title = remove_extra_info(title)
    return title

unfounds = list(map(remove_extra_info, unfounds))
```
## Effectiveness

Using a heuristic to measure performance, out of all the posts the Reddit API returns we can not find only 1% of them. This is extremly marginal and could just be because alot aren't on Spotify.

Using a different heuristic to measure performance out of the posts the bot identifies as potential songs, we cannot find 11% of them. This is due to 3 main factors:

 - People adding extra, sometimes completely irrelevant text to the title e.g
 *(Song) - (Artist) ...... Groovy*
 - Tracks not being found on Spotify
 - Tracks not actually being correctly identified e.g *Live sets*

## Improvements

The key factors I aim to improve are:

 - 🕸️Filter out Livesets to improve search efficiency
 - 🤖Create an AI to more effectively search for the songs to improve effectiveness
 - 💣Add an auto remove function for the monthly playlist.
