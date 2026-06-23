# '''
# #     This script classifies videos as political and non-political based on a threshold value.
# # '''

import pandas as pd
import re
from transformers import pipeline
import csv
import os

# Function to clean description
def clean_description(description):
    if pd.isna(description):
        return ""
    description = re.sub(r'http\S+', '', description)  # Remove URLs
    description = re.split(r'About NDTV India|NDTV इंडिया', description)[0]  # Remove specific phrases
    description = re.sub(r'#\S+', '', description)  # Remove hashtags
    description = description.replace('\n', ' ').replace('\r', '').strip()  # Remove newlines
    description = re.sub(r'\s+', ' ', description)  # Collapse multiple spaces
    return description

# Function to sanitize filenames
def sanitize_filename(title):
    return re.sub(r'[<>:"/\\|?*]', '_', title)

# File paths
input_file_path = 'data/video_info/hi_ndtv_india.csv'
output_file_path = os.path.join(
    'data/filter',
    sanitize_filename(os.path.basename(os.path.splitext(input_file_path)[0])) + '_filter.csv'
)

# Load input data
info_data = pd.read_csv(input_file_path)
info_data['cleaned_description'] = info_data['description'].apply(clean_description)

# Load existing classified data if output file exists
if os.path.exists(output_file_path):
    classified_data = pd.read_csv(output_file_path)
    already_classified_ids = set(classified_data['video_id']) if 'video_id' in classified_data.columns else set(classified_data['title'].apply(lambda x: x.strip().lower()))
else:
    classified_data = pd.DataFrame()
    already_classified_ids = set()

# Initialize classification model
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Define candidate labels
candidate_labels = ['political', 'non political']

# Open output file in append mode
with open(output_file_path, 'a', newline='', encoding='utf-8') as csvfile:
    fieldnames = list(info_data.columns) + ['political', 'non political', 'topic']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write header if the output file is new
    if csvfile.tell() == 0:
        writer.writeheader()

    # Iterate over input data
    for index, row in info_data.iterrows():
        unique_id = row['video_id'] if 'video_id' in row else row['title'].strip().lower()

        # Check if the video has already been classified
        if unique_id in already_classified_ids:
            print(f"Skipping already classified video: {row['title']}")
            continue

        # Prepare text for classification
        text = row['title'] + '\n' + row['cleaned_description']
        
        try:
            # Perform classification
            cl = classifier(text, candidate_labels)
            political_score = cl['scores'][cl['labels'].index('political')]
            non_political_score = cl['scores'][cl['labels'].index('non political')]
            topic = 'political' if political_score > 0.8 else 'non political'

            result = row.to_dict()
            result.update({
                'political': political_score,
                'non political': non_political_score,
                'topic': topic
            })

            # Write classified result to file
            writer.writerow(result)
            print(f"Classified and saved video {index + 1}: {row['title']}")

        except Exception as e:
            print(f"Error processing {row['title']}: {e}")
            continue

print(f"## Classification complete. Filtered data saved to {output_file_path}")
