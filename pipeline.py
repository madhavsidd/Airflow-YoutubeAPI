# youtube_comments_etl.py
# -*- coding: utf-8 -*-
import os
import pandas as pd
import googleapiclient.discovery

# Function to extract comments from YouTube API
def extract_comments(api_key, video_id):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api_key
    )

    comments_list = []
    request = youtube.commentThreads().list(
        part="snippet, replies",
        videoId=video_id
    )
    response = request.execute()

    comments_list.extend(process_comments(response['items']))

    # Loop through all pages of comments
    while response.get('nextPageToken', None):
        request = youtube.commentThreads().list(
            part="snippet, replies",
            videoId=video_id,
            pageToken=response['nextPageToken']
        )
        response = request.execute()
        comments_list.extend(process_comments(response['items']))

    print(f'Total comments extracted: {len(comments_list)}')
    return comments_list

# Function to process comments and extract required data
def process_comments(response_items):
    comments = []
    for comment in response_items:
        author = comment['snippet']['topLevelComment']['snippet']['authorDisplayName']
        comment_text = comment['snippet']['topLevelComment']['snippet']['textOriginal']
        publish_time = comment['snippet']['topLevelComment']['snippet']['publishedAt']

        comment_info = {
            'author': author,
            'comment': comment_text,
            'published_at': publish_time
        }
        comments.append(comment_info)

    print(f'Finished processing {len(comments)} comments.')
    return comments

# Function to load the data into a CSV file
def load_comments_to_csv(comments, output_file):
    df = pd.DataFrame(comments)
    df.to_csv(output_file, index=False)
    print(f'Data loaded into {output_file}')

# Main function to execute the ETL pipeline
def main():
    api_key = "YOUR_API_KEY"  # Replace with your YouTube API key
    video_id = "q8q3OFFfY6c"  # Replace with the YouTube video ID
    output_file = "youtube_comments.csv"  # Define the output CSV file

    # Step 1: Extract comments from the YouTube Data API
    comments = extract_comments(api_key, video_id)

    # Step 2: Load the processed comments into a CSV file
    load_comments_to_csv(comments, output_file)

if __name__ == "__main__":
    main()
