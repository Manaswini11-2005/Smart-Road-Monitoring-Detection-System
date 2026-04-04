import urllib.request
import os

def download_expert_weights():
    # 1. Define the direct download link (Expert-trained Pothole Weights)
    url = "https://huggingface.co/keremberke/yolov8m-pothole-segmentation/resolve/main/best.pt"
    
    # 2. Define the destination path in your project
    dest_folder = "core/ai/weights"
    dest_path = os.path.join(dest_folder, "road_damage_yolov8.pt")
    
    # 3. Create folder if it doesn't exist
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
        print(f"Created directory: {dest_folder}")

    print("--- Pothole Detection Weights Downloader ---")
    print(f"Downloading expert weights from: {url}")
    print("Please wait, this may take a minute depending on your internet speed...")
    
    try:
        # 4. Download the file
        urllib.request.urlretrieve(url, dest_path)
        print("\nSUCCESS!")
        print(f"File saved to: {dest_path}")
        print("\nYour project is now updated with the highest accuracy model.")
        print("You can now run your Django server and see the results!")
    except Exception as e:
        print(f"\nERROR: Could not download the file. {e}")
        print("Please check your internet connection and try again.")

if __name__ == "__main__":
    download_expert_weights()
