import subprocess
import sys
import os


venv_activation_script = 'myenv\\Scripts\\activate.bat'

def setup():
    if not os.getenv('VIRTUAL_ENV'):
        print('Please activate your virtual environment first.')
        sys.exit(1)
    try:
        subprocess.call([venv_activation_script, '&&', 'pip', 'install', '-r', 'requirements.txt'])
        print('Dependencies installed successfully.')
    except Exception as e:
        print(f'Failed to install dependencies: {e}')
        sys.exit(1)