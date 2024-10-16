# A Dockerized setup for prompting local LLMs via speech-to-text and getting responses via text-to-speech

# A video example

https://github.com/user-attachments/assets/82cce157-47b9-4c8b-85e6-485b8f974f33

## Which models we're using and what they do

This repo makes it possible for you to talk to AI characters using a series of local, open-source models.

This setup allows you to talk to the model via speech-to-text powered by [whisper.cpp](https://github.com/ggerganov/whisper.cpp).

After the text-to-speech is parsed, it's sent as a prompt to an LLM locally hosted by [Ollama](https://ollama.com/) (like phi3.5) using an API call.

The local LLM's response is streamed back and read aloud using [piper-tts](https://github.com/rhasspy/piper) while a simple character animation plays on screen. You can use a preset voice or clone a custom one.

You can then repeat these setps to continue the conversation, and the entire conversation history will be sent to the model each time.

## Inspiration

This repo was inspired by: 
- DougDoug's [Babagaboosh](https://github.com/DougDougGithub/Babagaboosh) repo
- [His video](https://youtu.be/W3id8E34cRQ?si=oRPEyZjjm58Z0lTv) where he created a system of proprietary AIs that completed the children's game Pajama Sam

This repo's AI system can all run locally on a 2019 Intel Chip Macbook Pro in near real-time for smaller Ollama models `phi3.5` and `qwen2.5:1.5b`.

## Using with Docker (Recommended)

### On MacOS

Because this uses text-to-speech we need to set up our local machine to interface with the Docker image.

We'll use `homebrew` as the primary installer. If you haven't already installed `homebrew` open the terminal and run
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)
```

Then, we'll install `pulseaudio` to handle audio parts with:

```
brew install pulseaudio
```

Then we'll get `pulseaudio` up and running in a way that will work with Docker

```
killall pulseaudio
pulseaudio --start --exit-idle-time=-1 --log-target=newfile:/tmp/pulse.log
```

Then run

```
pactl load-module module-native-protocol-tcp auth-anonymous=1
```

This command should return an integer (for example: 26)

Sometimes this command will fail if you try to run it right after the above commands. Wait for a bit and try again if it fails.

Then run

```
pulseaudio --check
```

and if you get no output you're good to go.

To run the Docker image fire up Docker Desktop and then use the following terminal command

```
docker run -it \
    -e PULSE_SERVER=host.docker.internal \
    -e MODELFILE_BASE_PATH="/app/fortune_teller" \
    -v ~/.config/pulse/cookie:/root/.config/pulse/cookie \
    --device /dev/snd \
    --privileged \
    mcmullarkey/local_dougdoug fortune_teller
```

It will take a while for the container to get started up since it has to start running the Ollama server from scratch and download the necessary base LLM models.

From there, you can follow the instructions on the command line to use the system.

That `docker run` command should automatically pull the `local_dougdoug` image from Docker Hub. If it doesn't for some reason you can do that manually by running

```
docker pull mcmullarkey/local_dougdoug
```

### Running a different model

To change which model you're using you'll need to change the `MODELFILE_BASE_PATH` as well as the `sysargv[1]` following `local_dougdoug` in the Docker command like this

```
docker run -it \
    -e PULSE_SERVER=host.docker.internal \
    -e MODELFILE_BASE_PATH="/app/spy_fox" \
    -v ~/.config/pulse/cookie:/root/.config/pulse/cookie \
    --device /dev/snd \
    --privileged \
    mcmullarkey/local_dougdoug spy_fox
```

### Note on Docker resources

You may need to increase the resources for your Docker image to run the models.

You will likely have enough resources allocated for the `fortune_teller/` model, but almost certainly not for the long context `pajama_sam/` or `spy_fox/` models. 

To up the Resources available to Docker containers go to Docker Desktop > Settings (The gear symbol) > Memory Limit to 32 GB (If you have that much available).

If you want to use smaller models or mess with the image, see the next section on building the Docker image yourself.

### Running with onscreen character animation (WORK IN PROGRESS)

The versions above won't display a character image because getting a window to display on your local computer via Docker is an entire can of worms.

If you'd like to add the character animation, follow these steps:

(WORK IN PROGRESS, NOT CURRENTLY WORKING)

Here's one [resource](https://medium.com/@mreichelt/how-to-show-x11-windows-within-docker-on-mac-50759f4b65cb)

### Building the Docker image yourself

Clone the repo

```
git clone https://github.com/mcmullarkey/local-dougdoug.git
```

navigate into the repo on your local machine

```
cd local-dougdoug
```

and finally navigate into the `cli/` directory

```
cd cli
```

First, make any changes you'd like to the files in the `cli/` directory/

For example, you could decrease the `PARAMETER num_ctx 16000` in the `spy_fox/Modelfile` to `PARAMETER num_ctx 4096` to make a smaller memory footprint.

(You don't have to make any changes, but if you're not going to you might as well pull the image from Dockerhub as advised in the section above)

If you're having any issues with changes you've made check out the Troubleshooting section later in this README.

Then build the docker image from the Dockerfile in the `cli/` directory.

```
docker build -t mcmullarkey/local_dougdoug .
```

After that you can follow the same process for running the Docker image as in the above section.

## Important note

This version of the system is something I primarily created to see: 
- If an AI could play through Spy Fox with friends
- If I could make a spooky fortune teller for a Halloween party
- If I could Dockerize a relatively complicated series of models

I decided to share because I thought folks might find it interesting to get into the guts of how to make a system like this work.

## Non-Docker installation and usage

Note: Not recommended unless for educational purposes! Breaking changes may occur that make this walkthrough obselete at any point. The process of installing this system isn't anywhere close to user-friendly! 

If you'd still like to follow this walkthrough at a point where the walkthrough will work, you can clone this repo and revert to commit c128187.

## Setup note

This setup has only been tested directly on an Intel-chip MacOS.

### Necessary installations

We'll use `homebrew` as the primary installer. If you haven't already installed `homebrew` open the terminal and run
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)
```

We'll then use `homebrew` to install the other necessary items using these commands in the terminal:

```
brew update
```
```
brew install pyenv ollama sox
```

`pyenv` allows us to use specific versions of Python as well as create virtual environments. We'll need both of those things for this project!

Before moving forward you'll need to "put `pyenv` on your PATH" so if you're not faimilar with that I recommend [this resource](https://realpython.com/intro-to-pyenv/).

### Cloning this repo

Go to the command line and navigate to where you'd like this repo to live on your local machine. 

If you're not comfortable navigating using the command line, this resource can help!

You'll also need to set up git if you haven't already. I like this resource.

Then, you can clone the repo

```
git clone https://github.com/mcmullarkey/local-dougdoug.git
```

navigate into the repo on your local machine

```
cd local-dougdoug
```

and finally navigate into the `cli/` directory

```
cd cli
```

### Setting up the Python environment with `pyenv`

The version depends on Python 3.11.9

Install that version of Python on the command line with 
```
pyenv install 3.11.9
```

After that install is complete, you need to install a virtual environment named local-dougdoug

On the command line, run 
```
pyenv virtualenv 3.11.9 local-dougdoug
``` 

to create the virtual environment

Finally, activate the local-dougdoug virtual environment by running 
```
pyenv activate local-dougdoug
``` 
on the command line.

### Installing Python dependencies

Once the local-dougdoug pyenv virtual environment is activated and you've navigated to the `cli/` directory, go to the command line and run 
```
pip install -r requirements.txt
```

This will install all the necessary Python dependencies to run the system.

### Installing the Whisper model for speech-to-text

From the `cli/` directory, navigate into the `models/` directory

```
cd models
```

and install the base.en Whisper model with the following command

```
./download-ggml-model.sh base.en
```

Then navigate back to the `cli/` directory

```
cd ..
```

### Creating the custom Ollama character models

Navigate into the `fortune_teller/` directory inside the `cli/` directory

```
cd fortune_teller
```

You can create the custom Ollama model by running

```
./create_model.sh
```

Note: If this is the first time you're trying to use the base model (in this case qwen2:1.5b) from Ollama this command will pull the model from Ollama and install it on your local machine.

When the command completes you should see output that says "Model 'fortune_teller' created successfully."

This command uses the `Modelfile` file to create a custom version of the qwen2:1.5b via a system message.

You can follow this same process for creating the pajama_sam and spy_fox subdirectories.

For now, navigate back to the `cli/` directory by running

```
cd ..
```

## Running the system

Once you're in the `cli/` directory, run

```
sudo ~/.pyenv/versions/local-dougdoug/bin/python run_local_dougdoug.py fortune_teller
```

If everything with the setup has gone well you should be able to start talking at the fortune_teller model! Running this will also automatically download the piper-tts voice model into the same directory where you run this process. This will work for either generic piper-tts voices or custom voice clones in [this HuggingFace repo](https://huggingface.co/mcmullarkey/local-dougdoug-voices).

You press "s" to start the conversation, "Esc" each time you're done speaking (I'd wait a small amount of time after you finish speaking before you hit "Esc"), and "c" to continue the conversation past one time you speak and the model responds. You can hit "q" to quit the conversation.

## Troubleshooting

### Speech-to-text

First, the program may not 100% capture your text accurately at baseline. The text parser may also include repeats of statements if two lines' fuzzy-matching similarity wasn't quite similar enough to trigger replacing the line. 

If you're getting repeated lines too often feel free to decrease the `similarity` argument in the `parse_speech()` function from 50 and try running the script again. 

If the speech-to-text isn't working at all I'd recommend checking the [whisper.cpp](https://github.com/ggerganov/whisper.cpp/issues) repo and seeing if any open or closed Github issues answer your questions

### Local LLM API call

Make sure you're running a small enough model to fit on your local resources. `qwen2:0.5b` as a base model should work on almost any modern-ish machine other than a Raspberry Pi (and maybe even then!)

Make sure your Ollama port is set as `11434` since the API calls go to `http://localhost:11434/api/chat`

If you're having other issues the [Ollama Discord](https://discord.com/invite/ollama) has a #help channel. You can see if your issue is solved already or you can ask your specific question.

### Text-to-speech

If everything else is running well but you're not having the responses read out loud, there's a chance the voice model didn't download properly.

Try running

```
sudo echo 'Welcome to the world of speech synthesis!' '|' piper '' --model en_US-lessac-medium '' --output_file welcome.wav && afplay welcome.wav
```

replacing en_US-lessac-medium with whatever voice you're trying to use if you're on a Mac. Make sure to only use, for example, `en_US-lessac-medium` instead of `en_US-lessac-medium.onnx` or `en_US-lessac-medium.onnx.json` 

Running this command will help confirm whether the voice file is downloaded and is working for text-to-speech.

Note if you're using Docker: You'll need to install piper-tts into a python virtual environment locally + activate the environment to run this test. Otherwise this failing just indicates you don't have piper-tts installed locally.

(Not relevant for Docker, won't help) Another potential fix is either installing or reinstalling `sox` via homebrew.

```
brew update
brew install sox
brew upgrade sox
```

If you're still stuck I recommend checking the [piper-tts](https://github.com/rhasspy/piper/issues) repo and seeing if any open or closed Github issues answer your questions

## Creating a custom voice model

You can do quite a bit with the models already provided by piper-tts. And if you want to create an entire local, open-source system like DougDoug did with Pajaam Sam you'll need to clone a voice.

Fair warning, this part is far more difficult than using a closed-source model.

The first thing we need to do is get ethically obtained recordings of the voice we'd like to clone.

For the Spy Fox voice clone, I recorded about 6 files of 5-12 seconds each of Spy Fox using [BackgroundMusic](https://github.com/kyleneideck/BackgroundMusic) while audio recording using QuickTime Player on my Mac.

I then used the `convert_m4a_to_wav.sh` script in the `cli/spy_fox/voice_cloning/` subdirectory to convert the .m4a files I'd generated via those recordings to  22050 Hz 16-bit, mono .wav files.

For ease of use later I'd highly recommend doing what I did and naming the files 1.wav, 2.wav, etc.

I then created the transcripts of those clips by hand to ensure 100% accuracy and created the file `cli/spy_fox/voice_cloning/transcripts.txt` The exact formatting of the file is important and example couple of lines looks like:

```
wavs/1.wav|Hm, so this is the sleepy little Greek island of Acedopholis. I seem to have arrived unfashionably early since nothing seems to be open.
wavs/2.wav|Someone once said the secret to life is making good decisions, which comes from good judgment, which comes from making bad decisions. I just thought I'd share that.
```

I've seen people recommend getting an hour of samples to train a high quality voice. I was able to get something serviceable for fun with ~1 minute of total voice time. However, using less audio shows in the ultimate voice clone (plenty of static and artificats). I also didn't isolate Spy Fox's voice from any background noises or music in the game. I also went with a medium-quality voice for speed purposes.

From here, I recommend using Google Colab to create the custom voice clone unless you have an awesome GPU locally. I certainly don't, so I used Colab.

There is a piper-tts training notebook for custom voices, but as of this writing if you use the notebook on the main branch the code will run but the voice won't be usable. 

Instead, use [this notebook](https://github.com/rmcpantoja/piper/blob/master/notebooks/piper_multilingual_training_notebook.ipynb) that's a PR currently waiting to be merged on the original piper-tts repo.

After following the instructions in the training notebook you should be able to use [this notebook](https://github.com/rmcpantoja/piper/blob/master/notebooks/piper_model_exporter.ipynb) from the same PR to export the .onnx and .onnx.json voice files.

The export notebook has a lot of bells and whistles, and just running this quick chunk in Colab (if your last.ckpt and config.json files are saved in the /content/ directory) got me my model files exported and ready to download

```
!python3 -m piper_train.export_onnx \
    /content/last.ckpt \
    /content/en_US-spy-fox-medium.onnx
    
!cp /content/config.json \
   /content/en_US-spy-fox-medium.onnx.json
```

Finally, make sure to put both the .onnx and .onnx.json files in the same directory as the script you're running + update the calls to the voices to the names of your custom files. You'll also have to modify the `get_model_details(), get_model_files(), get_voice_custom()`, and `check_and_download_voice()` functions to include a call to your custom character.


