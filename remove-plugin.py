import yaml
import sys

# Check if the file path is provided as a command-line argument
if len(sys.argv) < 2:
    print("Usage: python script.py <path_to_yaml_file>")
    sys.exit(1)

yaml_file_path = sys.argv[1]

print(f"Loading File at: {yaml_file_path}")

# Load the YAML file
with open(yaml_file_path, 'r') as file:
    yaml_content = yaml.safe_load(file)

print(f"File Loaded")

# Set 'plugins' section under 'spec' as an empty list
if 'spec' in yaml_content:

    if 'plugins' in yaml_content['spec'] and isinstance(yaml_content['spec']['plugins'], list):
        for plugin in yaml_content['spec']['plugins']:
            print(f"Removing plugin {plugin['alias']}") 

    yaml_content['spec']['plugins'] = []

# Save the modified YAML back to the file
with open(yaml_file_path, 'w') as file:
    yaml.dump(yaml_content, file)

print("spec.plugins section set as an empty list successfully.")