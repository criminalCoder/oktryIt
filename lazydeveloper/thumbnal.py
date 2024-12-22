import os
import subprocess


def extract_thumbnail(video_path, thumbnail_path, fallback_time="00:00:05"):
    """
    Extracts the embedded thumbnail from a video, or generates one if not available.

    Args:
        video_path (str): Path to the video file.
        thumbnail_path (str): Path to save the thumbnail.
        fallback_time (str): Time to capture thumbnail if no embedded thumbnail exists.
    """
    try:
        # Try extracting embedded thumbnail
        print("Attempting to extract embedded thumbnail...")
        command = [
            "ffmpeg",
            "-i", video_path,  # Input video file
            "-map", "0:v:0",  # Map the first video stream
            "-frames:v", "1",  # Extract one frame
            thumbnail_path  # Output thumbnail file
        ]
        subprocess.run(command, check=True)
        if os.path.exists(thumbnail_path):
            print(f"Embedded thumbnail extracted: {thumbnail_path}")
            return thumbnail_path
    except subprocess.CalledProcessError:
        print("No embedded thumbnail found. Generating thumbnail...")

    try:
        # Generate thumbnail at a specific time
        command = [
            "ffmpeg",
            "-ss", fallback_time,  # Time position to capture the thumbnail
            "-i", video_path,  # Input video file
            "-vframes", "1",  # Capture one frame
            "-q:v", "2",  # Set quality (lower is better)
            thumbnail_path  # Output thumbnail file
        ]
        subprocess.run(command, check=True)
        if os.path.exists(thumbnail_path):
            print(f"Generated thumbnail: {thumbnail_path}")
            return thumbnail_path
    except subprocess.CalledProcessError as e:
        print(f"Error generating thumbnail: {e}")
        return None

    return None
