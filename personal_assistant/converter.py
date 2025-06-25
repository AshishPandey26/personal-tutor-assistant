import os
import re
import pandas as pd
from io import StringIO
from PyPDF2 import PdfReader
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Step 1: Extract PDF Text
def extract_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            full_text += content + "\n"
    return full_text

# Step 2: Ask Gemini to convert it to structured syllabus
def ask_gemini_for_csv(pdf_text):
    prompt = f"""
You are a helpful assistant.

Analyze the following Class 9 Science syllabus content and extract it as structured data with the following columns:
Class, Subject, Unit Number, Chapter Number, Chapter Name, Chapter Topics (as bullet points or semicolon-separated list)

Return the data in a CSV or Markdown table format.

Here is the text:
{text[:25000]}
"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

# Step 3: Convert Markdown table (if present) to CSV-compatible string
def markdown_to_csv(markdown_text):
    lines = [line for line in markdown_text.split("\n") if line.strip() and not line.strip().startswith("|---")]
    cleaned = [re.sub(r"^\||\|$", "", line).strip() for line in lines if "|" in line]
    csv_ready = "\n".join([",".join(cell.strip() for cell in row.split("|")) for row in cleaned])
    return csv_ready

# Step 4: Save CSV
def save_csv_from_output(output_text, filename="class9_syllabus_ai.csv"):
    # Try to parse as markdown or plain csv
    try:
        if "|" in output_text:
            csv_data = markdown_to_csv(output_text)
        else:
            csv_data = output_text

        df = pd.read_csv(StringIO(csv_data))
        df.to_csv(filename, index=False)
        print(f"[+] CSV saved to: {filename}")
    except Exception as e:
        print("[!] Failed to convert Gemini output to CSV.")
        print("[Gemini Output]:")
        print(output_text)
        raise e

# Main Script
if __name__ == "__main__":
    pdf_path = "10class.pdf"  # Change if needed
    print("[*] Reading PDF...")
    text = extract_pdf_text(pdf_path)

    print("[*] Sending to Gemini...")
    output = ask_gemini_for_csv(text)

    print("[*] Parsing and saving CSV...")
    save_csv_from_output(output)
