# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 18:08:44 2024

@author: hor
"""

import requests
from datetime import datetime, timedelta
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
LIST_ID = config['LIST_ID']

# Uncomment this for a custom list_id
# list_id = '11111'


# Obsidian paths
obsidian_root_path = 'C:/Users/hor/Documents/Obsidian Vault/'  # Root path of your Obsidian vault
obsidian_relative_path = 'Tasks from Bar 2024-10-25.md'  # Path to the specific file inside the vault

# Full path to the Obsidian file
obsidian_file_path = os.path.join(obsidian_root_path, obsidian_relative_path)

# Default values
due_date_str = ''  # You can manually set this date in 'YYYY-MM-DD' format
# due_date_str = '2024-10-22'  # You can manually set this date in 'YYYY-MM-DD' format

# If due_date_str is not set or is empty, default to today's date
if not due_date_str:
    due_date_str = datetime.now().strftime('%Y-%m-%d')
    
start_time_str = '15:00'  # Default start time is 6 PM (18:00)

# Customizable variables
task_duration_minutes = 30  # Default task duration (in minutes), change this to your desired value
task_duration = timedelta(minutes=task_duration_minutes)  # Duration for each task

break_duration = timedelta(minutes=30)  # Default break duration of 30 minutes after every 2 tasks
end_time_limit = datetime.strptime(f'{due_date_str} 01:00', '%Y-%m-%d %H:%M')  # Limit until 1 AM next day

# Function to extract tasks from Obsidian markdown
def extract_tasks(file_path):
    tasks = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith('- [ ]'):
                task = line[6:].strip()
                tasks.append(task)
    return tasks

def upload_tasks_to_clickup(tasks, due_date, start_time_str):
    headers = {
        'Authorization': api_token,
        'Content-Type': 'application/json'
    }

    # Combine due date and start time
    start_time = datetime.strptime(f'{due_date_str} {start_time_str}', '%Y-%m-%d %H:%M')

    # Track the current time for scheduling tasks
    current_time = start_time

    task_counter = 0

    for task in tasks:
        # Calculate end time of the task
        end_time = current_time + task_duration

        # Check if end time exceeds 1 AM
        if end_time > end_time_limit:
            print(f"Warning: Task '{task}' may overlap as it exceeds the 1 AM limit.")

        # Prepare task data for ClickUp API
        task_data = {
            'name': task,
            'description': f'Task imported from Obsidian: {task}',
            'due_date': int(end_time.timestamp() * 1000),  # Due date is task's end time in milliseconds since epoch
            'start_date': int(current_time.timestamp() * 1000),  # Start time of the task
            'due_date_time': True,  # Include time for the due date
            'start_date_time': True,  # Include time for the start date
            'status': 'to do',  # Set task status (e.g., 'to do', 'in progress', etc.)
            'priority': 3,  # Priority 3 corresponds to "normal"
        }

        # Send a POST request to create the task in ClickUp
        response = requests.post(f'https://api.clickup.com/api/v2/list/{list_id}/task', headers=headers, json=task_data)

        if response.status_code == 200:
            print(f"Task '{task}' uploaded successfully to ClickUp from {current_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')}.")
        else:
            print(f"Failed to upload task '{task}' to ClickUp. Status code: {response.status_code}")
            print(f"Response: {response.json()}")

        # Update current_time for next task
        current_time = end_time

        # Add a break after every two tasks
        task_counter += 1
        if task_counter % 2 == 0:
            current_time += break_duration

# Extract tasks from the Obsidian file
tasks = extract_tasks(obsidian_file_path)

# Upload tasks to ClickUp with due date and start time
upload_tasks_to_clickup(tasks, due_date_str, start_time_str)
