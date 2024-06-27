import requests
import os
import subprocess
from diffs import run_diffs_on_sdk
from config import events_remote_path, events_local_path, yaml_path, sdk_path
from publish import publish

def downloadEventsFolder():
    try:
        #get contents of remote /events folder
        response = requests.get(events_remote_path)
        response.raise_for_status()
        json = response.json()

        os.makedirs(events_local_path, exist_ok=True)
        for file_info in json:
            if file_info['type'] == 'file' and file_info['name'].endswith('.ts'):
                file_response = requests.get(file_info['download_url'])
                file_response.raise_for_status()
                file_content = file_response.text
                file_path = os.path.join(events_local_path, file_info['name'])
                with open(file_path, 'w') as file:
                    file.write(file_content)
                print(f"Saved {file_info['name']} to /events")
            
    except requests.RequestException as e:
        print(f"Error fetching /events: {e}")
    except IOError as e:
        print(f"Error writing to local /events: {e}")

if __name__ == "__main__":
    subprocess.run([
        "openapi-generator", "generate",
        "-i", yaml_path,
        "-g", "typescript-fetch",
        "-o", sdk_path
        ], capture_output=True, text=True)
    #Some functions in /events are necessary for StreamingAvatarApi.ts
    downloadEventsFolder()

    print(f"Streaming Avatar SDK generated at {sdk_path}.\nPress any key to compare the local StreamingAvatarApi.ts and runtime.ts files with their remote versions and apply diffs.")
    input().strip().lower()
    run_diffs_on_sdk()

    choice = input("Finished merging changes. Would you like to publish the SDK to npm now? You can also run python publish.py later. (y/n)").lower()
    if choice == 'y':
        publish()
    else:
        print("Exiting.")

    