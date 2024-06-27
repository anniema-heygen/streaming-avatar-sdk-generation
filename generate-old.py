import requests
import sys
import os
import subprocess
import base64

StreamingAvatarApiUrl = "https://github.com/HeyGen-Official/StreamingAvatarSDK/blob/main/apis/StreamingAvatarApi.ts"
description = f"""
        This script will apply changes to the openapi-generated StreamingAvatarApi.ts based on code additions in the remote file (located at {StreamingAvatarApiUrl}). 
        It requires providing info from the remote StreamingAvatarApi.ts to determine what code to copy to the locally generated SDK.

        Usage: python generate.py <last_import_line> <first_line_added_to_class> <first_line_added_after_class>

        Parameters (Using 0 for any of the first two will skip applying the corresponding change):
            last_import_line: The line of the last import statement
            first_line_added: The first line of code added to the remote file
            is_code_added_to_class: True if first_line_added is added inside class StreamingAvatarApi, False if it is added after
            
        Example:
            python generate.py 55 311 True
            """

def modifyStreamingAvatarApi(last_import_line, first_line_added, is_code_added_to_class):
    try:
        #get contents of remote and local StreamingAvatarApi.ts
        response = requests.get("https://api.github.com/repos/HeyGen-Official/StreamingAvatarSDK/contents/apis/StreamingAvatarApi.ts")
        response.raise_for_status()
        json = response.json()
        remote_content = [f'{line}\n' for line in base64.b64decode(json['content']).decode('utf-8').splitlines()]
        local_file_path = './sdk/apis/StreamingAvatarApi.ts'
        with open(local_file_path, 'r') as local_file:
            local_content = local_file.readlines()

        if last_import_line != 0:
            last_import_line_local = next((i for i, line in reversed(list(enumerate(local_content))) if 'import ' in line or ' from ' in line), -1) + 1
            local_content = remote_content[:last_import_line + 1] + ["\n"] + local_content[last_import_line_local:]

        if first_line_added != 0:
            if is_code_added_to_class:
                local_content = local_content[:-2] + ["\n\n"] + remote_content[first_line_added - 1:]
            else:
                local_content += ["\n\n"] + remote_content[first_line_added - 1:]

        with open(local_file_path, 'w') as local_file:
            local_file.write(''.join(local_content))
           
        print(f"Successfully made changes to StreamingAvatarApi.ts")

    except requests.RequestException as e:
        print(f"Error fetching StreamingAvatarApi.ts: {e}")
    except IOError as e:
        print(f"Error writing to local StreamingAvatarApi.ts: {e}")

#Some changes to modifyStreamAvatarApi have dependencies in /events, so we need to download those files
def downloadEventsFolder():
    try:
        #get contents of remote /events folder
        response = requests.get("https://api.github.com/repos/HeyGen-Official/StreamingAvatarSDK/contents/events")
        response.raise_for_status()
        json = response.json()

        events_path = "./sdk/events"
        os.makedirs(events_path, exist_ok=True)
        for file_info in json:
            if file_info['type'] == 'file' and file_info['name'].endswith('.ts'):
                file_response = requests.get(file_info['download_url'])
                file_response.raise_for_status()
                file_content = file_response.text
                file_path = os.path.join(events_path, file_info['name'])
                with open(file_path, 'w') as file:
                    file.write(file_content)
                print(f"Successfully saved {file_info['name']} to /events")
            
    except requests.RequestException as e:
        print(f"Error fetching /events: {e}")
    except IOError as e:
        print(f"Error writing to local /events: {e}")

def modifyBaseAPIClassVariables():
    try:
        #get contents of remote and local runtime.ts
        response = requests.get("https://api.github.com/repos/HeyGen-Official/StreamingAvatarSDK/contents/runtime.ts")
        response.raise_for_status()
        json = response.json()
        remote_content = [f'{line}\n' for line in base64.b64decode(json['content']).decode('utf-8').splitlines()]
        local_file_path = './sdk/runtime.ts'
        with open(local_file_path, 'r') as local_file:
            local_content = local_file.readlines()

        #get line range BaseAPI class variables in remote and local runtime.ts
        start_of_class_remote = next((i for i, line in enumerate(remote_content) if 'class BaseAPI' in line), -1)
        end_of_constructor_remote = next((i for i, line in enumerate(remote_content[start_of_class_remote:]) if '}' in line), -1) + start_of_class_remote
        start_of_class_local = next((i for i, line in enumerate(local_content) if 'class BaseAPI' in line), -1)
        end_of_constructor_local = next((i for i, line in enumerate(local_content[start_of_class_local:]) if '}' in line), -1) + start_of_class_local

        local_content = local_content[:start_of_class_local] + remote_content[start_of_class_remote:end_of_constructor_remote + 1] + local_content[end_of_constructor_local + 1:]
        print(remote_content[start_of_class_remote:end_of_constructor_remote])

        with open(local_file_path, 'w') as local_file:
            local_file.write(''.join(local_content))
           
        print(f"Successfully made changes to BaseAPI class in runtime.ts")

    except requests.RequestException as e:
        print(f"Error fetching runtime.ts: {e}")
    except IOError as e:
        print(f"Error writing to local runtime.ts: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(description)
        sys.exit(1)

    last_import_line = int(sys.argv[1])
    first_line_added = int(sys.argv[2])
    is_code_added_to_class = bool(sys.argv[3])

    subprocess.run([
        "openapi-generator", "generate",
        "-i", "./sdk.yaml",
        "-g", "typescript-fetch",
        "-o", "./sdk"
        ], capture_output=True, text=True)

    #modifyStreamingAvatarApi(last_import_line, first_line_added, is_code_added_to_class)
    #downloadEventsFolder()
    #modifyBaseAPIClassVariables()

