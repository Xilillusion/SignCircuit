"""
- type: "AND"
  cond1: dict
  cond2: dict
  else: dict
- type: "OR"
  cond1: dict
  cond2: dict
  else: dict
- type: "NOT"
  cond: dict
  else: dict
- type: "date" | "day" | "hour" | "minu" | "second"
  value: int
  operator: ">" | "<" | "==" | ">=" | "<="
  else: dict
- type: "word"
  level: int
         1    # Fuzzy match (Levenshtein distance)
         2    # NL
  value: str
  start: [int, int]
  end: [int, int]
  thershold: float
  language: str
  else: dict
- type: "pixel"
  pos: [int, int]
  colour: [int, int, int]
  else: dict
- type: "area"
  level: int
         1    # Pixel Check
         2    # Template match
         3    # cv2.ORB_create
  start: [int, int]
  end: [int, int]
  confidence: float
  grayscale: bool
  image_paths:
    - "image1.png"
    - "image2.png"
  else: dict
"""

from utils import log

# Time-based condition evaluation
def compare_time(condition):
    from datetime import datetime

    now = datetime.now()
    time_till = condition["value"]
    time_now = getattr(now, condition["type"])

    operator_map = {
        ">": lambda a, b: a > b,
        "<": lambda a, b: a < b,
        "==": lambda a, b: a == b,
        "=": lambda a, b: a == b,
        ">=": lambda a, b: a >= b,
        "<=": lambda a, b: a <= b,
        "!=": lambda a, b: a != b
    }

    operator_func = operator_map.get(condition["operator"])
    if operator_func:
        return operator_func(time_now, time_till)
    else:
        log.error(f"Invalid operator {condition['operator']} in condition {condition}")
        exit()

def compare_time_weekday(condition):
    from datetime import datetime
    time_till = condition["value"]
    time_now = datetime.now().isoweekday()

    operator_map = {
        ">": lambda a, b: a > b,
        "<": lambda a, b: a < b,
        "==": lambda a, b: a == b,
        "=": lambda a, b: a == b,
        ">=": lambda a, b: a >= b,
        "<=": lambda a, b: a <= b,
        "!=": lambda a, b: a != b
    }

    operator_func = operator_map.get(condition["operator"])
    if operator_func:
        return operator_func(time_now, time_till)
    else:
        log.error(f"Invalid operator {condition['operator']} in condition {condition}")
        exit()

def get_screenshot(start: list, end: list):
    # Capture the specified screen area
    import mss
    left, top = start
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Assuming primary monitor
        width = monitor["width"] - left if not end else end[0]
        height = monitor["height"] - top if not end else end[1]
        region = {
            "top": top,
            "left": left,
            "width": width,
            "height": height
        }
        return sct.grab(region)

# Word-based condition evaluation
def compare_word(condition):
    from Levenshtein import ratio
    from PIL import Image
    
    value = condition.get("value", "")
    language = condition.get("language")
    level = condition.get("level", 1)
    threshold = condition.get("threshold", 0.8)
    start = condition.get("start", [0, 0])
    end = condition.get("end", [])

    screenshot = get_screenshot(start, end)
    pil_image = Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.bgra, "raw", "BGRX")
    
    if level == 1:
        # Use Levenshtein distance for fuzzy matching
        import pytesseract
        try:
            extracted = pytesseract.image_to_string(pil_image, lang=language).strip()
            return ratio(extracted, value) >= threshold
        except pytesseract.pytesseract.TesseractNotFoundError:
            log.error("Tesseract not found. Please install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki")
            return False
    else:
        # Use NL OCR and Levenshtein distance
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(lang=language, use_gpu=False)
        result = ocr.ocr(pil_image)
        extracted = ' '.join([line[1][0] for line in result[0]]) if result and result[0] else ''
        return ratio(extracted, value) >= threshold

# Colour-based condition evaluation
def compare_pixel(condition):
    import numpy as np
    pos = condition.get("position")
    threshold = condition.get("threshold", 0.9)
    colour = condition.get("colour")

    screenshot = get_screenshot([0, 0], [])
    pixel = np.array(screenshot)[pos]
    if np.allclose(pixel[:3], colour, atol=255*(1-threshold)):
        return True
    return False

# Image-based condition evaluation
def compare_picture(condition):
    import cv2
    import numpy as np

    image_paths = condition.get("image_paths")
    level = condition.get("level", 1)
    threshold = condition.get("threshold", 0.6)
    start = condition.get("start", [0, 0])
    end = condition.get("end", [])

    if type(image_paths) != "list":
        image_paths = list(image_paths)
    
    if condition.get("grayscale"):
        colour_func = cv2.COLOR_BGR2GRAY
        imread_func = cv2.IMREAD_COLOR
    else:
        colour_func = cv2.COLOR_BGRA2BGR
        imread_func = cv2.IMREAD_GRAYSCALE

    screenshot = get_screenshot(start, end)
    screen = cv2.cvtColor(np.array(screenshot), colour_func)

    if level == 1:
        import imagehash
        from PIL import Image

        screen_img = Image.frombytes("RGB", screen.size, screen.bgra, "raw", "BGRX")
        screen_hash = imagehash.average_hash(screen_img)

        for path in image_paths:
            img_hash = imagehash.average_hash(Image.open())

            if img_hash - screen_hash < threshold:
                return (end[0]-start[0], end[1]-start[1])

    elif level == 2:
        for path in image_paths:
            img = cv2.imread(path, imread_func)
            h, w = img.shape[:2]

            result = cv2.matchTemplate(screen, img, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= threshold:
                x = max_loc[0] + w//2
                y = max_loc[1] + h//2
                return (x, y)

    elif level == 3:
        orb = cv2.ORB_create(nfeatures=2000)
        kp1, des1 = orb.detectAndCompute(screen, None)
        total_kp = len(kp1)

        for path in image_paths:
            img = cv2.imread(path, imread_func)
            kp2, des2 = orb.detectAndCompute(img, None)
          
            # Use BFMatcher for feature matching
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(des1, des2)

            confodence = len([m for m in matches if m.distance < 30]) / total_kp
            if confodence < threshold:
                continue
            
            matches = sorted(matches, key=lambda x: x.distance)
            src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)

            M, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            if M is None:
                continue
            
            # Find the centre
            h, w = img.shape
            pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, min)

            centre = np.mean(dst, axis=0)[0]
            return (int(centre[0]), int(centre[1]))
    
    return False

def compare_audio(condition):
    log.error("Function not implemented")
    return True

def evaluate(condition):
    """Evaluate a conditional expression and return the result."""
    condition_type = condition.get("type")
    if condition_type:
        return CONDITION_MAP[condition_type](condition)

    log.error(f"Unknown condition type: {condition_type}")
    exit()

CONDITION_MAP = {
    # Logic gates
    'AND': lambda a: evaluate(a.get("cond1")) and evaluate(a.get("cond2")),
    'OR': lambda a: evaluate(a.get("cond1")) or evaluate(a.get("cond2")),
    'NOT': lambda a: not evaluate(a.get("cond")),
    'NAND': lambda a: not (evaluate(a.get("cond1")) and evaluate(a.get("cond2"))),
    'NOR': lambda a: not (evaluate(a.get("cond1")) or evaluate(a.get("cond2"))),
    'XOR': lambda a: evaluate(a.get("cond1")) != evaluate(a.get("cond2")),
    # Time-based conditions
    "day": compare_time,
    "weekday": compare_time_weekday,
    "hour": compare_time,
    "minute": compare_time,
    "second": compare_time,
    # Other condition types
    'word': compare_word,
    'audio': None,
    'pixel': compare_pixel,
    'picture': compare_picture
}
