# A local AI setup for talking to characters

## Which models we're using and what they do

This repo makes it possible for you to talk to AI characters using a series of local, open-source models.

This setup allows you to talk to the model via speech-to-text powered by [whisper.cpp](https://github.com/ggerganov/whisper.cpp).

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

Vavigate into the `fortune_teller` subdirectory inside the `cli` directory

`cd fortune_teller`

You can create the custom Ollama model by running

`./create_model.sh`

Note: If this is the first time you're trying to use the base model (in this case Qwen-2-1.5b) from Ollama this command will pull the model from Ollama and install it on your local machine.

When the command completes you should see output that says "Model 'fortune_teller' created successfully."

This command uses the `Modelfile` file to create a custom version of the Qwen-2-1.5b via a system message.

You can follow this same process for creating the pajama_sam and spy_fox subdirectories.

For now, navigate back to the `cli` directory by running

`cd ..`

### Running the system

Once you're in the `cli` directory, run

`sudo ~/.pyenv/versions/local-dougdoug/bin/python run_local_dougdoug.py fortune_teller`

If everything has gone well you should be able to start talking at the fortune_teller model!

You press "s" to start the conversation, "Esc" each time you're done speaking (I'd wait a small amount of time after you finish speaking before you hit "Esc"), and "c" to continue the conversation past one time you speak and the model responds. You can hit "q" to quit the conversation.

Note: The first time you try to use a piper-tts voice it will download the voice model necessary to do text-to-speech. This will include a .onnx file and a .onnx.json file.




