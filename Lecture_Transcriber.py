import whisper #an OpenAI library for transcription
import os #for interacting with operating system (listing files, creating folders, joining paths etc)
import subprocess #for running external command-line programs, like ffmpeg

folder_path = "Da_FOLDER"

"""Processed"""
output_folder_name = "HSIL_Processed"
output_folder_path = os.path.join(folder_path, output_folder_name) #create the path for the folder containing processed file


"""
define  whisper model size to use
there are five options: 'tiny', 'base', 'small', 'medium', and 'large'.
Small is most recommended for it strikes a good balance of speed and accuracy.
"""

Whisper_model_size = "small"

"""
Checking if the output folder exists.
"""

print(f'Ensuring output folder exists: {output_folder_path}')
os.makedirs(output_folder_path, exist_ok=True)
print("output folder is ready.")
print("-"*30)



"""
load the whisper model once before processing files.
Don't load it in the loop, even though technically the code will still run!
This is because loading the model can take some time, it is much more efficient to do it outside the loop
"""

print(f'Loading Whisper model.... Model size = {Whisper_model_size}...')

try:
    model = whisper.load_model(Whisper_model_size)
    print("Whisper model loaded successfully.")
except Exception as e:
    print(f"Error loading whisper model: {e}")
    exit()

#Processing about to begin!!!

"""
Get a list of all files and folders inside the folder
"""
try:
    print(f"Listing contents of input folder: {folder_path}")
    all_items_in_folder = os.listdir(folder_path)
    print(f"Found {len(all_items_in_folder)} items.")

    #only MP$
    mp4_files = [item for item in all_items_in_folder if item.lower().endswith('.mp4') and os.path.isfile(os.path.join(folder_path, item))]

    if not mp4_files:
        print(f"No .mp4 files found in '{folder_path}'. Exit.")
        exit()
    print (f"Found{len(mp4_files)} MP4 files to process.")
    print("-"*30)


# Loop through each identified MP4 file
# 'filename' will hold the name of the current MP4 file in each turn of the loop
    # (e.g., "HSIL_01_Introduction.mp4").
    for filename in mp4_files:
        print(f"Processing file: {filename}")

        input_mp4_path = os.path.join(folder_path, filename)

        # !!!!!!!This is the code I want!!!!!!
        # os.path.splitext() splits a path into the part before the last dot
        # and the extension (e.g., "HSIL_01_Introduction.mp4" -> ("HSIL_01_Introduction", ".mp4")).
        base_name = os.path.splitext(filename)[0]  # We take the first part [0].

        # Create the full path for the intermediate WAV file in the output folder.
        intermediate_wav_path = os.path.join(output_folder_path, base_name + ".wav")

        # Create the full path for the final Transcript TXT file in the output folder.
        transcript_txt_path = os.path.join(output_folder_path, base_name + "_Transcript.txt")

        # --- Check if transcription is already done ---
        # Before doing any work, let's see if the final output file (the transcript)
        # already exists. If it does, we can skip this file, saving time and effort.
        if os.path.exists(transcript_txt_path):
            print(f"  Transcript already exists: {transcript_txt_path}")
            print("  Skipping transcription for this file.")
            print("-" * 20) # Short separator
            continue # 'continue' skips the rest of the current loop's code and goes to the next file.

        # --- Convert MP4 to WAV ---
        # We only need to convert to WAV if the transcript doesn't exist.
        # We also check if the intermediate WAV file already exists to avoid re-converting.
        if not os.path.exists(intermediate_wav_path):
            print(f"  WAV file not found. Converting MP4 to WAV: {intermediate_wav_path}")

            # This is the command-line command we would run in the terminal using ffmpeg.

            ffmpeg_command = [
                'ffmpeg',           # The command to run ffmpeg
                '-i', input_mp4_path, # -i: specifies the input file (our mp4)
                '-vn',              # tells ffmpeg to ignore video streams, only process audio
                '-acodec', 'pcm_s16le', # specifies the audio codec (PCM signed 16-bit little-endian), good for transcription
                '-ar', '16000',     # sets the audio sample rate to 16000 Hz, which is recommended for Whisper
                '-ac', '1',         # sets the number of audio channels to 1 (mono), also recommended
                '-f', 'wav',        # forces the output format to WAV
                '-y',               # automatically overwrite output file if it exists
                '-loglevel', 'error', # only show errors from ffmpeg, keeps the output clean
                intermediate_wav_path # Output WAV file path
            ]

            try:
                # Run the ffmpeg command using subprocess.
                # 'capture_output=True' captures the output and errors of the command.
                # 'text=True' decodes the output as text.
                # 'check=True' makes subprocess.run raise a CalledProcessError if the command returns a non-zero exit code (indicating an error).
                subprocess.run(ffmpeg_command, capture_output=True, text=True, check=True)
                print(f"  Successfully converted to WAV: {intermediate_wav_path}")

            except FileNotFoundError:
                print(f"  Error: ffmpeg not found. Please install ffmpeg and ensure it's in your system's PATH.")
                # We can't convert, so we can't transcribe. Skip to the next file.
                print("-" * 20) # Short separator
                continue
            except subprocess.CalledProcessError as e:
                 print(f"  Error converting {filename} to WAV:")
                 print(f"  Command: {' '.join(e.cmd)}") # Print the command that failed
                 print(f"  ffmpeg Output (stderr): {e.stderr}") # Print ffmpeg's error output
                 # Conversion failed, skip to the next file.
                 print("-" * 20) # Short separator
                 continue
            except Exception as e:
                 print(f"  An unexpected error occurred during WAV conversion for {filename}: {e}")
                 # An unexpected error occurred, skip to the next file.
                 print("-" * 20) # Short separator
                 continue

        else:
             print(f"  Intermediate WAV file already exists: {intermediate_wav_path}")


        # --- Transcribe WAV to Text ---
        # This step happens if the transcript didn't exist AND the WAV file is now available.
        print(f"  Starting transcription using Whisper model '{Whisper_model_size}'...")
        try:
            # Call the model's transcribe method.
            # It automatically handles loading the audio from the WAV file path.
            # We get back a dictionary containing the transcription result. <-- need to study this. it's the line 24 in my original vibe code
            transcription_result = model.transcribe(intermediate_wav_path)

            # The actual text is in the 'text' key of the result dictionary.
            transcript_text = transcription_result["text"]

            print(f"  Transcription complete for {filename}.")

            # --- Save Transcript to File ---
            print(f"  Saving transcript to: {transcript_txt_path}")
      
            with open(transcript_txt_path, "w", encoding="utf-8") as f:
                f.write(transcript_text)

            print(f"  Transcript saved successfully.")

            # --- Optional: Clean up the intermediate WAV file ---
            # print(f"  Cleaning up intermediate file: {intermediate_wav_path}")
            # os.remove(intermediate_wav_path)
            # print("  WAV file removed.")

        except Exception as e:
            # Catch any errors that happen during transcription or saving.
            print(f"  Error during transcription or saving for {filename}: {e}")
            print("  Transcription failed for this file.")

        print("-" * 30) # Print a long separator after processing each file

# --- Error Handling for Folder Listing ---
# This except block catches the FileNotFoundError if os.listdir() fails because
# the input folder doesn't exist.
except FileNotFoundError:
    print(f"Error: The input folder '{folder_path}' was not found.")
    print("Please check the 'input_folder' variable in the script and make sure it's correct.")
    print("Also, ensure the script is run from a location where it can access this folder.")
except Exception as e:
    # Catch any other unexpected errors that might occur during the listing phase.
    print(f"An unexpected error occurred while listing files: {e}")


# --- Final Message ---
print("\nProcessing complete.")
