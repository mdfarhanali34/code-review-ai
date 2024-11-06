import openai
import re
from typing import List

# Set up OpenAI API key
openai.api_key = "your_openai_api_key"

# Define the FilePatchInfo structure
class FilePatchInfo:
    def __init__(self, base_file, head_file, patch, filename, edit_type, num_plus_lines, num_minus_lines):
        self.base_file = base_file
        self.head_file = head_file
        self.patch = patch
        self.filename = filename
        self.edit_type = edit_type
        self.num_plus_lines = num_plus_lines
        self.num_minus_lines = num_minus_lines

# Simulate your list of FilePatchInfo objects
file_patch_info_list = [
    FilePatchInfo(
        base_file='# test-web\n\nsadfsd dfg asdf sdf sdf fgh dfgdfg sfgfg dasf sdf dfg dsf fg dfg fgh dg\n\nmy name is kahn\n\nhola amigo xfg\n\nsdfg',
        head_file='# test-web\n\nsadfsd dfg asdf sdf sdf fgh dfgdfg sfgfg dasf sdf dfg dsf fg dfg fgh dg\n\nmy name is kahn\n\nhola amigo xfg\n\nsdfg',
        patch='@@ -1 +1,9 @@\n-# test-web\n\\ No newline at end of file\n+# test-web\n+\n+sadfsd dfg asdf sdf sdf fgh dfgdfg sfgfg dasf sdf dfg dsf fg dfg fgh dg\n+\n+my name is kahn\n+\n+hola amigo xfg\n+\n+sdfg\n\\ No newline at end of file',
        filename='README.md',
        edit_type="MODIFIED",
        num_plus_lines=9,
        num_minus_lines=1
    ),
    FilePatchInfo(
        base_file='def test():\n    return null',
        head_file='def test():\n    return null',
        patch='@@ -0,0 +1,2 @@\n+def test():\n+    return null\n\\ No newline at end of file',
        filename='test.py',
        edit_type="ADDED",
        num_plus_lines=2,
        num_minus_lines=0
    )
]

# Function to parse the patch and extract added lines
def parse_patch(patch: str) -> List[str]:
    added_lines = []
    patch_lines = patch.splitlines()
    for line in patch_lines:
        if line.startswith('+') and not line.startswith('++'):  # Ignore diff header lines (e.g., '+++')
            added_lines.append(line[1:].strip())  # Remove '+' and strip the line
    return added_lines

# Function to generate feedback using OpenAI
def generate_feedback(code_line: str) -> str:
    prompt = f"Provide feedback for the following code:\n{code_line}\n\nFeedback:"
    response = openai.Completion.create(
        engine="text-davinci-003",  # Use GPT-3 or another engine
        prompt=prompt,
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].text.strip()

# Function to process the file patches and generate feedback
def process_file_patches(file_patch_info_list: List[FilePatchInfo]):
    for file_patch in file_patch_info_list:
        print(f"Processing file: {file_patch.filename}")
        added_lines = parse_patch(file_patch.patch)  # Get added lines from the patch
        
        for line in added_lines:
            feedback = generate_feedback(line)  # Generate feedback for the added line
            print(f"Feedback for line '{line}': {feedback}\n")

# Process the file patches and generate feedback
process_file_patches(file_patch_info_list)
