from flask import Flask, request, jsonify
import whisper
import traceback
import os
import imageio_ffmpeg as ffmpeg
import subprocess
from threading import Timer

# Initialize Flask app
app = Flask(__name__)

# Load the Whisper model
print("Loading Whisper model...")
model = whisper.load_model("base")

class TimeoutException(Exception):
    pass

def timeout_handler():
    raise TimeoutException("Whisper transcription timed out")

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        # Define file paths
        temp_dir = os.path.abspath("C:/Users/metro/AppData/Local/Temp")
        original_path = os.path.join(temp_dir, "uploaded_audio.wav")
        converted_path = os.path.join(temp_dir, "converted_audio.wav")

        # Ensure the temporary directory exists
        os.makedirs(temp_dir, exist_ok=True)

        # Save the uploaded file
        audio_file = request.files['audio']
        audio_file.save(original_path)
        print(f"File saved successfully at: {original_path}")

        # Preemptively remove the converted file if it exists
        if os.path.exists(converted_path):
            os.remove(converted_path)
            print(f"Removed existing file: {converted_path}")

        # Check if the file and FFmpeg exist
        ffmpeg_path = ffmpeg.get_ffmpeg_exe()
        if not os.path.exists(original_path):
            raise Exception(f"Original file not found: {original_path}")
        if not os.path.exists(ffmpeg_path):
            raise Exception(f"FFmpeg executable not found: {ffmpeg_path}")

        # Replace backslashes with forward slashes for FFmpeg
        original_path_fixed = original_path.replace("\\", "/")
        converted_path_fixed = converted_path.replace("\\", "/")

        # Construct the FFmpeg command
        command = [
            ffmpeg_path,
            "-y",  # Add this flag to force overwrite
            "-i", original_path_fixed,
            "-ar", "44100",
            "-ac", "1",
            converted_path_fixed
        ]

        # Run the FFmpeg command
        print(f"Running FFmpeg command: {' '.join(command)}")
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print("FFmpeg failed with the following error:")
            print(result.stderr)
            raise Exception("FFmpeg conversion failed")
        else:
            print(f"File converted successfully at: {converted_path_fixed}")

        # Use Whisper to transcribe the converted file with a timeout
        transcription = None
        timer = Timer(300, timeout_handler)  # Set a timeout of 300 seconds
        timer.start()
        try:
            print("Starting Whisper transcription...")
            transcription = model.transcribe(converted_path)
            print("Whisper transcription complete.")
        except TimeoutException as e:
            print(str(e))
            raise Exception("Whisper transcription timed out")
        finally:
            timer.cancel()  # Cancel the timer if transcription completes

        return jsonify({"transcription": transcription['text']})
    except Exception as e:
        print("Error during transcription:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)