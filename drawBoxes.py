import os
import json
import cv2

from pathlib import Path

# Base directory = where this script is located
base_dir = Path(__file__).parent.resolve()

# Paths relative to the script directory
images_path = base_dir / "files"
json_path = base_dir / "output" / "detImages" / "predict"
output_path = base_dir / "files_images"


# Create output folder if not exists
os.makedirs(output_path, exist_ok=True)

# Iterate over all json files
for json_file in os.listdir(json_path):
    if not json_file.endswith(".json"):
        continue

    json_file_path = os.path.join(json_path, json_file)

    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Assume JSON filename corresponds to the image name (replace extension if needed)
    image_name = os.path.splitext(json_file)[0] + ".png"  # change if jpg/jpeg
    image_file = os.path.join(images_path, image_name)

    if not os.path.exists(image_file):
        print(f"[WARN] Image not found for {json_file}")
        continue

    # Load image
    img = cv2.imread(image_file)
    if img is None:
        print(f"[WARN] Could not load {image_file}")
        continue

    # Extract page number from filename (example: "page86.png" -> 86)
    page_num = ''.join([c for c in image_name if c.isdigit()])
    if not page_num:
        page_num = "0"

    # Draw boxes
    for shape in data.get("shapes", []):
        pts = shape["points"]
        x1, y1 = map(int, pts[0])
        x2, y2 = map(int, pts[1])
        shape_id = shape["id"]

        # --- Draw rectangle in RED ---
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 3)

        # Label text
        label_text = f"p{page_num}c{shape_id}"

        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.8   # slightly bigger for readability
        thickness = 2

        # Get text size
        (text_w, text_h), baseline = cv2.getTextSize(label_text, font, scale, thickness)

        # Compute center of the box
        box_cx = (x1 + x2) // 2
        box_cy = (y1 + y2) // 2

        # Position of text (top-left corner for putText)
        text_x = box_cx - text_w // 2
        text_y = box_cy + text_h // 2

        # Background rectangle coordinates
        tx1 = text_x - 5
        ty1 = text_y - text_h - 5
        tx2 = text_x + text_w + 5
        ty2 = text_y + 5

        # --- Semi-transparent black background (80%) ---
        overlay = img.copy()
        cv2.rectangle(overlay, (tx1, ty1), (tx2, ty2), (0, 0, 0), -1)
        alpha = 0.8
        img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

        # --- Put white text ---
        cv2.putText(img, label_text, (text_x, text_y), font, scale, (255, 255, 255), thickness, cv2.LINE_AA)

    # Save result
    out_file = os.path.join(output_path, image_name)
    cv2.imwrite(out_file, img)
    print(f"[OK] Saved {out_file}")
