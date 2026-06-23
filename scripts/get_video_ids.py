'''
    This script gets a given number of video ids for latest videos from a particular youtube channel and stores them in a txt file
'''
import os
import googleapiclient.discovery
import googleapiclient.errors
from datetime import datetime

# Define your API key and channel ID
api_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
channel_id = 'UC9CYT9gSNLevX5ey2_6CK0Q'

# Define your date range
start_date = datetime.strptime('2024-04-19', '%Y-%m-%d')
end_date = datetime.strptime('2024-06-01', '%Y-%m-%d')

# Build the YouTube API client
def build_youtube_client(api_key):
    return googleapiclient.discovery.build('youtube', 'v3', developerKey=api_key)

# Fetch video IDs from the channel
def fetch_video_ids(youtube, channel_id):
    video_ids = []
    request = youtube.playlistItems().list(
        part='snippet',
        playlistId='UU' + channel_id[2:],  # Use the channel ID to get the playlist ID
        maxResults=50
    )

    while request is not None:
        response = request.execute()
        
        for item in response['items']:
            video_id = item['snippet']['resourceId']['videoId']
            video_date = datetime.strptime(item['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
            if start_date <= video_date <= end_date:
                video_ids.append(video_id)

        request = youtube.playlistItems().list_next(request, response)

    return video_ids

# Save video IDs to a file
def save_video_ids_to_file(video_ids, filename):
    with open(filename, 'w') as file:
        for video_id in video_ids:
            file.write(f"{video_id}\n")

def main():
    youtube = build_youtube_client(api_key)
    video_ids = fetch_video_ids(youtube, channel_id)
    save_video_ids_to_file(video_ids, 'filtered_video_ids.txt')
    print(f"Filtered video IDs have been saved to 'filtered_video_ids.txt'.")

if __name__ == '__main__':
    main()
