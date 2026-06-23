# Media Bias Detection

![Python](https://img.shields.io/badge/PYTHON-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/STREAMLIT-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/PANDAS-150458?style=for-the-badge&logo=pandas&logoColor=white)

This project identifies potential bias in news channels by analyzing the titles, descriptions, and caption summaries of their YouTube videos. By examining these elements, it surfaces insights into the presence and direction of bias across different news channels.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Step 1 — Get video IDs for a channel
Run `scripts/get_video_ids.py` to scrape video IDs for the latest videos from a specified news channel. IDs are saved as a text file in `data/video_id`.

### Step 2 — Scrape video information
Add your YouTube API key to `scripts/input_config.py`. Then run `scripts/scrape_data.py`, passing in the video ID file from `data/video_id` and a date range to filter by.

- Video data is saved as CSV in `data/video_info`
- Logs are saved in `data/logs`

### Step 3 — Check for videos that failed to scrape
Run `scripts/check_missing_video_id.py` to find video IDs that weren't successfully scraped. Missing IDs are saved to `data/video_id`. Repeat Step 2 for those videos, then run `scripts/merge.py` to merge the new results into the original CSV.

### Step 4 — Filter for political content
Run `scripts/filter.py` on a video info file from `data/video_info` to classify each video as political or non-political. Update the cleaning regex as needed for your dataset. Filtered output is saved to `data/filter`.

### Step 5 — Cluster videos and identify top performers
Run `scripts/clustering_captions.py` on a filtered CSV from `data/filter`. This produces three outputs:

| Output | Description | Location |
|---|---|---|
| Cluster data | Political content tagged with cluster IDs | `data/cluster/cluster_data` |
| Cluster centers | Cluster centers and their dominant topics | `data/cluster/cluster_center` |
| Top 3 per cluster | Top 3 videos per cluster by engagement (70% likes, 30% views), including captions | `data/cluster/top3` |

### Step 6 — Generate insights
- `scripts/get_insights_tdc.py` — insights from title + description + captions → `data/insights/title_desc_cap`
- `scripts/get_insights_td.py` — insights from title + description only → `data/insights/title_desc`

## Tech stack

- **Language:** Python
- **Data processing:** Pandas, NumPy
- **Dashboard:** Streamlit
- **APIs:** YouTube Data API v3
