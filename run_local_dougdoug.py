import subprocess
import datetime
import threading
import keyboard
import re
import glob
import os
from ollama import Client
import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf
import simpleaudio as sa

stop_event = threading.Event()
whisper_thread = None

def main():
    
    client = Client(host='http://localhost:11434')
        
    os.makedirs('detected_speech', exist_ok=True)
    
    run_speech_detection()
    
    prompt_text = parse_speech("detected_speech/")
    
    print(f"The detected prompt text is: {prompt_text}")
    
    ollama_response = send_to_ollama(client, prompt_text)
    
    print(f"The response from Ollama is: {ollama_response}")
    
    respond_with_tts(ollama_response)
    
    return 0

def run_speech_detection():
    print("Press 's' to start and 'e' to stop speech detection.")
    output_lines = []
    stop_event = threading.Event()
    whisper_thread = None

    def start_detection():
        nonlocal whisper_thread
        whisper_cmd = subprocess.Popen(
            ["./stream", "-m", "./models/ggml-base.en.bin", "-t", "8", "--step", "0", "--length", "30000", "-vth", "0.6"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        for line in iter(whisper_cmd.stdout.readline, ''):
            if stop_event.is_set():
                whisper_cmd.terminate()
                whisper_cmd.wait()
                print("Speech detection stopped.")
                break
            print(line, end='')
            output_lines.append(line)

        if whisper_cmd.returncode == 0:
            print("Command executed successfully")
        else:
            print(f"Command failed with return code {whisper_cmd.returncode}")

        with open(f"detected_speech/{datetime.datetime.now()}_detected_speech.txt", "w") as f:
            f.writelines(output_lines)

    def start():
        nonlocal whisper_thread
        if not whisper_thread or not whisper_thread.is_alive():
            print("Starting speech detection...")
            stop_event.clear()
            whisper_thread = threading.Thread(target=start_detection)
            whisper_thread.start()

    def stop():
        print("Stopping speech detection...")
        stop_event.set()
        if whisper_thread:
            whisper_thread.join(timeout=1)

    keyboard.add_hotkey('s', start)
    keyboard.add_hotkey('e', stop)
    keyboard.wait('q')


def parse_speech(directory_path):
    print("Parsing speech...")
    
    # Get most recently created .txt file
    
    files = glob.glob(os.path.join(directory_path, '*.txt'))
    file_path =  max(files, key=os.path.getctime) if files else None
    
    # Get last Transcription block from that file
    
    with open(file_path, 'r') as file:
        content = file.read()
    matches = re.findall(r'### Transcription \d+ START(.*?)### Transcription \d+ END', content, re.DOTALL)
    if matches:
        last_transcription = matches[-1]
        text_lines = re.findall(r'\[.*?\](.*?)$', last_transcription, re.MULTILINE)
        return ' '.join(line.strip() for line in text_lines)


def send_to_ollama(client, prompt):
    print("Sending to Ollama...")
    response = client.chat(model='qwen2:1.5b', messages=[
    {
        'role': 'user',
        'content': prompt,
        'options': {
            'num_predict': 64,
            'num_ctx': 1024
        }
    },
    ])
    
    return response['message']['content']

def respond_with_tts(response_text):
    print("Responding with TTS...")
    #TODO Resolve numpy version issue
    #TODO Figure out if any way to do this faster locally
    
    # device = "cuda:0" if torch.cuda.is_available() else "cpu"

    # model = ParlerTTSForConditionalGeneration.from_pretrained("parler-tts/parler-tts-mini-v1").to(device)
    # tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler-tts-mini-v1")

    # prompt = response_text
    # description = "A female speaker delivers a slightly expressive and animated speech with a moderate speed and pitch. The recording is of very high quality, with the speaker's voice sounding clear and very close up."

    # input_ids = tokenizer(description, return_tensors="pt").input_ids.to(device)
    # prompt_input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)

    # generation = model.generate(input_ids=input_ids, prompt_input_ids=prompt_input_ids)
    # print("Finished generating")
    # audio_arr = generation.cpu().numpy().squeeze()
    # print("finished compressing")
    # sf.write("parler_tts_out.wav", audio_arr, model.config.sampling_rate)
    # print("Finished writing .wav file")    
    # wave_obj = sa.WaveObject.from_wave_file('parler_tts_out.wav')
    # play_obj = wave_obj.play()
    # play_obj.wait_done()

if __name__ == "__main__":
    main()

