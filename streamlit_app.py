import math
import streamlit as st
import random
import time
import requests



# Use your actual credentials here
API_KEY = "$2a$10$HjYpT8u2QEeuPI8L0Q/JUuONqkw7vXUuOhBRr3f8ytAhKdKnkyLdu"
BIN_ID = "6af77532ac6210605a85d78d"

# The meta endpoint for updating bin names
url = f"https://api.jsonbin.io/v3/b/{BIN_ID}/meta/name"

headers = {
    "X-Master-Key": API_KEY,
    "X-Bin-Name": "Daisy123",  # Change this to whatever name you want (1-128 characters)
}

response = requests.put(url, json={}, headers=headers)
print(response.status_code, response.json())
