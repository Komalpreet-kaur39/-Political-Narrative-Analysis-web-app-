import pandas as pd
import os

org_file_path = 'data/video_info/hi_ndtv.csv'

new_file_path = 'data/video_info/failed_videos.csv'

org_csv = pd.read_csv(org_file_path)
new_csv = pd.read_csv(new_file_path)

# Concatenate the two dataframes
merged_csv = pd.concat([org_csv, new_csv])

# Reset the index if needed (optional)
merged_csv.reset_index(drop=True, inplace=True)

# Save the merged dataframe to a new CSV file
merged_csv.to_csv(org_file_path, index=False)

if os.path.exists(new_file_path):
    os.remove(new_file_path)
