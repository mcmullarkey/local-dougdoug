import subprocess
import datetime
import threading
import keyboard
import glob
import os
from gtts import gTTS
import json
import pygame

def main():
        
    os.makedirs('detected_speech', exist_ok=True)
    
    run_speech_detection()
    
    prompt_text = parse_speech("detected_speech/")
    
    print(f"The detected prompt text is: {prompt_text}")
    
    ollama_response = send_to_ollama(prompt_text)
    
    print(f"The response from Ollama is: {ollama_response["message"]["content"]}")
    
    respond_with_tts(ollama_response, "pajama_sam/images/Pajama_Sam.png")
    
    return 0

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


def parse_speech(directory_path):
    print("Parsing speech...")
    
    # Get most recently created .txt file
    
    files = glob.glob(os.path.join(directory_path, '*.txt'))
    file_path =  max(files, key=os.path.getctime) if files else None
    
    # Get last Transcription block from that file
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    capture = False
    for line in lines:
        cleaned_line = line.strip().replace('[2K', '').strip()
        if "[Start speaking]" in line:
            capture = True
        elif capture and cleaned_line:
            return cleaned_line


def send_to_ollama(prompt):
    print("Sending to Ollama...")
    try:
        response = subprocess.run(
            [
                "curl", "-X", "POST", "http://localhost:11434/api/chat",
                "-H", "Content-Type: application/json",
                "-d", f'''{{
                    "model": "pajama_sam",
                    "messages": [
                        {{
                            "role": "user",
                            "content": "{prompt}",
                            "options": {{
                                "num_predict": 42,
                                "num_ctx": 4096
                            }}
                        }}
                    ],
                    "stream": false
                }}'''
            ],
            capture_output=True, text=True
        )
        
        # Check if the subprocess call was successful
        if response.returncode == 0:
            # Attempt to parse the response as JSON
            result = json.loads(response.stdout)
            return result
        else:
            print("Error:", response.stderr)
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def play_audio():
    os.system("afplay response.mp3")  # Use afplay for macOS

def respond_with_tts(response_text, image_path):
    print("Responding with TTS...")
    os.system("killall afplay")
    
    tts = gTTS(response_text["message"]["content"])
    tts.save('response.mp3')
    
    pygame.init()
    screen = pygame.display.set_mode((800, 800), pygame.NOFRAME | pygame.SRCALPHA)  # NOFRAME for borderless window
    image = pygame.image.load(image_path)
    image = pygame.transform.scale(image, (600, 600))
    
    angle = 0
    direction = 1

    audio_thread = threading.Thread(target=play_audio)
    audio_thread.start()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((0, 0, 0, 0))  # Fully transparent fill
        
        rotated_image = pygame.transform.rotate(image, angle)
        rect = rotated_image.get_rect(center=(400, 400))
        
        screen.blit(rotated_image, rect.topleft)
        pygame.display.flip()
        
        angle += direction
        if angle > 7 or angle < -7:
            direction = -direction

        if not audio_thread.is_alive():
            running = False

        pygame.time.delay(30)

    audio_thread.join()
    pygame.quit()
    os.remove('response.mp3')


if __name__ == "__main__":
    main()

