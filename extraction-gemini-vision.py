import os
import PIL.Image
import json
import csv
from google import genai


# Load API key from file
with open("apikey.txt", "r", encoding="utf-8") as f:
    api_key = f.read().strip()

image_dir = "./files_images/"

# Initialize Gemini API client
client = genai.Client(api_key=api_key)


# Read the prompt and input files
def read_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()

# Flatten and remove newlines
def flatten_field(value):
    if isinstance(value, list):
        return " ".join(item.replace("\n", " ").strip() for item in value)
    elif isinstance(value, str):
        return value.replace("\n", " ").strip()
    else:
        return ""

# Function to process each image and save the result as JSON and TSV
def process_image(image_path):
    image_name = os.path.basename(image_path)
    image = PIL.Image.open(image_path)

    prompt = read_file("prompt-vision.txt")

    # Generate content using Gemini API
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt, image]
    )

    # Clean response
    cleaned_response = response.text.strip()
    if cleaned_response.startswith("```json"):
        cleaned_response = cleaned_response.replace("```json", "").strip()
    if cleaned_response.endswith("```"):
        cleaned_response = cleaned_response[:-3].strip()

    # Save as JSON
    json_filename = os.path.splitext(image_name)[0] + ".json"
    json_path = os.path.join(image_dir, json_filename)
    with open(json_path, "w", encoding="utf-8") as json_file:
        json_file.write(cleaned_response)

    # Parse and convert to TSV
    try:
        data = json.loads(cleaned_response)

        tsv_filename = os.path.splitext(image_name)[0] + ".tsv"
        tsv_path = os.path.join(image_dir, tsv_filename)

        with open(tsv_path, "w", encoding="utf-8", newline="") as tsv_file:
            writer = csv.writer(tsv_file, delimiter="\t")
            writer.writerow([
                "textbook", "id", "full_ex", "num", "indicator", "instruction",
                "hint", "example", "statement", "instruction_hint_example",
                "label", "grandtype", "stratify_key"
            ])

            for exercise in data:
                props = exercise.get("properties", {})
                id_val = exercise.get("id", "none")
                numero = props.get("numero", "none")

                consignes = flatten_field(props.get("consignes", []))
                conseil = flatten_field(props.get("conseil", ""))
                exemple = flatten_field(props.get("exemple", ""))
                enonce = flatten_field(props.get("enonce", ""))

                instruction_hint_example = " ".join(filter(None, [consignes, conseil, exemple]))
                full_ex = " ".join(filter(None, [consignes, conseil, exemple, enonce]))

                writer.writerow([
                    "none", id_val, full_ex, numero, "none", consignes,
                    conseil, exemple, enonce, instruction_hint_example,
                    "none", "none", "none"
                ])
    except Exception as e:
        print(f"Error processing TSV for {image_name}: {e}")

# Iterate over each image in the directory
for filename in os.listdir(image_dir):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        image_path = os.path.join(image_dir, filename)
        process_image(image_path)
