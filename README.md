# Songs of Syx Difficulty Editor

A simple, open-source tool to edit hidden difficulty settings in **Songs of Syx** save files.

## 📖 Description
This tool allows you to modify internal difficulty variables that are not exposed in the game's standard difficulty menu. Whether you want to tweak **Loyalty**, adjust **Research Speed**, or modify **Opinion** modifiers, this editor gives you full control over your save file's difficulty parameters.

It automatically handles the decompression and re-compression of the game's save format, making editing safe and easy.

## ⚠️ Important Prerequisites
1. **Disable Steam Cloud**: Before editing, ensure Steam Cloud synchronization is disabled for the game. If enabled, Steam might overwrite your edited save file with the cloud version. After it should run as normal and you can turn it back on.
2. **Verify Save File Format**: This tool is designed for save files with the specific version identifier in their name. Look for files ending with a pattern similar to `-19b03b754bd-460010-402243d7-0` (e.g., `mysave-19b03b754bd-460010-402243d7-0.save`). After editing, make sure it has it or won't be detected.

## 🚀 Quick Start Guide

### 1. Installation
No installation is required! Just ensure you have **Python 3** installed on your computer.
- [Download Python](https://www.python.org/downloads/) (Make sure to check "Add Python to PATH" during installation).

### 2. Running the Editor
- **Windows**: Double-click the included `run_editor.bat` file.
- **Mac/Linux**: Open a terminal and run `python difficulty_editor.py`.

### 3. How to Edit Your Save
1.  **Load**: Click **"Load Save File"** and select your save file.
    - *Location:* Usually `C:\Users\YourName\AppData\Roaming\songsofsyx\saves`.
2.  **Edit**: The tool will list all detected settings (e.g., `BEHAVIOUR_LOYALTY`, `CIVIC_INNOVATION`).
    - **1.0** = Normal Difficulty
    - **0.4** = Hard Difficulty (Game Default for Hard)
    - **1.5** = Easy Difficulty
3.  **Save**: Click **"Save Changes"**.
    - The tool will create a **new** file named `edited_yoursave.save` to prevent overwriting your original progress.

## ✨ Features
- **Auto-Detection**: Scans your save file to find every available difficulty variable dynamically.
- **Safe Mode**: Never overwrites your original file; always creates a copy.
- **Bulk Tools**: One-click buttons to set everything to Easy, Normal, or Hard.
- **Cross-Platform**: Works on any system that runs Python.

## 🤖 Disclaimer
**This software was generated with the assistance of Artificial Intelligence.**
While the code has been tested and verified to work, please use it at your own risk. Always keep a backup of your original save files before using third-party tools.

## 🛠 Technical Details
For developers or the curious:
The tool searches for the `CIVIC_OPINION` block in the binary save file. It parses the structure:
`[Length (2 bytes)] [Name (UTF-16LE)] [Value (Double)]`
It includes logic to handle specific byte-alignment quirks of the engine where values sometimes overlap with the variable name string.

## License
MIT License. Feel free to modify, distribute, and improve!

