# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 12:14:04 2024

@author: hor
"""

import requests
import json
import os
from datetime import datetime, timedelta




# Define the folder where the config file is stored
config_folder = 'config'
config_file_path = os.path.join(config_folder, 'config.json')

# Load configuration from file
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

# Use the API key and task list ID from the config
API_KEY = config['API_KEY']
LIST_ID = config['LIST_ID']


# Default values
due_date_str = ''  # Manually set due date in 'YYYY-MM-DD' format if needed
current_date_from = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')  # Default to yesterday
current_date_to = datetime.now().strftime('%Y-%m-%d')  # Default to today

# Example: Manually set date range
# current_date_from = '2024-10-22'  # Set a specific start date, e.g., October 22, 2024
# current_date_to = '2024-10-23'  # Set a specific end date, e.g., October 23, 2024

# Example: Manually set due date
# due_date_str = '2024-10-22'  # Set a specific due date, e.g., October 22, 2024

# If due_date_str is not set or is empty, default to today's date
if not due_date_str:
    due_date_str = datetime.now().strftime('%Y-%m-%d')

start_time_str = '15:00'  # Manually set start time in 'HH:MM' format if needed
# Example: Manually set start time
# start_time_str = '15:00'  # Set a specific start time, e.g., 3 PM (15:00)

# If start_time_str is not set or is empty, default to '18:00'
if not start_time_str:
    start_time_str = '18:00'

task_duration_minutes = 30  # Default task duration (in minutes)
task_duration = timedelta(minutes=task_duration_minutes)
break_duration = timedelta(minutes=30)  # Break duration after every 2 tasks

# Fetch tasks with "TO DO" status from ClickUp
def get_todo_tasks():
    url = f'https://api.clickup.com/api/v2/list/{LIST_ID}/task'
    headers = {
        'Authorization': API_KEY
    }
    params = {
        'statuses[]': 'TO DO',
        'date_created_gt': int(datetime.strptime(current_date_from, '%Y-%m-%d').timestamp() * 1000),
        'date_created_lt': int(datetime.strptime(current_date_to, '%Y-%m-%d').timestamp() * 1000),
    }
    
    response = requests.get(url, headers=headers, params=params)
    return response.json().get('tasks', [])

# Update task start and due dates in ClickUp
def update_task_dates(task_id, start_date, due_date):
    url = f'https://api.clickup.com/api/v2/task/{task_id}'
    headers = {
        'Authorization': API_KEY,
        'Content-Type': 'application/json',
    }
    data = {
        'start_date': int(start_date.timestamp() * 1000),  # Convert to milliseconds
        'due_date': int(due_date.timestamp() * 1000),  # Convert to milliseconds
    }
    
    response = requests.put(url, headers=headers, json=data)
    return response.status_code == 200

# Main function to process and assign new start/due dates
def assign_task_dates():
    tasks = get_todo_tasks()
    start_time = datetime.strptime(f'{due_date_str} {start_time_str}', '%Y-%m-%d %H:%M')
    task_counter = 0

    for task in tasks:
        task_id = task['id']
        due_time = start_time + task_duration
        update_task_dates(task_id, start_time, due_time)
        
        # Increment task counter and add break after every 2 tasks
        task_counter += 1
        if task_counter % 2 == 0:
            start_time = due_time + break_duration
        else:
            start_time = due_time

    print(f"Updated {len(tasks)} tasks.")

# Execute the script
assign_task_dates()
