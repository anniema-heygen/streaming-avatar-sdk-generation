import difflib
import os
import requests
import base64
from config import StreamingAvatarApi_remote_path, StreamingAvatarApi_local_path, runtime_remote_path, runtime_local_path

def compare_files(file1_lines, file2_lines):
    differ = difflib.Differ()
    diffs = list(differ.compare(file1_lines, file2_lines))
    
    grouped_diffs = []
    current_group = []
    
    for diff in diffs:
        if diff[0] in ['-', '+', '?']:
            current_group.append(diff)
        else:
            if current_group:
                grouped_diffs.append(current_group)
                current_group = []
            grouped_diffs.append([diff])
    
    if current_group:
        grouped_diffs.append(current_group)
    
    return grouped_diffs, diffs, file1_lines, file2_lines

def display_files(file1_lines, file2_lines, start1, end1, start2, end2, diffs, local_file_path, context=3):
    term_width = os.get_terminal_size().columns
    file_width = (term_width - 7) // 2  # 7 for the middle separator and markers

    print(f"\nDiffs found:")
    print(f"{f'Lines {start1+1}-{end1+1} in {local_file_path}':<{file_width}} | {f'Lines {start2+1}-{end2+1} in the remote file':<{file_width}}")
    print("-" * term_width)
    
    # Determine the range of lines to display, including context
    display_start1 = max(0, start1 - context)
    display_end1 = min(len(file1_lines), end1 + context + 1)
    display_start2 = max(0, start2 - context)
    display_end2 = min(len(file2_lines), end2 + context + 1)

    i1, i2 = display_start1, display_start2
    while i1 < display_end1 or i2 < display_end2:
        line1 = file1_lines[i1].rstrip() if i1 < len(file1_lines) else ""
        line2 = file2_lines[i2].rstrip() if i2 < len(file2_lines) else ""
        
        if start1 <= i1 <= end1 or start2 <= i2 <= end2:
            # This line is part of the diff
            marker1 = "-" if start1 <= i1 <= end1 and any(d.startswith('-') for d in diffs) else " "
            marker2 = "+" if start2 <= i2 <= end2 and any(d.startswith('+') for d in diffs) else " "
            print(f"\033[1m{marker1} {line1:<{file_width-2}} | {marker2} {line2:<{file_width-2}}\033[0m")
        else:
            # This line is context
            print(f"  {line1:<{file_width-2}} |   {line2:<{file_width-2}}")
        
        i1 += 1
        i2 += 1

def apply_diff(grouped_diffs):
    result = []
    for diff in grouped_diffs:
        if diff.startswith('- '):
            continue  # Skip lines that are in the original but not in the new version
        elif diff.startswith('+ '):
            result.append(diff[2:])  # Add new lines
        elif diff.startswith('  '):
            result.append(diff[2:])  # Keep unchanged lines
    return result

def run_diffs(local_file_path, remote_file_path):
    response = requests.get(remote_file_path)
    response.raise_for_status()
    response_json = response.json()
    remote_content = [f'{line}\n' for line in base64.b64decode(response_json['content']).decode('utf-8').splitlines()]
    with open(local_file_path, 'r') as local_file:
        local_content = local_file.readlines()

    grouped_diffs, diffs, file1_lines, file2_lines = compare_files(local_content, remote_content)
    result_lines = []
    i1, i2 = 0, 0

    for diff in grouped_diffs:
        if any(diff[0] in ['-', '+'] for diff in diff):
            start1 = i1
            start2 = i2
            end1 = start1 + sum(1 for diff in diff if diff[0] in ['-', ' ']) - 1
            end2 = start2 + sum(1 for diff in diff if diff[0] in ['+', ' ']) - 1

            display_files(file1_lines, file2_lines, start1, end1, start2, end2, diffs, local_file_path)
            
            print(f"\n\nComparing: {local_file_path} and {remote_file_path}\nLegend: '-' indicates lines absent in the remote file, '+' indicates lines added in the remote file. Bold lines are part of the diff, non-bold lines are context")
            choice = input(f"Apply these changes to local {local_file_path}? (y/n): ").lower()
            if choice == 'y':
                result_lines.extend(apply_diff(diff))
            else:
                result_lines.extend(file1_lines[start1:end1+1])
            
            i1 = end1 + 1
            i2 = end2 + 1
        else:
            result_lines.append(diff[0][2:])  # Unchanged line
            i1 += 1
            i2 += 1

    with open(local_file_path, 'w') as file1:
        file1.writelines(result_lines)

    print(f"Selected changes applied to {local_file_path}.")

def run_diffs_on_sdk():
    run_diffs(StreamingAvatarApi_local_path, StreamingAvatarApi_remote_path)
    print("Finished merging remote changes into local StreamingAvatarApi.ts. Press any key to continue.")
    input().strip().lower()

    run_diffs(runtime_local_path, runtime_remote_path)

if __name__ == "__main__":
    run_diffs_on_sdk()