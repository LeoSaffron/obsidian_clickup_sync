# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 18:08:44 2024

@author: hor
"""

import requests
from datetime import datetime, timedelta
import os
import json
import argparse

# Define the folder where the config file is stored
config_folder = 'config'
config_file_path = os.path.join(config_folder, 'config.json')

# Load configuration from file
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

# Use the API key and task list ID from the config
API_KEY = config['API_KEY']
LIST_ID = config['LIST_ID']

# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Upload tasks from Obsidian to ClickUp.")
    parser.add_argument('--obsidian_root_path', type=str, default='C:/Users/hor/Documents/Obsidian Vault/',
                        help="Root path of your Obsidian vault.")
    parser.add_argument('--obsidian_relative_path', type=str, required=True,
                        help="Path to the specific file inside the vault.")
    parser.add_argument('--due_date_str', type=str, default=None,
                        help="Due date for tasks (YYYY-MM-DD).")
    parser.add_argument('--start_time_str', type=str, default=None,
                        help="Start time for tasks (HH:MM).")
    parser.add_argument('--task_duration_minutes', type=int, default=30,
                        help="Duration of each task in minutes.")
    parser.add_argument('--break_duration_minutes', type=int, default=30,
                        help="Duration of break after every two tasks in minutes.")
    parser.add_argument('--end_time_limit', type=str, default="01:00",
                        help="Limit for task end time (HH:MM).")
    return parser.parse_args()

# Function to extract tasks from Obsidian markdown
def extract_tasks(file_path):
    tasks = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith('- [ ]'):
                task = line[6:].strip()
                tasks.append(task)
    return tasks

# Function to upload tasks to ClickUp
def upload_tasks_to_clickup(tasks, due_date, start_time_str, task_duration, break_duration, end_time_limit, api_token, list_id):
    headers = {
        'Authorization': api_token,
        'Content-Type': 'application/json'
    }

    # Combine due date and start time
    start_time = datetime.strptime(f'{due_date} {start_time_str}', '%Y-%m-%d %H:%M')

    # Track the current time for scheduling tasks
    current_time = start_time
    task_counter = 0

    for task in tasks:
        # Calculate end time of the task
        end_time = current_time + task_duration

        # Check if end time exceeds the limit
        if end_time > end_time_limit:
            print(f"Warning: Task '{task}' may overlap as it exceeds the end time limit.")

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

        # Update current_time for the next task
        current_time = end_time

        # Add a break after every two tasks
        task_counter += 1
        if task_counter % 2 == 0:
            current_time += break_duration

# Main function to run the script
def main():
    args = parse_arguments()

    # Obsidian paths
    obsidian_root_path = args.obsidian_root_path
    obsidian_relative_path = args.obsidian_relative_path

    # Full path to the Obsidian file
    obsidian_file_path = os.path.join(obsidian_root_path, obsidian_relative_path)

    # Default values
    due_date_str = args.due_date_str or datetime.now().strftime('%Y-%m-%d')
    # due_date_str = '2024-10-22'  # Uncomment to set manually: specific due date, e.g., October 22, 2024

    start_time_str = args.start_time_str or '15:00'
    # start_time_str = '18:00'  # Uncomment to set manually: specific start time, e.g., 6 PM (18:00)

    task_duration_minutes = args.task_duration_minutes
    # task_duration_minutes = 45  # Uncomment to set manually: specific task duration in minutes

    task_duration = timedelta(minutes=task_duration_minutes)
    break_duration = timedelta(minutes=args.break_duration_minutes)
    # break_duration = timedelta(minutes=20)  # Uncomment to set manually: specific break duration in minutes

    end_time_limit = datetime.strptime(f'{due_date_str} {args.end_time_limit}', '%Y-%m-%d %H:%M')
    # end_time_limit = datetime.strptime(f'{due_date_str} 02:00', '%Y-%m-%d %H:%M')  # Uncomment for a different end time

    api_token = API_KEY
    list_id = LIST_ID
    # list_id = '11111'  # Uncomment for a custom list ID

    # Extract tasks from the Obsidian file
    tasks = extract_tasks(obsidian_file_path)

    # Upload tasks to ClickUp with due date and start time
    upload_tasks_to_clickup(tasks, due_date_str, start_time_str, task_duration, break_duration, end_time_limit, api_token, list_id)

# Entry point
if __name__ == "__main__":
    main()
