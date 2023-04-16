# SynthAssistant

SynthAssistant is an implementation of the Memory Stream concept from the LLM-base human simualacra experiment here: https://arxiv.org/abs/2304.03442

The goal is a python library with all of the functionality of a personal AI assistant with permanent, scalable, vector-based memory that can learn and grow with its user. 

### Requirements
Right now, SynthAssistant only support OpenAI LLMs and a remote Chroma vector database but I scaffolded it out to support other options in the future.

### Usage
1. Clone the repo
2. Set a new environment variable for the OpenAI api key with the name OPENAI_API_KEY
3. `pip install -r requirments.txt`
4. Import `SynthAssistant` into your python project

Example
```
import SynthAssistant

sa = SynthAssistant.synth_assistant("{your synth's name}", "{what you want your synth to call you}")
sa.start()
sa.interact("hello Synthia, what do you remember about me?", "George")

# snip embarrassing conversation
# oh no we need to wipe the memory

sa.wipe_memory()
```