import pandas as pd

# Get all video ids for the channel
video_ids_file_path = 'data/video_id/hi_ndtv_india.txt'

with open(video_ids_file_path, 'r') as file:
    video_ids = [line.strip() for line in file.readlines()]

# Get the csv containing scraped video information
csv_file_path = 'data/video_info/hi_ndtv_india.csv'

df = pd.read_csv(csv_file_path)

df['video_id'] = df['url'].apply(lambda x: x.split('=')[-1])

# Find missing video ids
missing_video_ids = [vid_id for vid_id in video_ids if vid_id not in df['video_id'].values]

print("--"*30)
print("Missing video IDs:", missing_video_ids)
print(len(missing_video_ids))
print("--"*30)

# Path to save missing video ids
output_file_path = 'data/video_id/failed_videos.txt'

with open(output_file_path, 'w') as file:
    for video_id in missing_video_ids:
        file.write(f"{video_id}\n")