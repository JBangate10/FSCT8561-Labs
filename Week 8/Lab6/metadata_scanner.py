import os
import csv
import base64
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime

IMAGE_FOLDER = "Images"
OUTPUT_FILE = "metadata_report.csv"

results = []
secret_steps = []

POINTS = {
    "gps": 10,
    "secret": 5,
    "timestamp": 5,
    "editing": 5
}

def get_metadata(path):
    metadata = {}
    try:
        img = Image.open(path)
        exif = img.getexif()

        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            metadata[tag] = value
    except:
        pass

    return metadata

def detect_secret(meta):
    fields = ["UserComment", "ImageDescription", "Software", "Copyright", "MakerNote"]

    for f in fields:
        if f in meta:
            text = str(meta[f])

            if len(text) > 10:
                try:
                    decoded = base64.b64decode(text).decode()
                    return decoded
                except:
                    return text
    
    return None

def check_gps(meta):
    if "GPSInfo" in meta:
        return True
    return False

def check_editing(meta):
    if "Software" in meta:
        return True
    return False

def timestamp_anomaly(meta, file):
    if "DateTimeOriginal" not in meta:
        return False
    
    try:
        exif_time = datetime.strptime(meta["DateTimeOriginal"], "%Y:%m:%d: %H:%M:%S")
        file_time = datetime.fromtimestamp(os.path.getmtime(file))

        if abs((file_time - exif_time).total_seconds()) > 3600:
            return True
    except:
        pass

    return False

for file in os.listdir(IMAGE_FOLDER):
    if not file.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    path = os.path.join(IMAGE_FOLDER, file)
    meta = get_metadata(path)

    gps = check_gps(meta)
    editing = check_editing(meta)
    time_issue = timestamp_anomaly(meta, path)
    secret = detect_secret(meta)

    risk_score = 0

    if secret:
        risk_score += POINTS["secret"]
        secret_steps.append(secret)
    if gps:
        risk_score += POINTS["gps"]
    if time_issue:
        risk_score += POINTS["timestamp"]
    if editing:
        risk_score += POINTS["editing"]
    
    results.append([
        file,
        meta.get("Make"),
        meta.get("Model"),
        meta.get("DateTimeOriginal"),
        meta.get("Software"),
        gps,
        time_issue,
        editing,
        secret,
        risk_score
    ])

full_secret = "".join(secret_steps)

print("\nReconstructed Secret:")
print(full_secret)

with open(OUTPUT_FILE, "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow([
        "Image",
        "Camera Make",
        "Camera Model",
        "DateTimeOriginal",
        "Software",
        "GPS Present",
        "Timestamp Anomaly",
        "Editing Detected",
        "Secret Step",
        "Risk Score"
    ])

    writer.writerow(results)

print("\nReport saved to:", OUTPUT_FILE)