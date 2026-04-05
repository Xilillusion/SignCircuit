# SignCircuit

SignCircuit is a Python-based automation bot framework designed for executing scripted actions with conditional logic. It supports mouse and keyboard input simulation, image recognition, OCR (Optical Character Recognition), and time-based conditions, making it suitable for automating repetitive tasks in applications or games.

## Features

- **Script Execution**: Load and execute YAML-based scripts with sequential actions
- **Conditional Logic**: Support for complex conditions including:
  - Time-based conditions (date, hour, minute, second)
  - Pixel color matching
  - Image template matching
  - OCR text recognition (with fuzzy matching)
  - Logical operators (AND, OR, NOT)
- **Input Simulation**: Mouse clicks, movements, drags, and keyboard inputs
- **Randomization**: Add variance to actions for more natural behavior
- **Position Locator**: Built-in utility to display mouse coordinates for scripting
- **Multi-language OCR**: Support for multiple languages in text recognition
- **Image Processing**: Template matching and feature detection using OpenCV

## Installation

1. Clone or download the repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Dependencies

- `yaml`: For parsing script configuration files
- `pydirectinput`: For simulating mouse and keyboard inputs
- `tkinter`: GUI framework (usually included with Python)
- `mss`: For fast screen capture
- `Levenshtein`: For fuzzy string matching in OCR
- `PIL` (Pillow): Image processing
- `pytesseract`: OCR engine
- `paddleocr`: Alternative OCR engine with better accuracy
- `numpy`: Numerical operations for image processing
- `cv2` (OpenCV): Computer vision and image matching
- `imagehash`: Image hashing for comparison
- `keyboard`: For detecting exit key presses

## Usage

### Running the Bot

1. Start the bot:

```bash
python main.py
```

2. Enter the script filename when prompted (e.g., `script.yaml`)

3. The position locator window will open automatically to help with coordinate detection

4. Press `ESC` to stop the bot

### Position Locator

The locator utility displays current mouse coordinates in real-time:

```bash
python utils/locator.py
```

This opens a semi-transparent window showing X,Y coordinates that follows your mouse cursor.

### Creating Scripts

Scripts are written in YAML format with the following structure:

```yaml
description: "Example automation script"
resolution: [1920, 1080]  # Target screen resolution
actions:
  - type: "log"
    message: "Starting automation"

  - type: "click"
    args: [100, 200]  # X, Y coordinates
    target:
      type: "pixel"
      pos: [100, 200]
      colour: [255, 0, 0]  # RGB color to wait for
    randomness:
      variance: 5  # Randomize click position within 5 pixels

  - type: "wait"
    duration: 2.0
    randomness:
      variance: 0.5
      deviation: 0.1

  - type: "press"
    args: ["enter"]

  - type: "move"
    args: [500, 300]
    kwargs:
      tween: "easeInOutQuad"  # Smooth movement
```

### Action Types

- `log`: Log a message
- `script`: Load and execute another script
- `click`: Left-click at coordinates
- `move`: Move mouse to coordinates
- `dragTo`: Drag from current position to coordinates
- `mouseDown`/`mouseUp`: Mouse button press/release
- `keyDown`/`keyUp`/`press`: Keyboard input
- `wait`: Pause execution

### Condition Types

Conditions can be attached to actions via the `target` field:

- `pixel`: Wait for specific color at position
- `area`: Image template matching or feature detection
- `word`: OCR text recognition with fuzzy matching
- `date`/`day`/`hour`/`minu`/`second`: Time-based conditions
- `AND`/`OR`/`NOT`: Logical combinations

## Configuration

Scripts support various configuration options:

- **Resolution**: Target screen resolution for coordinate scaling
- **Randomness**: Add variance to timing and positioning for more human-like behavior
- **OCR Settings**: Language selection and confidence thresholds
- **Image Matching**: Confidence levels and preprocessing options

## Troubleshooting

- **DPI Awareness**: The bot enables DPI awareness for accurate coordinate handling on high-DPI displays
- **Permissions**: May require administrator privileges for input simulation
- **OCR Accuracy**: Ensure Tesseract is installed for pytesseract, or use paddleocr for better results
- **Screen Capture**: Uses MSS for fast, reliable screen capture
- **Process Termination**: Use ESC key to cleanly exit the bot

## License

This project is provided as-is for educational and automation purposes. Use responsibly and in accordance with applicable laws and terms of service.