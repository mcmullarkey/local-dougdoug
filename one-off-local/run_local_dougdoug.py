import subprocess
import datetime
import threading
import keyboard
import glob
import os
import json
import pygame
from multiprocessing import Process

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
        
        send_to_ollama(prompt_text, "pajama_sam/images/Pajama_Sam.png")
        
        # if ollama_response is None:
        #     print("Failed to get a response from Ollama. Exiting.")
        #     break
        
        # print(f"The response from Ollama is: {ollama_response['message']['content']}")
        
        # respond_with_tts(ollama_response, "pajama_sam/images/Pajama_Sam.png",
        #                  tts)
        
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


def send_to_ollama(prompt, image_path):
    print("Sending to Ollama...")

    try:
        response = subprocess.Popen(
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
                    "stream": true
                }}'''
            ],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        for line in response.stdout:
            try:
                if line.strip():
                    result = json.loads(line)
                    content = result.get('message', {}).get('content', '')
                    if content:
                        print(f"Message exists and is: {content}")
                        # Pass the content to the TTS and animation function
                        respond_with_tts({"message": {"content": content}}, image_path)
            except json.JSONDecodeError:
                print("Failed to decode JSON:", line)


        response.wait()
        if response.returncode != 0:
            print("Error:", response.stderr.read())
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
    
    # Play the output.wav file TODO Need to check and play different files vs. just output.wav
    wave_obj = sa.WaveObject.from_wave_file("output.wav")
    play_obj = wave_obj.play()
    play_obj.wait_done()  # Wait until sound has finished playing
    

def respond_with_tts(response_text, image_path):
    print("Responding with TTS...")
    os.system("killall afplay")

    # Activate the virtual environment
    tts_command = (
        # f"pyenv activate local-douddoug && "
        f"echo '{response_text['message']['content']}' | "
        "piper --model en_US-lessac-medium --output-raw | "
        "play -t raw -b 16 -e signed-integer -c 1 -r 22050 -"
    )
    
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.expanduser("~/.pyenv/versions/local-dougdoug/lib/python3.11.9/site-packages")
    env["PATH"] = os.path.expanduser("~/.pyenv/versions/local-dougdoug/bin") + ":" + env["PATH"]

    subprocess.run(tts_command, shell=True, env=env)

    # Start Pygame in a separate process
    pygame_process = Process(target=character_animation, args=(image_path,))
    pygame_process.start()

    # Wait for the audio playback to finish
    pygame_process.join()

    print("Pygame window should now be closed.")


if __name__ == "__main__":
    main()

