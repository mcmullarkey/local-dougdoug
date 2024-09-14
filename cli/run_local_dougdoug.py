import subprocess
import datetime
import threading
import keyboard
import glob
import os
import json
import pygame
from multiprocessing import Process, Event
import re
import sys
from fuzzywuzzy import fuzz

conversation_history = []

def main():
    if not validate_arguments():
        return

    ollama_model, character_image, voice = get_model_details(sys.argv[1])

    os.makedirs('detected_speech', exist_ok=True)

    while True:
        if not wait_for_start_or_quit():
            return

        # Now wait for the user to press 's' before proceeding
        if wait_for_start_signal():
            run_speech_detection()
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
        print("Error: Invalid character. Choose 'spy_fox', 'fortune_teller', or 'pajama_sam'.")
        return False
    return True

def get_model_details(character):
    models = {
        "spy_fox": ("spy_fox", "spy_fox/images/spy_fox.png", "en_US-spy-fox-medium.onnx"),
        "fortune_teller": ("fortune_teller", "fortune_teller/images/fortune_teller.png", "en_GB-aru-medium.onnx"),
        "pajama_sam": ("pajama_sam", "pajama_sam/images/Pajama_Sam.png", "en_US-lessac-medium.onnx"),
    }
    return models.get(character)

def wait_for_start_or_quit():
    print("Press 'q' to exit or 's' to start the conversation.")
    while True:
        if keyboard.is_pressed('q'):
            print("Exiting the program.")
            return False
        if keyboard.is_pressed('s'):
            return True

def wait_for_start_signal():
    print("Press 's' to start speech detection.")
    while True:
        if keyboard.is_pressed('s'):
            print("Start speaking when prompted, press Esc when done speaking.")
            return True

def wait_for_continue_or_quit():
    print("Press 'c' to continue the conversation, or 'q' to quit.")
    while True:
        if keyboard.is_pressed('q'):
            print("Conversation ended.")
            return False
        if keyboard.is_pressed('c'):
            print("Continuing the conversation...")
            return True

def run_speech_detection():
    process = subprocess.Popen(["./stream", "-m", "./models/ggml-base.en.bin", "-t", "8", "--step", "0", "--length", "30000", "-vth", "0.6"], 
                               stdout=open(f"detected_speech/{datetime.datetime.now()}_detected_speech.txt", 'w'), 
                               stderr=subprocess.STDOUT, 
                               shell=True)
    print("Started speech detection")

    def listen_for_stop(proc):
        keyboard.wait('esc')
        proc.terminate()
        proc.wait()
        print("Speech detection terminated")

    listener_thread = threading.Thread(target=listen_for_stop, args=(process,))
    listener_thread.start()
    listener_thread.join() 

def parse_speech(directory_path, similarity_threshold):
    print("Parsing speech...")

    file_path = get_latest_file(directory_path)
    if not file_path:
        return ""

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
    cleaned_line = line.strip()
    cleaned_line = re.sub(r'\[\d+[A-Z]*', '', cleaned_line)
    return re.sub(r'[^\x20-\x7E]+', '', cleaned_line)

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
    os.system("killall afplay")

    response = escape_and_replace(response_text['message']['content'])
    tts_command = (
        f"echo '{response}' | "
        f"piper --model {voice_type} --output-raw | "
        "play -t raw -b 16 -e signed-integer -c 1 -r 22050 -"
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.expanduser("~/.pyenv/versions/local-dougdoug/lib/python3.11.9/site-packages")
    env["PATH"] = os.path.expanduser("~/.pyenv/versions/local-dougdoug/bin") + ":" + env["PATH"]

    tts_done_event = Event()

    tts_process = Process(target=run_tts, args=(tts_command, env, tts_done_event))
    tts_process.start()

    pygame_process = Process(target=character_animation, args=(image_path, tts_done_event))
    pygame_process.start()

    tts_process.join()
    pygame_process.join()

    print("TTS and animation processes should now be complete.")

def run_tts(tts_command, env, tts_done_event):
    subprocess.run(tts_command, shell=True, env=env)
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




