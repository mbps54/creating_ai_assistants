# Set up the working environment
## Setup the working environment on Ubuntu 22.04
### 1. Install python3 and pip
```
DEBIAN_FRONTEND=noninteractive apt update
DEBIAN_FRONTEND=noninteractive apt install -y python3 python3-pip python3-venv
```

### 2. Add aliases (redirect python → python3, and pip → pip3)
```
echo "alias python='python3'" >> ~/.bashrc
echo "alias pip='pip3'" >> ~/.bashrc
source ~/.bashrc
```

### 3. Verify installation
```
python --version
pip --version
```

### 4. Create a virtual environment
```
python -m venv ~/llm
source ~/llm/bin/activate
```

### 5. Install dependencies (basic stack)
Download the `requirements.txt` file:
```
curl -o requirements.txt https://gist.githubusercontent.com/mbps54/f4b7ebd73b157aa1dfef86c4d7be4279/raw/a3ecde01acda80b149cf01d46450ed5856cca003/requirements.txt
```
Install the software:
```
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Export the API key
```
 export OPENAI_API_KEY=sk-proj-<...>
```
