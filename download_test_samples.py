import os
import requests
from tqdm import tqdm

def download_file(url, folder, filename):
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    path = os.path.join(folder, filename)
    print(f"--- Downloading {filename} from {url} ---")
    
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(path, 'wb') as f, tqdm(
        desc=filename,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            f.write(data)
            bar.update(len(data))
    
    print(f"--- Successfully downloaded to {path} ---\n")

if __name__ == "__main__":
    folder = "pothole_test_videos"
    samples = [
        ("https://raw.githubusercontent.com/chaitanyaram1204/Pothole_detection/main/test2.mp4", "sample_pothole_01.mp4"),
        ("https://raw.githubusercontent.com/priya-dwivedi/Deep-Learning/master/pothole_detection/test_videos/test_video.mp4", "sample_pothole_02.mp4")
    ]
    
    print("\n--- Starting Pothole Sample Media Download ---")
    for url, name in samples:
        try:
            download_file(url, folder, name)
        except Exception as e:
            print(f"Failed to download {name}: {e}")
    
    print("--- Done! ---")
    print(f"Check the '{folder}' directory for your videos.")
