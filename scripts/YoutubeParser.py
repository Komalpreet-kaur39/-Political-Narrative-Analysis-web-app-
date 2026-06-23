'''
    This scripts scraps information for videos and store them in a csv file
'''

import logging
import os
import json
import csv
import input_config
from googleapiclient.errors import HttpError
from pytube import YouTube
from pytube.exceptions import VideoUnavailable

logger = logging.getLogger(__name__)

class YoutubeParser:
    def __init__(self):
        from googleapiclient.discovery import build
        self.youtube = build(
            "youtube",
            "v3",
            developerKey=input_config.YOUTUBE_API_KEY,
        )
        self.url = ''
        self.url_id = ""
        self.text = None

    # Scrap video information
    def get_video_info(self):
        try:
            my_video = YouTube(self.url)
        except Exception as e_video:
            logger.error(f"Error creating YouTube object: {e_video}")
            my_video = None

        try:
            title = my_video.title
            publish_date = my_video.publish_date.date() if my_video.publish_date else None
            length = my_video.length
        except AttributeError as e_attr:
            logger.error(f"Error retrieving video information: {e_attr}")
            title, publish_date, length = "", None, None

        try:
            video = (
                self.youtube.videos()
                .list(part="snippet,statistics", id=self.url_id)
                .execute()
            )
            items = video.get("items", [])
            if not items:
                return None
                # raise ValueError("No video information found for the given URL ID")

            snippet = items[0]["snippet"]
            statistics = items[0]["statistics"]

            video_info = {
                "channel_name": snippet.get("channelTitle", "Unknown Channel"),
                "likes": statistics.get("likeCount", 0),
                "comments": statistics.get("commentCount", 0),
                "views": statistics.get("viewCount", 0),
                "description": snippet.get("description", ""),
                "title": title,
                "publish_date": publish_date,
                "length": length,
            }

            return video_info
        
        except HttpError as e:
            error_content = e.content.decode('utf-8')
            logger.error(f"HTTP error fetching video information: {error_content}")
            if 'quotaExceeded' in error_content:
                return "quota_exceeded"
            raise e
        
        except VideoUnavailable as e_private:
            logger.error(f"Private video: {self.url}. Error: {e_private}")
            raise e_private  # Reraise the exception to handle in main.py
        

        except Exception as e:
            logger.error(f"Error fetching video information: {e}")
            return None

    # Save the scraped information to a csv file
    def save_to_csv(self, data, csv_output_file, fieldnames):
    
        os.makedirs(os.path.dirname(csv_output_file), exist_ok=True)

        with open(csv_output_file, "a", encoding="utf-8", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if f.tell() == 0:
                writer.writeheader()

            writer.writerow(data)
            logger.info(f"Video information saved to {csv_output_file}")

    # Create a log for the entire scraping process
    def log_failed_urls(self, url, log_file):
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"Failed to scrape video information for URL: {url}\n")
            logger.info(f"Logged failed URL: {url}")

    # parse the video urls to get video information
    def parse(self, url: str, output_dir_csv: str = ".", csv_output_file: str = "scraped_data.csv", log_file: str = "log_data.log"):
        from urllib.parse import parse_qs, urlparse

        self.url = url
        parsed_url = urlparse(self.url)
        query_parameters = parse_qs(parsed_url.query)
        self.url_id = query_parameters.get("v", [None])[0]

        if not self.url_id:
            logger.error("No video ID found in the URL")
            return None

        logger.info("Trying to get video info")
        try:
            video_info = self.get_video_info()
            if video_info=="quota_exceeded":
                return "quota_exceeded"
        except HttpError as e:
            with open(log_file, "a", encoding="utf-8") as log_f:
                log_f.write(f"HTTP error fetching video information for URL {url}: {e}\n")
            logger.error(f"Quota exceeded for URL: {url}. Stopping script.")
            return "quota_exceeded"
        
        except Exception as e:
            self.log_failed_urls(url, log_file)
            return None


        data = {
            "url": self.url,
            "title": video_info["title"],
            "publish_date": str(video_info["publish_date"]),
            "authors": video_info["channel_name"],
            "length": video_info["length"],
            "likes": video_info["likes"],
            "comments": video_info["comments"],
            "views": video_info["views"],
            "description": video_info["description"],
        }

        # Save to CSV
        csv_output_path = os.path.join(output_dir_csv, csv_output_file)
        fieldnames = ["url", "title", "publish_date", "authors", "length", "likes", "comments", "views", "description"]
        self.save_to_csv(data, csv_output_path, fieldnames)

        return data