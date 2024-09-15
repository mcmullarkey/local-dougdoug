# A local AI setup for talking to characters

## Which models we're using and what they do

This repo makes it possible for you to talk to AI characters using a series of local, open-source models.

This setup allows you to talk to the model via speech-to-text powered by [whisper.cpp](https://github.com/ggerganov/whisper.cpp){:target="_blank"}.

After the text-to-speech is parsed, it's sent as a prompt to an LLM locally hosted by [Ollama](https://ollama.com/) (like Phi3.5-mini) using an API call.

The local LLM's response is streamed back and read aloud using [piper-tts](https://github.com/rhasspy/piper) while a simple character animation plays on screen. You can use a preset voice or clone a custom one.

You can then repeat these setps to continue the conversation, and the entire conversation history will be sent to the model each time.

Here's a video example of the process:

https://github.com/user-attachments/assets/82cce157-47b9-4c8b-85e6-485b8f974f33

## Inspiration

This repo was inspired by: 
- DougDoug's [Babagaboosh](https://github.com/DougDougGithub/Babagaboosh) repo
- [His video](https://youtu.be/W3id8E34cRQ?si=oRPEyZjjm58Z0lTv) where he created a system of proprietary AIs that completed the children's game Pajama Sam

This repo's AI system can all run locally on a 5 year old, Intel Chip Macbook Pro in near real-time for smaller models like Phi-3.5-mini and Qwen-2-1.5b.

## Important note

The process of installing this system isn't anywhere close to user-friendly! 

This version of the system is something I primarily created to see: 
- If an AI could play through Spy Fox with friends
- If I could make a spooky fortune teller for a Halloween party

I decided to share because I thought folks might find it interesting to get into the guts of how to make a system like this work.

## Current setup

Note: This setup has only been tested directly on an Intel-chip MacOS.

### Necessary installations

We'll use `homebrew` as the primary installer. If you haven't already installed `homebrew` open the terminal and run
`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

We'll then use `homebrew` to install the other necessary items using this command in the terminal:

`brew install pyenv ollama sox`

`pyenv` allows us to use specific versions of Python as well as create virtual environments. We'll need both of those things for this project!

Before moving forward you'll need to "put `pyenv` on your PATH" so if you're not faimilar with that I recommend [this resource](https://realpython.com/intro-to-pyenv/).

### Clonging this repo

Go to the command line and navigate to where you'd like this repo to live on your local machine. 

If you're not comfortable navigating using the command line, this resource can help!

You'll also need to set up git if you haven't already. I like this resource.

Then, you can clone the repo

`git clone https://github.com/mcmullarkey/local-dougdoug.git`

navigate into the repo on your local machine

`cd local-dougdoug`

and finally navigate into the `cli` directory

`cd cli`

### Setting up the Python environment with `pyenv`

The current version depends on Python 3.11.9

Install that version of Python on the command line with `pyenv install 3.11.9`

After that install is complete, you need to install a virtual environment named local-dougdoug

On the command line, run `pyenv virtualenv 3.11.9 local-dougdoug` to create the virtual environment

Finally, activate the local-dougdoug virtual environment by running `pyenv activate local-dougdoug` on the command line.

### Installing Python dependencies

Once the local-dougdoug pyenv virtual environment is activated and you've navigated to the `cli` directory, go to the command line and run `pip install -r requirements.txt`

This will install all the necessary Python dependencies to run the system.

### Creating the custom Ollama character models

Navigate into the `fortune_teller` subdirectory inside the `cli` directory

`cd fortune_teller`

You can create the custom Ollama model by running

`./create_model.sh`

Note: If this is the first time you're trying to use the base model (in this case Qwen-2-1.5b) from Ollama this command will pull the model from Ollama and install it on your local machine.

When the command completes you should see output that says "Model 'fortune_teller' created successfully."

This command uses the `Modelfile` file to create a custom version of the Qwen-2-1.5b via a system message.

You can follow this same process for creating the pajama_sam and spy_fox subdirectories.

For now, navigate back to the `cli` directory by running

`cd ..`

### Testing the character voice

Back in the `cli` directory, run the following on the command line

```bash 
echo 'This sentence is spoken first. This sentence is synthesized while the first sentence is spoken.' | \
  ./piper --model en_GB-aru-medium.onnx --output-raw | \
  play -t raw -b 16 -e signed-integer -c 1 -r 22050 -
```

This should download the voice used by the fortune_teller model and alert you to any issues with the streaming TTS you need to address. If you didn't install `sox` via homebrew above this command won't work.

The files necessary for the a piper-tts text-to-speech voice are a .onnx file and a .onnx.json file. If you ran the above code in the "Testing the character voice" section the voice for fortune_teller should already be downloaded because it's a generic piper-tts model.

If you haven't, the system will throw an error and direct you to the piper-tts Github page for more info. This way you can debug any issues with TTS separately without having to run the entire system first.

If you are doing this process with the spy_fox model, you'll notice that the voice is instead downloaded from HuggingFace. That's because the SpyFox voice is a custom piper-tts model (a voice clone of Spy Fox from the game) that isn't available directly from piper-tts. See "Creating a custom voice model" below.

## Running the system

Once you're in the `cli` directory, run

`sudo ~/.pyenv/versions/local-dougdoug/bin/python run_local_dougdoug.py fortune_teller`

If everything with the setup has gone well you should be able to start talking at the fortune_teller model!

You press "s" to start the conversation, "Esc" each time you're done speaking (I'd wait a small amount of time after you finish speaking before you hit "Esc"), and "c" to continue the conversation past one time you speak and the model responds. You can hit "q" to quit the conversation.

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

There is a piper-tts training notebook, but as of this writing if you use it the code will run but the voice won't be usable. Instead using [this notebook](https://github.com/rmcpantoja/piper/blob/master/notebooks/piper_multilingual_training_notebook.ipynb) that's a PR currently waiting to be merged on the  original piper-tts repo.

After following the instructions in the training notebook you should be able to use [this notebook](https://github.com/rmcpantoja/piper/blob/master/notebooks/piper_model_exporter.ipynb) from the same PR to export the voice files.

The export notebook has a lot of bells and whistles, and just running this quick chunk in Colab got me my model files exported and ready to download

```
!python3 -m piper_train.export_onnx \
    /content/last.ckpt \
    /content/en_US-spy-fox-medium.onnx
    
!cp /content/config.json \
   /content/en_US-spy-fox-medium.onnx.json
```

Finally, make sure to put both the .onnx and .onnx.json files in the same directory as the script you're running + update the calls to the voices to the names of your custom files.


