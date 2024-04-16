# hackathon



## Workflow

## How it works (for the hackathon)


## Future state


# Set up 

https://python.langchain.com/docs/integrations/chat/llama2_chat
https://python.langchain.com/docs/templates/llama2-functions
https://huggingface.co/blog/llama2#how-to-prompt-llama-2 
https://python.langchain.com/docs/integrations/llms/llamacpp#grammars

## 1. pyenv

Install here: [https://github.com/pyenv/pyenv#homebrew-on-macos]

Configure by adding the following to your `~/.zshrc` or equivalent (use line nano ~/.zshrc'):

```sh
# Pyenv environment variables
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"

# Pyenv initialization
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
```

Basic usage:

```sh
# Check Python versions
pyenv install --list
# Install the Python version defined in this repo
pyenv install $(cat .python-version)
# See installed Python versions
pyenv versions
```

```sh
# Change to the Python version you just installed
pyenv shell $(cat .python-version)
```

## 2. [pyenv-virtualenvwrapper](https://github.com/pyenv/pyenv-virtualenvwrapper)

```sh
# Install with homebrew (recommended if you installed pyenv with homebrew)
brew install pyenv-virtualenvwrapper
```

Configure by adding the following to your `~/.zshrc` or equivalent:

```sh
# pyenv-virtualenvwrapper
export PYENV_VIRTUALENVWRAPPER_PREFER_PYVENV="true"
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME/code  # <- change this to wherever you store your repos
export VIRTUALENVWRAPPER_PYTHON=$HOME/.pyenv/shims/python
pyenv virtualenvwrapper_lazy
```

Test everything is working by opening a new shell (e.g. new Terminal window):

```sh
# Change to the Python version you just installed
pyenv shell $(cat .python-version)
# This only needs to be run once after installing a new Python version through pyenv
# in order to initialise virtualenvwrapper for this Python version
python -m pip install --upgrade pip
python -m pip install virtualenvwrapper
pyenv virtualenvwrapper_lazy

# Create test virtualenv (if this doesn't work, try sourcing ~/.zshrc or opening new shell)
mkvirtualenv venv_test
which python
python -V

# Deactivate & remove test virtualenv
deactivate
rmvirtualenv venv_test
```

## 3. Get the repo & initialise the repo environment

⚠️ N.B. You should replace `REPO_GIT_URL` here with your actual URL to your GitHub repo.

```sh
git clone ${REPO_GIT_URL}
pyenv shell $(cat .python-version)

# Make a new virtual environment using the Python version & environment name specified in the repo
mkvirtualenv -p python$(cat .python-version) $(cat .venv)
python -V  # check this is the correct version of Python
python -m pip install --upgrade pip

# resume working on the virtual environment
workon $(cat .venv)
```

## 4. Install Python requirements into the virtual environment using [Poetry](https://python-poetry.org/docs/)

Install Poetry onto your system by following the instructions here: [https://python-poetry.org/docs/]

Note that Poetry "lives" outside of project/environment, and if you follow the recommended install
process it will be installed isolated from the rest of your system.

```sh
# Update Poetry regularly as you would any other system-level tool. Poetry is environment agnostic,
# it doesn't matter if you run this command inside/outside the virtualenv.
poetry self update

# This command should be run inside the virtualenv.
poetry install --sync

# Export new requirements.txt
poetry export -f requirements.txt --output requirements.txt --without-hashes
```


## 5. Install pre-commit hooks

Pre commit hooks run after commit to fix up formatting and other issues. Install them with:

```sh
pre-commit install
```

You can then run:

```sh
pre-commit run --all-files
```

and commit any changes made to files in the repo.

## 6. Add secrets into .env

- Run `cp .env.template .env` and update the secrets.

## 7. llama-cpp-python

Follow the instructions here: https://abetlen.github.io/llama-cpp-python/macos_install/

```sh
pip uninstall llama-cpp-python -y
CMAKE_ARGS="-DLLAMA_METAL=on" FORCE_CMAKE=1 pip install -U llama-cpp-python --no-cache-dir
pip install 'llama-cpp-python[server]'
```

Download a model file, see the following for advice:
  - [https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF#provided-files]
  - download llama-2-7b-chat.Q4_K_M.gguf


```sh
mv ./llama-2-7b-chat.Q4_K_M.gguf ./models/
```

Run the webserver:

```sh
# config your gguf model path
# make sure it is gguf and Q4
export MODEL=./models/llama-2-7b-chat.Q4_K_M.gguf
python3 -m llama_cpp.server --model $MODEL  --n_gpu_layers 1
# Note: If you omit the --n_gpu_layers 1 then CPU will be used
```

Try the Python API:

```python
from llama_cpp import Llama
llm = Llama(model_path="./models/llama-2-7b-chat.Q4_K_M.gguf")
output = llm("Q: Name the planets in the solar system? A: ", max_tokens=64, stop=["Q:", "\n"], echo=True)
print(output)
print(output['choices'][0]['text'])
```

## Jupyter kernel

```sh
python -m ipykernel install --user --name hackathon --display-name "Python (hackathon)"
```

## Streamlit

```sh
streamlit run app/home.py
```

## Docker local

```
# only require build initially
docker-compose build
docker-compose up -d
docker-compose down
```

check opensearch by visiting http://localhost:5601/app/login? or running `curl https://localhost:9200 -ku 'admin:admin'`

## Sagemaker setup
- Launch a SageMaker Notebook from SageMaker > Notebook > Notebook instances > Create notebook instance
- Select `ml.g4dn.xlarge` instance type (see [https://aws.amazon.com/sagemaker/pricing/] for pricing)

### Install Python dependencies

Create a new terminal and run the following:

```sh
# Switch to a bash shell
bash

# Change to the repo root
cd ~/SageMaker/hackathon

# Activate a Python 3.10 environment pre-configured with PyTorch
conda create -n hackathon python=3.10.13
conda create -n hackathon python=$(cat .python-version)
conda activate hackathon

# Check Python version
python --version

# Install the repo's declared dependencies
pip install poetry
poetry install

### Add Envs

```sh
cp .env.template env
mv env .env
```

## Jupyter
```sh
python -m ipykernel install --user --name hackathon --display-name "Python"
```

## Streamlit

```sh
streamlit run app/home.py
```
