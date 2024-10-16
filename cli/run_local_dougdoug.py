import subprocess
import datetime
import threading
# import keyboard
import glob
import os
import json
import pygame
from multiprocessing import Process, Event
import re
import sys
from fuzzywuzzy import fuzz
import platform
import time

conversation_history = []

def main():
    if not validate_arguments():
        return

    character = sys.argv[1]
    print(f"The detected character is: {character}")
    
    ollama_model, character_image, voice = get_model_details(character)
    
    voice_files = get_model_files(character)
    
    is_voice_custom = get_voice_custom(character)
    
    if is_voice_custom:
        check_and_download_voice(voice_files,
                            f"https://huggingface.co/mcmullarkey/local-dougdoug-voices/resolve/main/{character}/")
    else:
        language, dialect, voice_name = get_piper_path(voice)
        check_and_download_voice(voice_files,
                            f"https://huggingface.co/rhasspy/piper-voices/resolve/main/{language}/{dialect}/{voice_name}/medium/")

    os.makedirs('detected_speech', exist_ok=True)
    
    check_and_start_ollama()
    
    create_ollama_model(character)

    while True:
        if not wait_for_start_or_quit():
            return

        # Now wait for the user to press 's' before proceeding
        if wait_for_start_signal():
            run_speech_detection()
            print("Checking detected_speech/ directory...")
            print(os.listdir('detected_speech/'))
            prompt_text = parse_speech("detected_speech/", 50)

            print(f"The detected prompt text is: {prompt_text}")

            conversation_history.append({"role": "user", "content": prompt_text})

            send_to_ollama(ollama_model, character_image, voice)

            if not wait_for_continue_or_quit():
                return

def validate_arguments():
    if len(sys.argv) < 2:
        print("Error: Missing character argument.")
        return False
    if sys.argv[1] not in ["spy_fox", "fortune_teller", "pajama_sam"]:
        print(f"Error: Invalid character. You chose {sys.argv[1]} Choose 'spy_fox', 'fortune_teller', or 'pajama_sam'.")
        return False
    return True

def get_model_details(character):
    models = {
        "spy_fox": ("spy_fox", "spy_fox/images/spy_fox.png", "en_US-spy-fox-medium.onnx"),
        "fortune_teller": ("fortune_teller", "fortune_teller/images/fortune_teller.png", "en_GB-aru-medium.onnx"),
        "pajama_sam": ("pajama_sam", "pajama_sam/images/Pajama_Sam.png", "en_US-lessac-medium.onnx"),
    }
    return models.get(character)

def get_model_files(character):
    model_files = {
        "spy_fox": ("en_US-spy-fox-medium.onnx", "en_US-spy-fox-medium.onnx.json"),
        "fortune_teller": ("en_GB-aru-medium.onnx", "en_GB-aru-medium.onnx.json"),
        "pajama_sam": ("en_US-lessac-medium.onnx", "en_US-lessac-medium.onnx.json")
    }
    return model_files.get(character)

def get_voice_custom(character):
    custom_voice = {
        "spy_fox": True,
        "fortune_teller": False,
        "pajama_sam": False
    }
    return custom_voice.get(character)

def get_piper_path(voice):
    voice_language_supercategory = voice[:2]   
    voice_language_subcategory = voice[:5]
    name = voice[5:].split('-')[1]
    return voice_language_supercategory, voice_language_subcategory, name

def check_and_download_voice(files, hf_url):
    for file in files:
        if not os.path.exists(file):
            print(f"{file} not found, downloading...")
            download_url = f"{hf_url}{file}"
            print(f"The download url is {download_url}")
            try:
                subprocess.run(f"curl -L {download_url} -o {file}", shell=True, check=True)
            except:
                print("Model not available from HuggingFace repo, check for typos in command line call to a custom voice model or piper-tts Github for how to download generic models")
        else:
            print(f"{file} already exists.")

def check_and_start_ollama():
    try:
        # Check if Ollama server is running
        subprocess.run(["curl", "http://localhost:11434"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Ollama server is already running.")
    except subprocess.CalledProcessError:
        print("Ollama server not running. Starting the server...")
        # Start the Ollama server
        subprocess.Popen(["ollama", "serve"])

        # Wait for the server to be fully up
        while True:
            try:
                subprocess.run(["curl", "http://localhost:11434"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("Ollama server is now running.")
                break
            except subprocess.CalledProcessError:
                print("Waiting for Ollama server to start...")
                time.sleep(2)

def create_ollama_model(character):
    try:
        result = subprocess.run(['bash', f"{character}/create_model.sh"], check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        print(f"Standard Output: {e.stdout}")
        print(f"Standard Error: {e.stderr}")
        return None

def wait_for_start_or_quit():
    choice = input("Press 'q' and then 'Enter' to exit or 's' and then 'Enter' to start the conversation: ").strip().lower()
    if choice == 'q':
        print("Exiting the program.")
        return False
    elif choice == 's':
        return True
    return True

def wait_for_start_signal():
    input("Press 'Enter' to start speech detection. Start speaking when prompted, press Enter again when done speaking.")
    return True

def wait_for_continue_or_quit():
    choice = input("Press 'c' and then 'Enter' to continue the conversation, or 'q' and then 'Enter' to quit: ").strip().lower()
    if choice == 'q':
        print("Conversation ended.")
        return False
    elif choice == 'c':
        print("Continuing the conversation...")
        return True
    return True

def run_speech_detection():
    try:
        with open(f"detected_speech/{datetime.datetime.now()}_detected_speech.txt", 'w') as output_file:
            process = subprocess.Popen(["./stream", "-m", "./models/ggml-base.en.bin", "-t", "8", "--step", "0", "--length", "30000", "-vth", "0.6"], 
                                       stdout=output_file, 
                                       stderr=subprocess.STDOUT, 
                                       shell=False
                                       )
            print("Started speech detection")
    
            def listen_for_stop(proc):
                input("Press Enter to stop speech detection.")
                proc.terminate()
                proc.wait()
                print("Speech detection terminated")

            listener_thread = threading.Thread(target=listen_for_stop, args=(process,))
            listener_thread.start()
            listener_thread.join()
    except Exception as e:
        print(f"An error occurred: {e}") 

def parse_speech(directory_path, similarity_threshold):
    print("Parsing speech...")

    file_path = get_latest_file(directory_path)
    print(f"File detected: {file_path}")
    if not file_path:
        return "File path not detected"
    
    with open(file_path, 'r') as f:
            file_contents = f.read()
            print(f"Contents of {file_path}:\n{file_contents}")
    
    with open(file_path, 'r') as f:
        lines = f.readlines()

    speech_lines = extract_speech_lines(lines, similarity_threshold)
    result = ' '.join(speech_lines).strip()
    result = re.sub(r'\s+', ' ', result)

    return result

def get_latest_file(directory_path):
    files = glob.glob(os.path.join(directory_path, '*.txt'))
    return max(files, key=os.path.getctime) if files else None

def extract_speech_lines(lines, similarity_threshold):
    capture = False
    speech_lines = []
    last_cleaned_line = ""

    for line in lines:
        cleaned_line = clean_speech_line(line)

        if "[Start speaking]" in line:
            capture = True
        elif capture:
            if "whisper_print_timings" in cleaned_line:
                break

            if cleaned_line:
                if last_cleaned_line:
                    similarity = fuzz.ratio(last_cleaned_line, cleaned_line)
                    print(f"Comparing:\nLast: {last_cleaned_line}\nCurrent: {cleaned_line}\nSimilarity: {similarity}")

                    if similarity >= similarity_threshold:
                        print(f"Similar (>= {similarity_threshold}): Replacing last entry.")
                        speech_lines[-1] = cleaned_line
                    else:
                        print(f"Not Similar (< {similarity_threshold}): Appending new entry.")
                        speech_lines.append(cleaned_line)
                else:
                    speech_lines.append(cleaned_line)

                last_cleaned_line = cleaned_line
    return speech_lines

def clean_speech_line(line):
    # Remove transcription markers like "### Transcription 0 START" or "### Transcription 0 END"
    if line.startswith("### Transcription"):
        return ""
    
    # Remove timestamp blocks like "[00:00:00.000 --> 00:00:05.000]"
    cleaned_line = re.sub(r'\[\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}\]', '', line)
    
    # Remove any remaining non-printable characters
    cleaned_line = re.sub(r'[^\x20-\x7E]+', '', cleaned_line)
    
    # Return stripped line if it's not empty
    return cleaned_line.strip()

def send_to_ollama(ollama_model, image_path, voice):
    print("Sending to Ollama...")

    try:
        response = subprocess.Popen(
            [
                "curl", "-X", "POST", "http://localhost:11434/api/chat",
                "-H", "Content-Type: application/json",
                "-d", json.dumps({
                    "model": ollama_model,
                    "messages": conversation_history,
                    "stream": True,
                    "options": {"keep_alive": "15m"}
                })
            ],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        handle_response_stream(response, image_path, voice)

        response.wait()
        if response.returncode != 0:
            print("Error:", response.stderr.read())

    except Exception as e:
        print(f"An error occurred: {e}")

def handle_response_stream(response, image_path, voice):
    buffer = ""
    full_response = ""
    sentence_queue = []

    for line in response.stdout:
        try:
            if line.strip():
                result = json.loads(line)
                content = result.get('message', {}).get('content', '')
                if content:
                    buffer += content
                    full_response += content

                    while re.search(r'[.!?;]', buffer):
                        end_idx = re.search(r'[.!?;]+', buffer).end()
                        sentence = buffer[:end_idx]
                        buffer = buffer[end_idx:].lstrip()
                        if re.search(r'\w', sentence):
                            sentence_queue.append(sentence)

        except json.JSONDecodeError:
            print("Failed to decode JSON:", line)
        except Exception as e:
            print(f"An error occurred while processing the line: {e}")

    for sentence in sentence_queue:
        print(f"Reading sentence: {sentence}")
        respond_with_tts({"message": {"content": sentence}}, image_path, voice)

    if full_response:
        conversation_history.append({"role": "assistant", "content": full_response})

    print(f"The full conversation history is: {conversation_history}")

def respond_with_tts(response_text, image_path, voice_type):
    print("Responding with TTS...")
    
    response = escape_and_replace(response_text['message']['content'])
    
    tts_command = (
    f"echo '{response}' | "
    f"piper --model {voice_type} --output-raw | "
    "pacat --format=s16le --channels=1 --rate=22050"
    )

    tts_done_event = Event()

    tts_process = Process(target=run_tts, args=(tts_command, tts_done_event))
    tts_process.start()

    pygame_process = Process(target=character_animation, args=(image_path, tts_done_event))
    pygame_process.start()
    
    tts_process.join()
    pygame_process.join()

    print("TTS and animation processes should now be complete.")

def run_tts(tts_command, tts_done_event):
    subprocess.run(tts_command, shell=True)
    tts_done_event.set()

def character_animation(image_path, tts_done_event):
    pygame.init()
    screen = pygame.display.set_mode((800, 800), pygame.NOFRAME | pygame.SRCALPHA)
    image = pygame.image.load(image_path)
    image = pygame.transform.scale(image, (600, 600))

    angle = 0
    direction = 1
    rotation_speed = 0.5  # Slow down the rotation

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0, 0))
        rotated_image = pygame.transform.rotate(image, angle)
        rect = rotated_image.get_rect(center=screen.get_rect().center)
        screen.blit(rotated_image, rect)
        pygame.display.flip()

        angle += direction * rotation_speed
        if abs(angle) >= 7:
            direction = -direction

        pygame.time.delay(30)  # Increase delay to make the motion slower

        if tts_done_event.is_set():
            running = False

    pygame.quit()


def escape_and_replace(text):
    return text.replace("'", "'\\''")

if __name__ == '__main__':
    main()




