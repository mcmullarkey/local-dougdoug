import subprocess
import datetime
import threading
import keyboard
import glob
import os
from gtts import gTTS
import json
import pygame
from multiprocessing import Process
import torch
from TTS.api import TTS
import simpleaudio as sa

def main():
    os.makedirs('detected_speech', exist_ok=True)
    
    while True:
        print("Press 's' to start speech detection or 'q' to exit the conversation.")
        
        while True:
            if keyboard.is_pressed('q'):
                print("Exiting the program.")
                return  # Exit the function to break the loop
            
            if keyboard.is_pressed('s'):
                print("Start speaking when prompted, press Esc when done speaking")
                break  # Break the inner loop to start detection
        
        run_speech_detection()
        
        prompt_text = parse_speech("detected_speech/")
        
        if prompt_text.lower() in ["exit", "quit", "stop"]:
            print("Conversation ended.")
            break
        
        print(f"The detected prompt text is: {prompt_text}")
        
        ollama_response = send_to_ollama(prompt_text)
        
        if ollama_response is None:
            print("Failed to get a response from Ollama. Exiting.")
            break
        
        print(f"The response from Ollama is: {ollama_response['message']['content']}")
        
        respond_with_tts(ollama_response, "pajama_sam/images/Pajama_Sam.png")
        
        # Check if user wants to continue or quit after the response
        print("Press 'c' to continue the conversation, or 'q' to quit.")
        while True:
            if keyboard.is_pressed('q'):
                print("Conversation ended.")
                return  # Exit the loop and the program
            if keyboard.is_pressed('c'):
                print("Continuing the conversation...")
                break  # Continue with the outer loop

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
    
    # TODO Append response from model to subsequent prompts to Ollama 
    # to enable actual conversation
    
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

def character_animation(image_path):
    pygame.init()
    screen = pygame.display.set_mode((800, 800), pygame.NOFRAME | pygame.SRCALPHA)
    image = pygame.image.load(image_path)
    image = pygame.transform.scale(image, (600, 600))
    
    angle = 0
    direction = 1

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

        pygame.time.delay(30)
    
    pygame.display.quit()
    pygame.quit()


def play_audio():
    # os.system("afplay response.mp3")  # Use afplay for macOS
    
    # Play the output.wav file
    wave_obj = sa.WaveObject.from_wave_file("output.wav")
    play_obj = wave_obj.play()
    play_obj.wait_done()  # Wait until sound has finished playing
    

def respond_with_tts(response_text, image_path):
    
    #TODO Enable more advanced TTS with Coqui https://docs.coqui.ai/en/latest/models/xtts.html
    
    print("Responding with TTS...")
    os.system("killall afplay")
    
    # Get device
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Init TTS
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    # Run TTS
    tts.tts_to_file(text=response_text["message"]["content"], speaker_wav="pajama_sam_test_reduced.wav", language="en", file_path="output.wav")
    
    # tts = gTTS(response_text["message"]["content"])
    # tts.save('response.mp3')
    
    # Start Pygame in a separate process
    pygame_process = Process(target=character_animation, args=(image_path,))
    pygame_process.start()

    # Start the audio playback in a separate thread
    audio_thread = threading.Thread(target=play_audio)
    audio_thread.start()

    # Wait for the audio to finish
    audio_thread.join()

    # Once audio is done, terminate the Pygame process
    pygame_process.terminate()
    pygame_process.join()
    
    # os.remove('response.mp3')
    os.remove('output.wav')

    print("Pygame window should now be closed.")


if __name__ == "__main__":
    main()

