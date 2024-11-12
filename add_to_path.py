import os
import sys
import platform
import subprocess

def add_to_path(directory):
    # Get the current PATH environment variable
    current_path = os.environ.get('PATH', '')
    
    # Check if the directory is already in PATH
    if directory in current_path:
        print(f"The directory {directory} is already in the PATH.")
        return

    # Determine the system platform and modify the PATH accordingly
    if platform.system() == 'Windows':
        # For Windows, modify the PATH in the registry
        try:
            # Get the current PATH from the system environment
            reg_key = r"HKCU\Environment"
            reg_value = "Path"
            current_path = subprocess.check_output(['reg', 'query', reg_key, '/v', reg_value], stderr=subprocess.STDOUT).decode()
            current_path = current_path.split("    ")[-1]  # Extract the path value
            
            # Add the directory to the PATH
            new_path = f"{current_path};{directory}"
            subprocess.run(['reg', 'add', reg_key, '/v', reg_value, '/t', 'REG_EXPAND_SZ', '/d', new_path, '/f'])
            print(f"Successfully added {directory} to PATH.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to add directory to PATH: {e}")
            sys.exit(1)

    elif platform.system() == 'Darwin' or platform.system() == 'Linux':
        # For Linux or macOS, we modify the .bashrc or .zshrc depending on the shell used
        shell_config_file = os.path.expanduser('~/.bashrc') if os.path.exists(os.path.expanduser('~/.bashrc')) else os.path.expanduser('~/.zshrc')
        
        try:
            with open(shell_config_file, 'a') as file:
                file.write(f'\n# Adding {directory} to PATH\n')
                file.write(f'export PATH="$PATH:{directory}"\n')
            print(f"Successfully added {directory} to PATH. Please restart your terminal or run 'source {shell_config_file}' to apply changes.")
        except Exception as e:
            print(f"Failed to modify {shell_config_file}: {e}")
            sys.exit(1)

    else:
        print(f"Unsupported OS: {platform.system()}")
        sys.exit(1)

if __name__ == "__main__":
    directory_to_add = input("Enter the directory to add to PATH: ").strip()
    
    if not os.path.isdir(directory_to_add):
        print("The provided directory does not exist.")
        sys.exit(1)

    add_to_path(directory_to_add)
