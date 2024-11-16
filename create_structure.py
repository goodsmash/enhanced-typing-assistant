import os
import shutil

# Create main package directory
os.makedirs("typing_assistant", exist_ok=True)
os.makedirs("typing_assistant/ui", exist_ok=True)
os.makedirs("typing_assistant/core", exist_ok=True)
os.makedirs("typing_assistant/utils", exist_ok=True)
os.makedirs("typing_assistant/assets", exist_ok=True)
os.makedirs("typing_assistant/config", exist_ok=True)

# Create __init__.py files
init_files = [
    "typing_assistant/__init__.py",
    "typing_assistant/ui/__init__.py",
    "typing_assistant/core/__init__.py",
    "typing_assistant/utils/__init__.py",
    "typing_assistant/config/__init__.py",
]

for init_file in init_files:
    with open(init_file, "w") as f:
        f.write('"""Package initialization."""\n')
