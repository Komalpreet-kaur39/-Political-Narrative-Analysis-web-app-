# Media Bias Detection (YouTube Header Analysis)

## Description

This project aims to identify potential biases in news channels by analyzing the titles, descriptions, and caption summaries of their YouTube videos. By examining these elements, we can gain insights into the presence and direction of bias in the content produced by various news channels.

## Installation

To install the required dependencies, use the following command:

```bash
pip install -r requirements.txt
```

## Usage

### Step 01: Get Video IDs for a YouTube Channel
We have a script located at `/scripts/get_video_ids.py` that scrapes video IDs for a number of the latest videos from a specified news channel and stores them in a text file in the `/data/video_id` directory.

### Step 02: Scrape Information for the Videos
Keep your YouTube API key in `/scripts/input_config.py`. Then, run the script `/scripts/scrape_data.py`, providing the input path for the text file with video IDs from `/data/video_id` and specifying the date range for which the data needs to be filtered. 

The video information will be stored in CSV format in the `/data/video_info` directory. The logs for the process will be stored in a log file in the `/data/logs` directory.

### Step 03: Check for Videos That Were Not Scraped
Run the script at `/scripts/check_missing_video_id.py` to get the video IDs for which the information was not scraped. The missing video IDs will be stored in a text file in the `/data/video_id` directory. Then, follow Step 02 again for the failed videos. Run `/scripts/merge.py` to merge the new CSV with the original CSV.

### Step 04: Filter Data Based on Political Content
Run the script `/scripts/filter.py` to classify each video as political or non-political, providing the input path for the video information file stored at `/data/video_info`. Do not forget to change the regular expression for cleaning description based as per needs. The filtered data will be saved in CSV format in the `/data/filter` directory.

### Step 05: Cluster the Filtered Data and Get Top 3 Videos with Video Captions Based on Engagement
Run the script `/scripts/clustering_captions.py`, passing the filtered data CSV from `/data/filter` as input. The output will be in the form of three CSV files:

1) Political content with cluster IDs stored in `/data/cluster/cluster_data`.
2) Cluster centers and their topics stored in `data/cluster/cluster_center`.
3) Top 3 videos from each cluster based on engagement, which is a weighted average of 70% likes and 30% views, stored in `data/cluster/top3`. This CSV will also include the captions for the top 3 videos per cluster.

### Step 06: Get Insights Using Video Information
Run the script `/scripts/get_insights_tdc.py` to get insights using the title, description, and captions for the top 3 videos of each cluster stored in `/data/cluster/top3`. The insights will be stored in a CSV file in `/data/insights/title_desc_cap`.

Run the script `/scripts/get_insights_td.py` to get insights using the title and description for the top 3 videos of each cluster stored in `/data/cluster/top3`. The insights will be stored in a CSV file in `/data/insights/title_desc`.