# D-AI

> A small AI project built from scratch in Python.

D-AI is a personal AI project I'm building from the ground up.

The goal is not to make another chatbot that just calls an API. I want to understand how an AI actually works by building the different parts myself.

Right now, D-AI is still very early in development, but it already has things like a tokenizer, persistent memory, conversation handling, a basic statistical language model, a GUI, and a simple learning system.

And yes, it is still pretty dumb sometimes.

That's part of the fun.

---

## What is D-AI?

D-AI is an experimental AI written in Python.

The project started as a simple experiment with text prediction and gradually grew into something bigger.

The long-term goal is to turn it into a much more capable AI with its own neural network architecture, memory, learning system, and language generation.

I'm building it step by step instead of trying to make everything perfect from the beginning.

---

## Current features

D-AI currently has:

- 🧠 Persistent memory
- 💬 Conversation handling
- 🔤 Custom tokenizer
- 📊 Statistical language model
- 📚 Basic learning system
- 🖥️ Tkinter GUI
- 🤔 Thinker/debug system
- 💾 Conversation storage
- 📖 Vocabulary management
- 🛠️ Brain diagnostics
- 🔄 Brain reset and validation tools

The AI can also remember information about the user.

For example:

```text
You: my name is eewooouriyo

D-AI: Got it! I'll remember that your name is eewooouriyo.

You: what's my name

D-AI: Your name is eewooouriyo.
```

It isn't perfect, but it works.

How it works right now

D-AI is currently made of several components.

D-AI
│
├── main.py
├── gui.py
├── brain.py
├── memory.py
├── tokenizer.py
├── train.py
├── data.txt
└── model.json
main.py

The main entry point of D-AI.

It starts the GUI and can also start the Thinker system.

python main.py

Or:

python main.py --thinker
gui.py

The graphical interface.

It provides the chat window, menus, statistics, vocabulary tools, brain controls, and the Thinker interface.

The GUI is currently made with Tkinter.

brain.py

This is the main brain logic.

It handles things such as:

Understanding basic user input
Detecting intentions
Generating basic responses
Learning from conversations
Managing context
Working with memory
Running diagnostics

This is currently the biggest part of the project.

memory.py

Handles persistent memory.

D-AI stores memories and conversations inside:

memory.json

This allows information to survive after closing the program.

tokenizer.py

Converts text into tokens and tokens back into text.

It currently supports special tokens such as:

<PAD>
<UNK>
<BOS>
<EOS>
train.py

Currently trains a small trigram-based statistical language model.

The model is saved to:

model.json

This is not the final AI architecture.

It is just one of the first steps.

Current AI architecture

At the moment, D-AI is not a Transformer or LLM yet.

The current system is a combination of:

Rules
  +
Memory
  +
Conversation learning
  +
Tokenizer
  +
Trigram language model

The plan is to eventually replace the statistical language model with a neural network.

Roadmap

The project is still under development, so this roadmap will probably change.

Phase 1 — Basic AI
[x] Basic tokenizer
[x] Vocabulary system
[x] Statistical language model
[x] Basic responses
[x] Conversation handling
[x] Persistent memory
[x] GUI
[x] Thinker/debug system
Phase 2 — Neural network
[] Build the neural network from scratch
[] Implement embeddings
[] Implement attention
[] Implement positional encoding
[] Build a Transformer architecture
[] Implement training
[] Implement inference
[] Connect the neural model to D-AI
Phase 3 — Better learning
[] Learn from conversations
[] Improve long-term memory
[] Improve context handling
[] Improve vocabulary management
[] Better response generation
[] Better error handling
Phase 4 — Bigger D-AI
[] Better reasoning
[] Better language understanding
[] More reliable memory
[] Better conversation context
[] Model checkpoints
[] Training tools
[] More advanced GUI
[] Installation

D-AI currently requires Python.

Clone the repository:

git clone https://github.com/eewooouriyo/D-AI.git

Enter the project folder:

cd D-AI

Then run:

python main.py

That's it.

Running the Thinker

D-AI has a separate Thinker/debug interface.

Start it with:

python main.py --thinker

The Thinker is meant to show some of the internal processing performed by the current brain system.

It is mainly useful while developing and debugging D-AI.

Training

The current statistical model can be trained with:

python train.py

This generates:

model.json

The current training system uses data.txt.

This is temporary.

One of the goals of the project is to eventually move toward a system that can learn from conversations instead of relying entirely on a manually created training file.

Why build this?

Because I want to know how it works.

It's easy to make a chatbot by connecting an API to a few lines of code.

That's not what I'm trying to do here.

I want to build the system myself, make mistakes, break things, fix them, and slowly understand what I'm actually building.

D-AI is basically my attempt to learn AI by making one.

Project status

🚧 D-AI is currently experimental and under active development.

A lot of things are unfinished.

Some responses will be bad.

Some features may completely break.

Some parts of the architecture will probably be replaced later.

That's expected.

Dependencies

Currently D-AI mainly uses Python's standard library.

The project currently uses modules such as:

json
os
re
collections
tkinter
datetime

Additional dependencies may be added as the neural network implementation develops.

License

This project is currently experimental.

A proper license will be added later.

Final note

D-AI started as a small experiment.

It probably won't become a giant AI overnight.

But that's not really the point.

I'm building it one piece at a time.

And we'll see how far it gets.
