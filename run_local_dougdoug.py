import subprocess
import datetime
import threading
import keyboard

stop_event = threading.Event()
whisper_thread = None

def main():
    run_speech_detection()
    parse_speech()
    send_to_ollama()
    respond_with_tts()
    return 0

def run_speech_detection():
    print("Press spacebar to start/stop speech detection.")
    output_lines = []

    def start_detection():
        global whisper_thread
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
            output_lines.append(line)  # Collect output lines

        if whisper_cmd.returncode == 0:
            print("Command executed successfully")
        else:
            print(f"Command failed with return code {whisper_cmd.returncode}")

        with open(f"detected_speech/{datetime.datetime.now()}_detected_speech.txt", "w") as f:  # Save the output to a text file
            f.writelines(output_lines)

    def toggle_detection():
        global whisper_thread
        if stop_event.is_set():
            print("Starting speech detection...")
            stop_event.clear()
            whisper_thread = threading.Thread(target=start_detection)
            whisper_thread.start()
        else:
            print("Stopping speech detection...")
            stop_event.set()
            if whisper_thread:
                whisper_thread.join()

    keyboard.add_hotkey('space', toggle_detection)
    keyboard.wait('esc')

def parse_speech():
    print("Parsing speech...")

def send_to_ollama():
    print("Sending to Ollama...")

def respond_with_tts():
    print("Responding with TTS...")

if __name__ == "__main__":
    main()

