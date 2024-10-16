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
import time
import random

# Initialize conversation history
conversation_history = []

def main():
    if not validate_arguments():
        return

    character = sys.argv[1]
    print(f"The detected character is: {character}")
    
    ollama_model, character_image, voice, activation, deactivation = get_model_details(character)
    
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

    while True:
        if not listen_for_activation(activation, deactivation):
            continue  # If deactivated, keep listening for activation
        
        give_opening_response(character_image, voice)
        
        time.sleep(1)
        
        prompt_text = get_speech_prompt(activation, deactivation)

        if not prompt_text:
            print("No prompt detected, waiting for activation again.")
            continue

        print(f"The detected prompt text is: {prompt_text}")
        conversation_history.append({"role": "user", "content": prompt_text})

        send_to_ollama(ollama_model, character_image, voice)

        # Optional: Automatically listen for further conversation or activation again


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
        "spy_fox": ("spy_fox", "spy_fox/images/spy_fox.png", "en_US-spy-fox-medium.onnx", "rise", "sleep"),
        "fortune_teller": ("fortune_teller", "fortune_teller/images/fortune_teller.png", "en_GB-aru-medium.onnx", "rise", "sleep"),
        "pajama_sam": ("pajama_sam", "pajama_sam/images/Pajama_Sam.png", "en_US-lessac-medium.onnx", "rise", "sleep"),
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


def listen_for_activation(activation, deactivation):
    print("Listening for activation phrase...")
    
    while True:
        process = subprocess.Popen(["./stream", "-m", "./models/ggml-base.en.bin", "-t", "8", "--step", "0", "--length", "30000", "-vth", "0.6"], 
                                   stdout=open(f"detected_speech/{datetime.datetime.now()}_detected_speech.txt", 'w'), 
                                   stderr=subprocess.STDOUT, 
                                   shell=True)

        def check_activation(proc, activation, deactivation):
            while True:
                detected_text = parse_speech("detected_speech/", similarity_threshold=50)
                if activation in detected_text:
                    print(f"Activation phrase '{activation}' detected.")
                    proc.terminate()  # Stop activation listening
                    proc.wait()
                    return True
                if deactivation in detected_text:
                    print(f"Deactivation phrase '{deactivation}' detected. Reverting to activation listening.")
                    proc.terminate()  # Stop the process
                    proc.wait()
                    return False

        listener_thread = threading.Thread(target=check_activation, args=(process, activation, deactivation))
        listener_thread.start()
        listener_thread.join()

        if listener_thread.is_alive():
            continue  # Keep listening until deactivation or activation

        return True  # Activation detected, ready for conversation

def give_opening_response(character_image, voice):
    
    if character_image == "fortune_teller/images/fortune_teller.png":
                        opening_responses = [
                            """It is I, Enigma, the devourer of souls. Ask your question, but be quick.
                            """,
                            """You have summoned Enigma, haunter of all the living. Give me your question
                            without delay.
                            """,
                            """Enigma peeks from beyond the veil. Ask your fortune if you dare.
                            """,
                            """I am Enigma, the teller of grim stories no one dares read. 
                            Ask me about your story, but don't wait too long.
                            """,
                            """I am Enigma, I've seen so many like you. 
                            Tell me what you want, but don't make me wait.
                            """,
                            """I am Enigma, ask what you will before I go back to the land of nightmares.
                            """,
                            """I am Enigma, the guide to the damned and the fools. Ask my guidance now.
                            """,
                            """You sit before Enigma, a power you cannot comprehend. 
                            Tell me what you want to know now.
                            """,
                             """In shadows, I linger—Enigma, the whisperer of secrets. Speak your truth, but do so wisely.
    """,
    """You stand at the crossroads with Enigma, the keeper of fate. What knowledge do you seek?
    """,
    """I am Enigma, a fleeting thought from the abyss. Dare to ask, but choose your words carefully.
    """,
    """Enigma rises from the depths of despair. Your question awaits, but time is of the essence.
    """,
    """I am Enigma, the scribe of unsung destinies. What tales shall we uncover together?
    """,
    """Enigma, the observer of the lost, beckons you. Speak your desire before I fade into the void.
    """,
    """You have awoken Enigma, the oracle of shadows. Reveal your inquiry, but tread lightly.
    """,
    """I am Enigma, the architect of nightmares and dreams. What shall we construct from your query?
    """,
    """In the echo of silence, I am Enigma, the phantom of questions unasked. What troubles your mind?
    """,
    """I am Enigma, the traveler of forgotten paths. Ask your question before I turn to dust.
    """,
    """From the edge of reality, I am Enigma, the keeper of twilight. Speak swiftly, for I am fleeting.
    """,
    """You call upon Enigma, the shaper of destinies. What wisdom do you crave, my seeker?
    """,
    """I am Enigma, the shadow that follows your thoughts. Speak now, for the hour grows late.
    """,
    """Enigma dances on the brink of existence. What truth do you wish to unveil?
    """,
    """I am Enigma, a voice from the shadows. Your question whispers in the dark—ask it now.
    """,
    """You stand in the presence of Enigma, the ghost of questions past. What echoes do you wish to hear?
    """,
    """I am Enigma, the keeper of fragmented dreams. What tale shall we weave together?
    """,
    """With a heart of mystery, I am Enigma. Your inquiry awaits, but make haste.
    """,
    """In the realm of the unknown, I am Enigma, your guide. Ask, if you dare to know.
    """,
    """I am Enigma, the bridge between your reality and the unseen. What do you seek, oh curious soul?
    """
                        ]
                        
    respond_with_tts({"message": {"content": random.choice(opening_responses)}}, character_image, voice)
    


def get_speech_prompt(activation, deactivation):
    print("Listening for speech prompt...")

    process = subprocess.Popen(["./stream", "-m", "./models/ggml-base.en.bin", "-t", "8", "--step", "0", "--length", "30000", "-vth", "0.6"], 
                               stdout=open(f"detected_speech/{datetime.datetime.now()}_detected_speech.txt", 'w'), 
                               stderr=subprocess.STDOUT, 
                               shell=True)

    def listen_for_prompt(proc):
        while True:
            prompt_text = parse_speech("detected_speech/", similarity_threshold=50)
            if any(phrase in prompt_text for phrase in ["[silence]", "[ silence ]", "[blank_audio]", 
                                                        "(muffled speaking)", "[music]", "[sighs]",
                                                        "[inaudible]", "[pause]", "[ pause ]"]):
                print("Likely end of speaking detected. Terminating speech detection.")
                proc.terminate()
                proc.wait()
                print("Speech detection terminated.")
                return  # Exit the loop
            if deactivation in prompt_text:
                print(f"Deactivation phrase '{deactivation}' detected. Reverting to activation listening.")
                proc.terminate()
                proc.wait()
                return  # Exit to listen for activation

            # Optional: Add a sleep or a small delay to prevent constant CPU usage
            time.sleep(0.5)

    listener_thread = threading.Thread(target=listen_for_prompt, args=(process,))
    listener_thread.start()
    listener_thread.join()

    prompt_text = parse_speech("detected_speech/", similarity_threshold=50)
    if not prompt_text.strip():
        print("No valid speech detected.")
        return ""
    
    return prompt_text


def parse_speech(directory_path, similarity_threshold):
    print("Parsing speech...")

    file_path = get_latest_file(directory_path)
    if not file_path:
        return ""

    with open(file_path, 'r') as f:
        lines = f.readlines()

    speech_lines = extract_speech_lines(lines, similarity_threshold)
    result = ' '.join(speech_lines).strip().lower()
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

    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.expanduser("~/.pyenv/versions/local-dougdoug/lib/python3.11.9/site-packages")
    env["PATH"] = os.path.expanduser("~/.pyenv/versions/local-dougdoug/bin") + ":" + env["PATH"]
    
    response = escape_and_replace(response_text['message']['content'])
    tts_command = (
        f"echo '{response}' | "
        f"piper --model {voice_type} --output-raw | "
        "play -t raw -b 16 -e signed-integer -c 1 -r 22050 -"
    )

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




