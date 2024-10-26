# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 18:59:44 2024

@author: hor
"""

import requests
import os
import json


# Define the folder where the config file is stored
config_folder = 'config'
config_file_path = os.path.join(config_folder, 'config.json')

# Load configuration from file
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

# Use the API key and task list ID from the config
API_KEY = config['API_KEY']

api_token = API_KEY

# ClickUp API endpoint to get the teams
url = 'https://api.clickup.com/api/v2/team'

# Set up headers for the request
headers = {
    'Authorization': api_token
}

# Make the request to get teams
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    teams = data.get('teams', [])
    for team in teams:
        print(f"Team Name: {team['name']}, Team ID: {team['id']}")
else:
    print(f"Failed to retrieve teams: {response.status_code}")

