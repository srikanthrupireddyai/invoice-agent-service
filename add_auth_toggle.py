#!/usr/bin/env python3
"""
Script to add AUTH_ENABLED flag to the .env file
"""
import os

def update_env_file():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    # Check if .env exists
    if not os.path.exists(env_path):
        print(f"Error: .env file not found at {env_path}")
        return
    
    # Read current content
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Check if AUTH_ENABLED already exists
    auth_enabled_exists = any(line.startswith('AUTH_ENABLED=') for line in lines)
    
    # If not, add it
    if not auth_enabled_exists:
        print("Adding AUTH_ENABLED=false to .env file")
        with open(env_path, 'a') as f:
            f.write("\n# Authentication Settings\nAUTH_ENABLED=false  # Set to false to disable authentication in development\n")
        print("Done! Authentication is now disabled in development environment.")
    else:
        print("AUTH_ENABLED already exists in .env file")
        print("You can manually set it to 'false' to disable authentication in development.")

if __name__ == "__main__":
    update_env_file()
