
# Stop Vibe Coding, Start Code Vibing
We are doing "vibe coding" all wrong.   

Today, vibe coding means, telling our vibe to an AI, so it can write the code
for us. But we could be using AI in a far more efficient way - like curating
the perfect playlist to match our mood, while WE do the coding. Because
sometimes, all you can do is describe your "vibe", but you just don't know
which songs go with it. But AI, pulling from its vast training data, does.

Hence, this CLI AI Music app built by a developer, for developers (and honestly
anyone with a terminal). No need to painstakingly craft your perfect playlist
before your coding session (or jam to lo-fi beats that you just don't feel like
listening to right now). Just launch codevibe in a separate tmux window (or
any terminal or command prompt window), and keep coding on your other window.

## How to use it?

### Prequisites
You will need:   

- **VLC Media Player**. 
    - Make sure the VLC version matches your OS (64-bit VLC for 64-bit Windows,
      32-bit VLC for 32-bit Windows).   
- **Openrouter API key**. This program uses Openrouter for the AI. Thus, you
  will need an Openrouter API key.
    - Head over to [Openrouter](https://openrouter.ai/), and create an account
      (Google sign-in works too). 
    - Hover over the top right gear icon, and select "Keys". You can also click
      this [link](https://openrouter.ai/settings/keys) to directly go to the
      "Keys" page. 
    - Press the "Create API Key" button. Enter a name for the API Key, and
      press "Create". Now, you have the API key. Copy the API Key, and save it
      somewhere. **You won't see it again!**


### Run on Linux:
Download the `codevibe`, from the releases page of this repo, and extract the
folder. Open a new terminal session in the extracted folder, and run:   

```
./codevibe
```

From there follow the on-screen instruction. Note: you will need the Openrouter
API key you saved previously.
   
### Run on Windows:
Download the zip file from the releases page, and extract it. Once done, just
double-click on the `codevibe.exe` file, and the app will open in a new command
prompt window. From there just follow the on-screen instruction. Note, you will
need the Openrouter API key you saved previously.

### A Note About the AI Model
This app uses the **Mistral Small 3.2 24B** model from Mistral AI for the AI
model. While Openrouter allows the use of a variety of other models, this model
was chosen as it was a reliable free model. For now, there is no way to select
other AI models from within the app, as the model is hardcoded right now. I
will add support to select other models, including paid models as well, in the
future. Right now, if you want to change the model, you will need to:   

- modify the source code 
- compile the program yourself (or simply run it using Python).

The instructions for that is given below.


### How to Run/Build from Source Code
- Ensure you have Python version 3.11 or later, and VLC Media Player installed
- Use Git to clone the repository. Or download the code as a zip file.
- This step is optional, but I highly recommend creating a Python virtual
  environment
- While in the project root directory (the folder where pyproject.toml is
  contained), install all the dependencies by running `pip install -r
  requirements.txt`
- Install the codevibe package by running `pip install .`, while in the project
  root
- If you're on Windows, you would also need to additionally install the
  `windows-curses` package by running `pip install windows-curses`
- Once all the dependencies are installed, from the project root, run `python
  code_vibing\main.py` on Windows. For Linux, run `python3 code_vibing/main.py`.
- If you want to compile it to make your own binary, install `pyinstaller`
  (`pip install pyinstaller`) and while in the project root run `pyinstaller
  code_vibing/main.py`. This will create a "dist" folder which will contain a
  folder named "main." Inside the "main" folder will be the compiled binary.


