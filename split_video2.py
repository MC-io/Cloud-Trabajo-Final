import cv2
import json
import time
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from upload_to_bucket import upload_file_to_gcs
from google.cloud import pubsub_v1

project_id = "god-eyes-444201"
topic_id = "frames"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "god-eyes-444201-7a0a8e69bd01.json"

# Create a Publisher client
publisher = pubsub_v1.PublisherClient()

# Build the topic path
topic_path = publisher.topic_path(project_id, topic_id)
subscriber = pubsub_v1.SubscriberClient()

# Replace with your subscription name
subscription_path = subscriber.subscription_path(project_id, 'frames-sub')

# Pull messages and acknowledge them
def acknowledge_all_messages():
    # Pull messages from the subscription
    response = subscriber.pull(
        subscription=subscription_path,
        max_messages=10
    )
    if response.received_messages:
        ack_ids = [msg.ack_id for msg in response.received_messages]
        subscriber.acknowledge(subscription=subscription_path,ack_ids=ack_ids)
        print(f'Acknowledged {len(ack_ids)} messages.')
    else:
        print('No messages to acknowledge.')




def extract_frames(video_path, key, output_folder, interval=0.5):
    os.makedirs(output_folder, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Unable to open video file.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)  # Frames per second
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps  # Duration of the video in seconds
    
    print(f"Video duration: {duration:.2f}s, FPS: {fps:.2f}, Total Frames: {total_frames}")
    
    frame_interval = int(fps * interval)  # Number of frames between each capture    
    
    frame_idx = 0
    
    while True:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            print("End of video reached.")
            break
        # Save the frame
        output_file = os.path.join(output_folder, f"{key}-{frame_idx}.jpg")
        cv2.imwrite(output_file, frame)
        print(f"Saved: {output_file}")

        frame_idx += frame_interval
        
        if frame_idx >= total_frames:
            break
    
    cap.release()
    print("Frame extraction completed.")

    return key, frame_interval, total_frames



def post_frames(frames, key, frame_interval, total_frames, interval=0.5):
    start_time = time.time()  # Record the start time
    
    frame_idx = 0
    saved_frame_count = 0
    bucket_name = 'camera-frames'
    while frame_idx < total_frames:
        target_time = start_time + saved_frame_count * interval
        current_time = time.time()
        if current_time < target_time:
            time.sleep(target_time - current_time)


        output_file = os.path.join(frames, f"{key}-{frame_idx}.jpg")
        public_file_url = upload_file_to_gcs(bucket_name, output_file, f"frames/{key}-{frame_idx}.jpg")


        payload = {
            "name": key,
            "url": public_file_url,
            "timestamp": frame_idx,
        }
        url = "http://34.28.167.34/predict"
        response = requests.post(url, json=payload)

        response_data = response.json()
        json_string = json.dumps(response_data)


        data = json_string.encode("utf-8")
        future = publisher.publish(topic_path, data)
        print(f"Published message ID: {future.result()}")

        saved_frame_count += 1
        frame_idx += frame_interval
        
# Example usage

# video_file = "VIRAT-DATASET/VIRAT_S_000200_00_000100_000171.mp4"
# output_dir = "frames"
# extract_frames(video_file, output_dir, interval=3.0)
acknowledge_all_messages()


videos = {
    "video1": "VIRAT-DATASET/VIRAT_S_010003_03_000219_000259.mp4",
    "video2": "VIRAT-DATASET/VIRAT_S_010204_04_000646_000754.mp4",
    "video3": "VIRAT-DATASET/VIRAT_S_040000_08_001084_001190.mp4",
    "video4": "VIRAT-DATASET/VIRAT_S_040103_01_000132_000195.mp4",
    "video5": "VIRAT-DATASET/VIRAT_S_050000_08_001235_001295.mp4",
}

frames_interval_dict = dict()
total_frames_dict = dict()

with ThreadPoolExecutor(max_workers=8) as executor:
    futures = [executor.submit(extract_frames, filename, key, "frames", 5.0) for key, filename in videos.items()]
    for future in as_completed(futures):
        key, frames_interval, total_frames = future.result()
        frames_interval_dict[key] = frames_interval
        total_frames_dict[key] = total_frames

    futures = [executor.submit(post_frames, "frames", key, frames_interval_dict[key], total_frames_dict[key],  5.0) for key, filename in videos.items()]
    for future in as_completed(futures):
        future.result()