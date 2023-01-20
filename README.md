## Rohlik-Invoice-Manager

This program helps divide the cost of a grocery order among multiple people by automatically reading and analyzing emails from a specific grocery delivery service (Rohlik.cz). It extracts the items and prices from the emails, and uses stored information to identify the correct person to pay for each item. If necessary, the program prompts the user for clarification via the console.

## Requirements

The module requires Python 3.8, pip3 and pipenv installed on your machine.
It will also need your Gmail credentials (get them here: https://console.cloud.google.com/apis/credentials?project=galvanic-card-375314) and put `credentials.json` to the project folder

## Installation

Clone the repository and install dependencies.
```
pipenv shell --python 3.8
pipenv install --dev
```

Build the package
```
pip3 install --editable .
```

Start the script using the following command
```
python3 rohlik/invoice_creator.py
```

During the initial setup, the program will request access to read your emails. You can review the source code to ensure that your data is safe and will not be shared with any third party. To use the program, click "Accept." If you do not grant access, the program will not function.
