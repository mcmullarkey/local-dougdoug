# A local AI setup for talking to characters

## General repo description and inspirtation

This repo makes it possible for you to talk to AI characters using a series of local, open-source models.

This repo was inspired by: 
- DougDoug's [Babagaboosh](https://github.com/DougDougGithub/Babagaboosh) repo
- [His video](https://youtu.be/W3id8E34cRQ?si=oRPEyZjjm58Z0lTv) where he created a system of proprietary AIs that completed the children's game Pajama Sam

This repo's AI system can all run locally on a 5 year old, Intel Chip Macbook Pro in near real-time for smaller models like Phi-3.5 mini and Qwen-2 0.5b.

## Which models we're using and what they do

This setup allows you to talk to the model via speech-to-text powered by whisper.cpp.

After the text-to-speech is parsed, it's sent as a prompt to an LLM locally hosted by Ollama.

The local LLM's response is streamed back and read aloud using piper-tts while a simple character animation plays on screen.

You can then repeat these setps to continue the conversation, and the entire conversation history will be sent to the model each time.

Here's a video example of the process.

https://github.com/user-attachments/assets/82cce157-47b9-4c8b-85e6-485b8f974f33

## Current setup

Note: This setup has only been tested directly on an Intel-chip MacOS.

### Necessary installations

We'll use `homebrew` as the primary installer. If you haven't already installed `homebrew` open the terminal and run
```/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"```

We'll then use `homebrew` to install the other necessary items using this command in the terminal:

```brew install pyenv ollama sox```

`pyenv` allows us to use specific versions of Python as well as create virtual environments. We'll need both of those things for this project!

Before moving forward you'll need to "put `pyenv` on your PATH" so if you're not faimilar with that I recommend [this resource](https://realpython.com/intro-to-pyenv/).

### Local setup



