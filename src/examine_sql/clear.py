import os

def clear_console():
    """Clears the console."""
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For macOS and Linux
        os.system('clear')

# Call the function to clear the console
clear_console()