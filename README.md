# Mouse Position Display

This project includes a utility to display the current mouse position on the screen.

## Usage

To display the mouse position, run the locator.py script:

```bash
python utils/locator.py
```

This will open a small, semi-transparent window that shows the current mouse coordinates (X, Y) and follows the mouse cursor around the screen.

## Requirements

Install the required packages:

```bash
pip install -r requirements.txt
```

## Troubleshooting

- If the window doesn't appear, ensure you have tkinter installed (usually comes with Python).
- If pyautogui fails, try installing it with pip.
- The window is set to always stay on top; if it interferes, you can close it by terminating the script.