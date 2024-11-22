import requests
import os

# Define the server URL and the file path of the audio file
url = "http://localhost:5000/transcribe"
file_path = "E:/Narrion/test_audio.wav"  # Update this to your actual audio file's location

# Check if the file exists before sending
if not os.path.exists(file_path):
    print(f"Error: File not found at {file_path}")
else:
    try:
        # Open the audio file and send the POST request
        with open(file_path, "rb") as audio_file:
            print(f"Uploading {file_path} to {url}...")
            response = requests.post(url, files={"audio": audio_file})
        
        # Handle the server's response
        if response.status_code == 200:
            print("Transcription result:")
            print(response.json())
        else:
            print(f"Server returned an error: {response.status_code}")
            print("Response content:")
            print(response.text)
    except Exception as e:
        print(f"An error occurred: {e}")
