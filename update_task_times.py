# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 12:14:04 2024

@author: hor
"""

import requests
import json
import os
import argparse
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

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Update ClickUp tasks with new start and due dates.")
parser.add_argument('--current_date_from', type=str, default=None, help="Start date for filtering tasks (YYYY-MM-DD).")
parser.add_argument('--current_date_to', type=str, default=None, help="End date for filtering tasks (YYYY-MM-DD).")
parser.add_argument('--due_date_str', type=str, default=None, help="Due date for tasks (YYYY-MM-DD).")
parser.add_argument('--start_time_str', type=str, default=None, help="Start time for tasks (HH:MM).")
parser.add_argument('--verbose', type=bool, default=True, help="Enable verbose output (True/False).")
parser.add_argument('--verbose_level', type=int, default=2, help="Verbose level (1 for brief, 2 for detailed).")
args = parser.parse_args()

# Default values from command-line or dynamically assigned
current_date_from = args.current_date_from or (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
# current_date_from = '2024-11-14'  # Uncomment to set manually: specific start date, e.g., November 1, 2024

current_date_to = args.current_date_to or datetime.now().strftime('%Y-%m-%d')
# current_date_to = '2024-11-14'  # Uncomment to set manually: specific end date, e.g., November 14, 2024

due_date_str = args.due_date_str or datetime.now().strftime('%Y-%m-%d')
# due_date_str = '2024-10-22'  # Uncomment to set manually: specific due date, e.g., October 22, 2024

start_time_str = args.start_time_str or '12:00'  # Default start time
# start_time_str = '15:00'  # Uncomment to set manually: specific start time, e.g., 3 PM (15:00)

verbose = args.verbose
verbose_level = args.verbose_level

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
    
    if verbose:
        print(f"Found {len(tasks)} tasks to update.")

    for task in tasks:
        task_id = task['id']
        due_time = start_time + task_duration
        task_name = task.get('name', 'Unnamed Task')  # Default if task name is missing
        updated = update_task_dates(task_id, start_time, due_time)
        
        # Increment task counter and add break after every 2 tasks
        task_counter += 1
        if task_counter % 2 == 0:
            start_time = due_time + break_duration
        else:
            start_time = due_time
            
        if verbose and updated:
            if verbose_level == 1:
                print(f"Updated task ID: {task_id}")
            elif verbose_level == 2:
                print(f"Updated task: {task_name} - Start: {start_time} - Due: {due_time}")
            elif verbose_level == 3:
                print(f"Updated task ID: {task_id}, Name: {task_name} - Start: {start_time} - Due: {due_time}")

    if verbose:
        print(f"Updated {len(tasks)} tasks.")

# Execute the script
if __name__ == "__main__":
    assign_task_dates()
