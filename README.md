
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

### Choose Your Own AI Model
This app uses the **Mistral Small 3.2 24B** model from Mistral AI for the AI
model by default. Openrouter lets you choose from a variety of other AI as well
including a number of other free models. To specify a model of your own choice:   

1. Go to the Openrouter [models](https://openrouter.ai/models) page.
2. Search for your preferred model, and make sure the model you have chosen
   have the "structured outputs" capabilities. In the models page, check under
   the "Supported Parameters" section and click on "structured_outputs". 
3. Once you have selected your preferred model, click on the "Copy model id"
   icon beside the model name. It is usually a small clipboard icon beside the
   model name. 
4. In the codevibe folder (where `codevibe` executable is), you will see a file
   named "config.toml" Open the file, and in the "model" field under the "ai"
   section, paste the value you just copied from the openrouter models page
   between the `""` quotation marks. 
5. Now when you run codevibe, it will run using your specified model.

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


