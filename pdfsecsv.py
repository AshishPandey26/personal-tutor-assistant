import fitz  # PyMuPDF
import pandas as pd
import google.generativeai as genai
import os

# === Set your Gemini API key here ===
GOOGLE_API_KEY = "AIzaSyDPeBzC_Z_Ur1bel0inbPhM8tIGDSOZPy0"
genai.configure(api_key=GOOGLE_API_KEY)

# Load Gemini model (Flash is faster for structured tasks)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# === PDF to Text Function ===
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# === Gemini Prompt for Structured Output ===
def get_structured_data(raw_text, class_name="10", subject="Science", unit="1", chapter=""):
    prompt = f"""
You are a textbook content extractor. Based on the provided textbook content, extract a list of *topics* as rows in the following format, using | as separator:

Class | Subject | Unit | Chapter | Topic

Only return actual topics found in the content. A topic can be a heading, subheading, or concept described (e.g., "Ohm's Law", "Resistance", "Electric Circuit"). Each topic should be on a separate line.

Repeat Class, Subject, Unit, and Chapter for every topic.

Class: {class_name}
Subject: {subject}
Unit: {unit}
Chapter: {chapter or "Infer from content if not given"}

Now extract topics from the following content:
\"\"\"
{raw_text}
\"\"\"

Only return rows like:
10 | Science | 1 | Electricity | Ohm’s Law
10 | Science | 1 | Electricity | Current and Voltage
...
"""
    response = model.generate_content(prompt)
    return response.text.strip()

# === Save to CSV ===
def save_to_csv(data_text, output_path):
    rows = []
    for line in data_text.splitlines():
        # Skip empty lines
        if not line.strip():
            continue
        # Split on pipe separator
        parts = [part.strip() for part in line.split("|")]
        if len(parts) == 5:
            rows.append(parts)
        else:
            print(f"⚠ Skipping malformed line: {line}")

    # Create DataFrame
    df = pd.DataFrame(rows, columns=["Class", "Subject", "Unit", "Chapter", "Topic"])
    df.to_csv(output_path, index=False)
    print(f"✅ Saved to: {output_path}")


# === Main Function ===
def convert_pdf_to_csv(pdf_path, csv_path):
    print("🔍 Extracting text from PDF...")
    raw_text = extract_text_from_pdf(pdf_path)

    print("🤖 Sending to Gemini Flash 1.5...")
    structured_text = get_structured_data(raw_text)

    print("💾 Saving structured data to CSV...")
    save_to_csv(structured_text, csv_path)

# === Run ===
if _name_ == "_main_":
    pdf_path = "10class.pdf"  # Change to your PDF path
    csv_path = "output.csv"
    convert_pdf_to_csv(pdf_path, csv_path)