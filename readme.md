# Discord Token Grabber Extension
## To login using the received token, see the folder 'Login Script'.

## Overview
This is a browser extension designed to automatically grab Discord tokens from the user's browser and send them to a specified server for processing. The extension runs in the background and fetches the token whenever it is detected on specific Discord API requests.

## Features
- Automatically grabs Discord tokens from the browser.
- Sends tokens to a specified server for processing.
- Minimal user interaction required.

## Installation
1. Clone this repository to your local machine.
2. Navigate to `chrome://extensions` in your Chrome browser.
3. Enable **Developer mode**.
4. Click on **Load unpacked** and select the directory where the extension files are located.

## Usage
- When the extension is installed, it automatically starts fetching Discord tokens.
- Tokens are sent to the specified server endpoint for processing.

## How it Works
- The extension listens for specific Discord API requests in the background.
- When a request containing a token is detected, it extracts the token and sends it to the server for processing.

## Server (server.py)
The `server.py` script sets up a Flask server to handle incoming token requests. It receives tokens, processes user data using the `discord_functions.py` module, and sends back a response containing user information.

## Discord Functions (discord_functions.py)
The `discord_functions.py` module contains functions to process user data retrieved from the Discord API. It fetches user information, friend count, payment details, and other relevant data, and saves it to both a JSON file and a MySQL database.

## Requirements
- Python 3.x
- Flask
- Requests
- MySQL Connector (for server.py)

## Configuration
- Modify the `db_config` dictionary in `discord_functions.py` to configure the MySQL database connection.
- Update the server endpoint URL in the extension code (`background.js`) to match the server hosting `server.py`.
