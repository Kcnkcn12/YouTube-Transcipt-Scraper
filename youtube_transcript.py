# pip install google-api-python-client
# or the instructions here https://github.com/googleapis/google-api-python-client#installation
from googleapiclient.discovery import build

# pip install youtube_transcript_api
# or the instructions here https://github.com/jdepoix/youtube-transcript-api#install
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# pip install requests
import requests

import os       # for os.path.abspath() because idk where my output file is

######################################

#!!!!!!!!!!! FILL THIS IN !!!!!!!!!!!#

# post your youtube api key (get it from here https://developers.google.com/youtube/v3/getting-started)
youTubeApiKey = 'API_key_here' # or import from another file

# post the channel url
channel_url = 'channel_url_here'

# name of file to write to
file_name = 'transcripts.txt'

# transcript languages
transcript_language = ['en', 'en-GB'] # e.g. grabs American English or UK English in that order

######################################

# choose youtube api to connect to
youtube = build('youtube', 'v3', developerKey = youTubeApiKey)

# get channel id from url
channel_id = ''
if 'youtube.com/user/' in channel_url:
    channel_username = channel_url.split("/")[-1]
    channel_username_response = youtube.channels().list(part = 'id', forUsername = channel_username).execute()
    channel_id = channel_username_response['items'][0]["id"]
elif 'youtube.com/channel/' in channel_url:
    channel_id = channel_url.split("/")[-1]
elif 'youtube.com/c/' in channel_url:
#    print('YouTube\'s API does not (and will not) support urls with the format: youtube.com/c/custom_url')
#    print('Google\'s response: https://issuetracker.google.com/issues/165676622.')
#    print('As a workaround, please go to the channel, click on any video, then click on the channel name.')
#    print('The url will now be of the format "youtube.com/channel/channel_id" and can be used.')
#    exit()

    # script workaround: scrape channel id from webpage
    channel_page_content = requests.get('https://www.youtube.com/c/inanutshell')
    channel_id = channel_page_content.text.split("channel_id=")[1].split("\"")[0]

else:
    print('unknown url format')
    exit()

# get list of the channel's videos' id
# saved in video_id_list
channel_response = youtube.channels().list(part = 'contentDetails, snippet', id = channel_id).execute()
videos = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

video_id_and_name_list = []
playlist_response = youtube.playlistItems().list(part = 'snippet', playlistId = videos, maxResults = 50).execute()
for item in playlist_response['items']:
    video_id_and_name_list.append((item['snippet']['resourceId']['videoId'], item['snippet']['title']))
while 'nextPageToken' in playlist_response:
    playlist_response = youtube.playlistItems().list(part = 'snippet', playlistId = videos, maxResults = 50, pageToken = playlist_response['nextPageToken']).execute()
    for item in playlist_response['items']:
        video_id_and_name_list.append((item['snippet']['resourceId']['videoId'], item['snippet']['title']))

# get transcript of videos and write to file
file = open(file_name, 'w', encoding='utf-8')

file.write(channel_response['items'][0]['snippet']['title'])    # channel name
file.write('\n\n')

for video_id, video_name in video_id_and_name_list:
    file.write('============================================================================================\n')
    file.write(video_name)
    file.write('\n')
    file.write('https://www.youtube.com/watch?v=')
    file.write(video_id)
    file.write('\n\n')
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages = transcript_language)
        formatter = TextFormatter()
        formatted_transcript = formatter.format_transcript(transcript)  # converts transcript response into text

        file.write(formatted_transcript)

        print(video_id, ': success')
    except BaseException as e:
        print('Failed to do something: ' + str(e))
        file.write('<no transcript>')

    file.write('\n')
file.close()

print('done')
print('the file is located at', os.path.abspath(file_name))