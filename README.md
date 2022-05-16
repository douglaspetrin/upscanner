# upScanner

upScanner is a very robust data extractor written in Python.
___

### Installing locally
You'll need poetry installed and then:
    
    make install

### Settings
Edit **params.json** in case you want to set other parameters such as **login, password, headless** and so on. 

### Running locally
** Make sure you set **login, password and secret_answer**  before running it.

If is the first time you are running the scanner:

    poetry run scanner/app.py

otherwise you can use the flag **last-state** to be using the cookies stored in scanner-state.json:

    poetry run scanner/app.py last-state


### Docker

    docker build -t upscanner .
    docker run -it upscanner

#### Testing

    make test

### Shortcuts for tools
Running individual tools is also possible, you can try:

for type checking your code:

    make mypy 
  
for security auditing your code:

    make bandit

for linting:

    make flake8

for finding dead code:

    make vulture
