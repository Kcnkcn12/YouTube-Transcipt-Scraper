# pip install google-api-python-client
# or the instructions here https://github.com/googleapis/google-api-python-client#installation
from googleapiclient.discovery import build

# pip install youtube_transcript_api
# or the instructions here https://github.com/jdepoix/youtube-transcript-api#install
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

import os       # for os.path.abspath() because idk where my output file is

######################################

#!!!!!!!!!!! FILL THIS IN !!!!!!!!!!!#

# post your youtube api key (get it from here https://developers.google.com/youtube/v3/getting-started)
youTubeApiKey = 'api_key_here' # or import from another secure file
youtube = build('youtube', 'v3', developerKey = youTubeApiKey)  # choose youtube api to connect to

# post the channel id (https://www.youtube.com/channel/this_is_channel_id)
channel_id = 'channel_id_here'

# name of file to write to
file_name = 'transcripts.txt'

# transcript languages
transcript_language = ['en', 'en-GB'] # grabs American English or UK English in that order

######################################

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
    file.write('https://www.youtube.com/watch?v=')              # link to video
    file.write(video_id)                                        #
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