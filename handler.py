import boto3
from moviepy.editor import VideoFileClip
import tempfile
import os

# Initialize S3 client
s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = 'virat-dataset'
    video_key = 'VIRAT-DATASET/VIRAT_S_000201_03_000640_000672.mp4'
    
    # Create temp directories for downloading video and saving frames
    with tempfile.TemporaryDirectory() as temp_dir:
        # Download the video from S3
        video_path = os.path.join(temp_dir, 'video.mp4')
        s3.download_file(bucket_name, video_key, video_path)
        
        # Load video with moviepy
        clip = VideoFileClip(video_path)
        
        # Extract frames every second and save to S3
        frame_count = 0
        for t in range(0, int(clip.duration)):
            frame_path = os.path.join(temp_dir, f'frame_{t}.jpg')
            frame = clip.get_frame(t)
            
            # Save frame locally as JPEG
            imageio.imwrite(frame_path, frame)
            
            # Upload frame to S3
            frame_key = f'frames/{os.path.basename(video_key)}/frame_{t}.jpg'
            s3.upload_file(frame_path, bucket_name, frame_key)
            frame_count += 1
        
        print(f"{frame_count} frames saved to S3 in 'frames/' folder.")

    return {
        'statusCode': 200,
        'body': f"Extracted and saved {frame_count} frames."
    }
