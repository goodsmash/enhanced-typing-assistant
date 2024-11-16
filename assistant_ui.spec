# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs
from PyInstaller.building import Analysis, EXE, PYZ
import os
import sys
import time
import glob
import subprocess
from shutil import which

# Define constants
RUNTIME_HOOK = "hook-runtime.py"
RUNTIME_HOOK_CONTENT = """import os
import sys
if hasattr(sys, "_MEIPASS"):
    base_path = sys._MEIPASS
    os.environ["QT_PLUGIN_PATH"] = os.path.join(base_path, "plugins")
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(base_path, "platforms")
    os.environ["QT_QPA_PLATFORM_THEME"] = "windows"
    os.environ["QT_QPA_FONTDIR"] = os.path.join(base_path, "fonts")
    os.environ["QT_TRANSLATIONS_DIR"] = os.path.join(base_path, "translations")
"""

# Create runtime hook with error handling
try:
    with open(RUNTIME_HOOK, 'w', encoding='utf-8') as f:
        f.write(RUNTIME_HOOK_CONTENT)
except Exception as e:
    print(f"Error creating runtime hook: {e}")
    sys.exit(1)

# Ensure PyQt5 is imported before use
try:
    import PyQt5
except ImportError as e:
    print(f"Error: {e}")
    sys.exit(1)

# Get PyQt5 path
def find_pyqt_path():
    return os.path.join(os.path.dirname(PyQt5.__file__), 'Qt5')

pyqt_path = find_pyqt_path()

# Initialize ruby_path and rubocop_path
ruby_path = None
rubocop_path = None

# Add Ruby and RuboCop paths
def find_rubocop_installation():
    """Enhanced RuboCop installation finder"""
    def get_gem_paths():
        try:
            result = subprocess.run(['gem', 'env', 'gempath'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split(os.pathsep)
        except Exception as e:
            print(f"Warning: Could not get gem paths: {e}")
        return []

    possible_paths = [
        os.path.expandvars(r'%USERPROFILE%\.gem\ruby\*\bin'),
        os.path.expandvars(r'%LOCALAPPDATA%\gem\ruby\*\bin'),
        os.path.expandvars(r'C:\Ruby*\bin'),
        os.path.expandvars(r'%PROGRAMFILES%\Ruby*\bin'),
        *get_gem_paths()
    ]

    def expand_wildcards(paths):
        expanded = []
        for p in paths:
            if '*' in p:
                expanded.extend(glob.glob(p))
            else:
                expanded.append(p)
        return expanded

    search_paths = expand_wildcards(possible_paths)
    executables = ['rubocop.bat', 'rubocop.cmd', 'rubocop']

    # First try PATH
    rubocop_in_path = which('rubocop')
    if rubocop_in_path:
        ruby_path = os.path.dirname(os.path.dirname(rubocop_in_path))
        print(f"Found RuboCop in PATH: {rubocop_in_path}")
        return ruby_path, rubocop_in_path

    # Then search all possible locations
    for base_path in search_paths:
        if os.path.exists(base_path):
            for exe in executables:
                full_path = os.path.join(base_path, exe)
                if os.path.exists(full_path):
                    ruby_path = os.path.dirname(os.path.dirname(base_path))
                    print(f"Found RuboCop at: {full_path}")
                    return ruby_path, full_path

    raise RuntimeError("RuboCop not found! Please run: gem install rubocop")

# Replace existing Ruby path detection with enhanced version
try:
    ruby_path, rubocop_path = find_rubocop_installation()
except Exception as e:
    print(f"Warning: {str(e)}")
    ruby_path = rubocop_path = None

# Add Ruby environment variables to ensure proper execution
if ruby_path:
    os.environ['RUBY_PATH'] = ruby_path
    os.environ['PATH'] = os.pathsep.join([
        os.path.join(ruby_path, 'bin'),
        os.environ.get('PATH', '')
    ])

# Update Analysis with conditional Ruby paths
pathex_list = [os.path.abspath('.')]
if ruby_path:
    pathex_list.append(ruby_path)

# Collect all dynamic libraries at once
qt_libs = collect_dynamic_libs("PyQt5")
win_libs = []
for lib_name in ["win32gui", "win32api"]:
    try:
        win_libs.extend(collect_dynamic_libs(lib_name))
    except Exception as e:
        print(f"Warning: Could not collect {lib_name} libraries: {e}")

binaries_list = qt_libs + win_libs
if rubocop_path:
    binaries_list.append((rubocop_path, "."))

# Collect Qt plugins with enhanced error handling
qt_plugins = [
    ("PyQt5/Qt5/plugins/platforms", "platforms"),
    ("PyQt5/Qt5/plugins/styles", "styles"),
    ("PyQt5/Qt5/plugins/imageformats", "imageformats"),
    ("PyQt5/Qt5/plugins/iconengines", "iconengines"),
    ("PyQt5/Qt5/plugins/platforminputcontexts", "platforminputcontexts"),
    ("PyQt5/Qt5/plugins/platformthemes", "platformthemes"),
    ("PyQt5/Qt5/plugins/generic", "generic"),
    ("PyQt5/Qt5/translations", "translations")
]

# Enhanced file collection with error handling
added_files = []
for source, target in qt_plugins:
    try:
        plugin_files = collect_data_files('PyQt5', subdir=source)
        if plugin_files:
            added_files.extend(plugin_files)
        else:
            print(f"Warning: No files found for plugin: {source}")
    except Exception as e:
        print(f"Warning: Could not collect files from {source}: {e}")

# Update Analysis configuration
block_cipher = None  # Define block_cipher used in Analysis and PYZ configurations
a = Analysis(
    ["assistant_ui.py"],
    pathex=pathex_list,
    binaries=binaries_list,
    datas=[
        ("styles.qss", "."),
        ("resources", "resources"),
        ("app_icon.ico", "."),
        *added_files
    ],
    hiddenimports=[
        "openai", "pyttsx3", "enchant", "speech_recognition", "cryptography",
        "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtWidgets", "PyQt5.QtNetwork",
        "PyQt5.QtPrintSupport", "PyQt5.QtSvg", "PyQt5.QtXml", "pyqtconfig"
    ],
    hookspath=[],
    runtime_hooks=[RUNTIME_HOOK],
    excludes=["tkinter", "matplotlib"],
    cipher=block_cipher,
    noarchive=False
)

# Create the final executable
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TypingAssistant',
    debug=False,
    strip=False,
    upx=True,
    upx_exclude=[
        'vcruntime140.dll', 'python*.dll', 'Qt5*.dll', 'ruby*.dll', 'qwindows.dll',
        'qsvg.dll', 'qtsvg.dll', 'platforms/*', 'styles/*', 'imageformats/*',
        'qwindowsvistastyle.dll', 'translations/*', 'platformthemes/*', 'iconengines/*'
    ],
    runtime_tmpdir=None,
    console=True,
    icon='app_icon.ico',
    version='file_version_info.txt'
)

# Enhanced cleanup with multiple retries
def remove_with_retry(file_path, max_retries=3):
    for i in range(max_retries):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            if i == max_retries - 1:
                print(f"Warning: Could not remove {file_path} after {max_retries} attempts: {e}")
            time.sleep(0.1)
    return False

# Clean up runtime hook
remove_with_retry(RUNTIME_HOOK)

