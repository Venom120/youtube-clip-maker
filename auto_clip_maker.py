import os
import yt_dlp
import subprocess
from whisper_timestamped import load_model, transcribe_timestamped

VIDEO_URL = "https://www.youtube.com/watch?v=P3m94TRQu60"
VIDEO_FILE = "input.mp4"
CLIP_FOLDER = "clips"

# 1. Download YouTube video
def download_video(url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': VIDEO_FILE,
        'merge_output_format': 'mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# 2. Transcribe with whisper-timestamped
def transcribe_video(video_file):
    model = load_model("medium")  # or "base", "small", "large" etc.
    segments = transcribe_timestamped(model, video_file)
    return segments["segments"]  # segments are inside the "segments" key

# 3. Cut clips from segments
def cut_clips(video_file, segments):
    os.makedirs(CLIP_FOLDER, exist_ok=True)
    for i, segment in enumerate(segments):
        start = segment['start']
        end = segment['end']
        output_path = os.path.join(CLIP_FOLDER, f"clip_{i+1:03d}.mp4")

        # ffmpeg command to cut without re-encoding (fast)
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_file,
            "-ss", str(start),
            "-to", str(end),
            "-c", "copy",
            output_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    print("Downloading video...")
    download_video(VIDEO_URL)

    print("Transcribing with whisper-timestamped...")
    segments = transcribe_video(VIDEO_FILE)

    print(f"Cutting {len(segments)} clips...")
    cut_clips(VIDEO_FILE, segments)

    print(f"Done! Clips saved in folder '{CLIP_FOLDER}'")

if __name__ == "__main__":
    main()
