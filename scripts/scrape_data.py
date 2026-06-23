
import logging
from YoutubeParser import YoutubeParser
import os
import pandas as pd
log_file = 'data/logs/hi_ndtv_india.log'
txt_file_name = 'data/video_id/hi_ndtv_india.txt'
output_dir_csv = 'data/video_info'

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(filename=log_file),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

# Extract video ID from YouTube URL
def extract_video_id(url):
    if 'v=' in url:
        return url.split('v=')[1]
    elif '/' in url:
        return url.split('/')[-1]
    return None

def main():
    # Load video IDs from the text file
    with open(txt_file_name, 'r') as f:
        video_ids = f.read().splitlines()

    # Path to the existing CSV file where scraped data is stored
    file = os.path.splitext(os.path.basename(txt_file_name))[0]
    csv_output_file = f"{file}.csv"
    output_file_path = os.path.join(output_dir_csv, csv_output_file)

    # Initialize YouTubeParser and load existing scraped data
    youtube_parser = YoutubeParser()

    # Load existing data to identify previously scraped videos
    if os.path.exists(output_file_path):
        df_existing = pd.read_csv(output_file_path)
        scraped_video_ids = set(df_existing['url'].apply(extract_video_id))
    else:
        df_existing = pd.DataFrame()
        scraped_video_ids = set()

    # Temporary list to store information for new videos
    scraped_data = []

    print('## Data Scraping Started for Unscraped Videos!')

    # Scrape new videos
    for idx, video_id in enumerate(video_ids):
        if video_id in scraped_video_ids:
            logger.info(f"Video ID {video_id} is already scraped. Skipping.")
            continue

        link = f'https://www.youtube.com/watch?v={video_id}'
        logger.info(f"Processing link {idx + 1}/{len(video_ids)}: {link}")

        try:
            # Parse the video information
            info = youtube_parser.parse(url=link, output_dir_csv=None, csv_output_file=None, log_file=log_file)  # Avoids auto-saving
            
            if info is None:
                logger.error(f"Failed to scrape video information for URL: {link}")
            else:
                scraped_data.append(info)
                logger.info(f"Video info for {link}: Temporarily stored.")
        
        except Exception as e:
            logger.error(f"Error processing URL {link}: {e}")
            logger.exception(f"Error traceback: {e}")

    # If there’s new data, append it to the main CSV file
    if scraped_data:
        df_new = pd.DataFrame(scraped_data)
        if not df_existing.empty:
            # Combine existing and new data
            df_combined = pd.concat([df_existing, df_new]).drop_duplicates(subset='url')
        else:
            # No existing data, so just use new data
            df_combined = df_new

        df_combined.to_csv(output_file_path, index=False, quoting=1)
        print(f"## New Data Appended to {output_file_path}!")
    else:
        print("No new data to scrape.")

    print("## Data Scraping Completed!")

if __name__ == "__main__":
    main()
