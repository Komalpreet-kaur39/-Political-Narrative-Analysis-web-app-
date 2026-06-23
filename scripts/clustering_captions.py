# '''
#     This script performs clustering on the data categorized as political.
#     Then it picks top 3 videos from each cluster based on its engagement (weighted average of 30% views and 70% likes).
#     Captions are then extracted for top 3 videos per cluster.
# '''

import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AffinityPropagation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from youtube_transcript_api import YouTubeTranscriptApi
import os

# Custom Hindi stopwords list
hindi_stopwords = [
    'और', 'द', 'व', 'क', 'ह', 'न', 'म', 'अ', 'स', 'त', 'उ', 'भ', 'ज', 'र', 'प',
    'ल', 'क', 'ह', 'स', 'म', 'न', 'व', 'ज', 'क', 'त', 'प', 'द', 'ग', 'स', 'व', 'ह',
    # Add more stopwords as needed
]
english_stopwords = ['the', 'is', 'in', 'and', 'to', 'a', 'of', 'for', 'on', 'with'] # Example list

def extract_keywords(text, num_keywords=5, lang='en'):
    """
    Extract top keywords from the text using TF-IDF in both Hindi and English.
    """
    stop_words = list(hindi_stopwords) if lang == 'hi' else list(english_stopwords)
    vectorizer = TfidfVectorizer(stop_words=stop_words, max_features=num_keywords)
    tfidf_matrix = vectorizer.fit_transform([text])
    keywords = vectorizer.get_feature_names_out()
    return ' '.join(keywords)

def get_representative_text(cluster_label, embeddings, texts, cluster_labels, cluster_centers_indices):
    """
    Find the representative text for a given cluster.
    """
    cluster_texts = texts[cluster_labels == cluster_label]
    cluster_embeddings = embeddings[cluster_labels == cluster_label]

    # Calculate cosine similarity between each text and cluster center
    similarities = cosine_similarity(cluster_embeddings, [embeddings[cluster_centers_indices[cluster_label]]])

    # Get index of text closest to cluster center
    representative_index = similarities.argmax()
    representative_text = cluster_texts.iloc[representative_index]

    return representative_text

def perform_clustering(input_csv, core_samples_csv, clustered_data_csv):
    """
    Perform clustering on the given input CSV file and save the results to specified output CSV files.

    Parameters:
    input_csv (str): Path to the input CSV file.
    core_samples_csv (str): Path to save the core samples CSV file.
    clustered_data_csv (str): Path to save the clustered data CSV file.
    """
    # Load the CSV file
    print('##### Loading Data . . .')
    df = pd.read_csv(input_csv)
    df = df[df['topic'] == 'political']

    # Get title and cleaned description
    df['text'] = df['title'] + ' ' + df['cleaned_description']

    # Generate text embeddings
    print('##### Loading Model . . . ')
    model = SentenceTransformer('all-MiniLM-L12-v2')
    df['text'] = df['text'].astype(str)
    embeddings = model.encode(df['text'].tolist())

    # Perform Affinity Propagation on the embeddings
    print('##### Performing Clustering . . . ')
    af = AffinityPropagation().fit(embeddings)

    # Get the cluster ids
    cluster_labels = af.labels_
    df['cluster'] = cluster_labels

    # Get cluster centers and store separately
    print('##### Getting Cluster Centers . . . ')
    cluster_centers_indices = af.cluster_centers_indices_
    core_samples = df.iloc[cluster_centers_indices][['title', 'cleaned_description', 'cluster']]

    # Get topics for each cluster
    print('##### Extracting Topics of Clusters . . .')
    cluster_topics = {}
    for cluster_label in df['cluster'].unique():
        representative_text = get_representative_text(cluster_label, embeddings, df['text'], cluster_labels, cluster_centers_indices)
        short_topic = extract_keywords(representative_text, lang='hi')  # Assuming Hindi, adjust if English
        cluster_topics[cluster_label] = short_topic

    # Add topics to core samples
    core_samples['topic'] = core_samples['cluster'].map(cluster_topics)

    df.drop('text', axis=1, inplace=True)

    # Save cluster centers with topics and original data with cluster ids to separate files
    df.to_csv(clustered_data_csv, index=False, encoding='utf-8-sig', quoting=1)
    print(f"------> Data with cluster ids saved to '{clustered_data_csv}'.")

    core_samples.to_csv(core_samples_csv, index=False, encoding='utf-8-sig')
    print(f"------> Core samples with topics saved to '{core_samples_csv}'.")

    return df

def get_top3(clustered_data):
    '''
    Get top 3 rows per cluster based on views and likes.
    70% weightage given to likes and 30% weightage to views.
    '''
    # Handle null values
    clustered_data.fillna('', inplace=True)
    
    clustered_data['views'] = pd.to_numeric(clustered_data['views'], errors='coerce')
    clustered_data['likes'] = pd.to_numeric(clustered_data['likes'], errors='coerce')

    # Create a new score based on the weighted combination of views and likes
    clustered_data['score'] = 0.7 * clustered_data['likes'] + 0.3 * clustered_data['views']

    # Sort data by the new score in descending order and group them on the basis of clusters
    print('##### Fetching top 3 rows per cluster. . .')
    clustered_data = clustered_data.sort_values(by='score', ascending=False)
    top3_df = clustered_data.groupby('cluster').head(3).reset_index(drop=True)

    # Sort data based on cluster ids and save to csv
    top3_df = top3_df.sort_values(by='cluster', ascending=True).reset_index(drop=True)

    return top3_df

# Function to extract video ID from YouTube URL
def extract_video_id(url):
    if 'v=' in url:
        return url.split('v=')[1]
    elif '/' in url:
        return url.split('/')[-1]
    return None

# Get video captions   
def get_captions(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'hi'])
        captions = ' '.join([t['text'] for t in transcript])
        print(f'-- Caption extracted for video id : {video_id} . . .')

        return captions
    except Exception:
        print('-- Captions not found. Storing empty caption !')
        return ''

def add_captions(top3_df, output_file):
    # Extract video IDs and fetch captions
    top3_df['video_id'] = top3_df['url'].apply(extract_video_id)

    print('##### Getting video captions . . .')
    top3_df['captions'] = top3_df['video_id'].apply(lambda vid: get_captions(vid))

    # Save the updated DataFrame to a new CSV file
    top3_df.to_csv(output_file, index=False, quoting=1, encoding='utf-8-sig')

    print(f"------> Updated CSV file with captions saved to: {output_file}")

    return top3_df


if __name__ == "__main__":
    filtered_data = 'data/filter/hi_ndtv_india_filter.csv'

    base_filename = os.path.splitext(os.path.basename(filtered_data))[0]
    channel_name = '_'.join(base_filename.split('_')[1:-1])

    # Define the base paths for the new files
    base_cluster_path = 'data/cluster'
    cluster_center_path = os.path.join(base_cluster_path, 'cluster_center', f'hi_{channel_name}_cluster_center.csv')
    cluster_data_path = os.path.join(base_cluster_path, 'cluster_data', f'hi_{channel_name}_cluster_data.csv')
    top_3_output_path = os.path.join(base_cluster_path, 'top3', f'hi_{channel_name}_top3.csv')

    clustered_data = perform_clustering(filtered_data, cluster_center_path, cluster_data_path)   #comment if the clusters are already formed
    # clustered_data = pd.read_csv(cluster_data_path)
    top_3_df = get_top3(clustered_data)
    top_3_df_captions = add_captions(top_3_df, top_3_output_path)

