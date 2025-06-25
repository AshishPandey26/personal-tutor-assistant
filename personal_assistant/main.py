import google.generativeai as genai
import json
import os

# Load memory
if os.path.exists("memory.json"):
    with open("memory.json", "r") as f:
        memory = json.load(f)
else:
    memory = {}

# Setup Gemini
genai.configure(api_key="AIzaSyCmKJh5T9tOLYAKZ7wQybIepcIYx2gsFh4")
model = genai.GenerativeModel("gemini-1.5-flash")

def save_memory():
    with open("memory.json", "w") as f:
        json.dump(memory, f)

print("🤖 Hello! I'm your simple AI assistant. Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Assistant: Bye! Talk to you soon.")
        break

    # Check for basic memory interaction
    if "my name is" in user_input.lower():
        name = user_input.split("is")[-1].strip().capitalize()
        memory["name"] = name
        save_memory()
        print(f"Assistant: Nice to meet you, {name}!")
        continue

    if "what's my name" in user_input.lower() or "do you remember my name" in user_input.lower():
        if "name" in memory:
            print(f"Assistant: Your name is {memory['name']}.")
        else:
            print("Assistant: I don't know your name yet.")
        continue

    # Use Gemini API
    try:
        response = model.generate_content(user_input)
        print(f"Assistant: {response.text}")
    except Exception as e:
        print("Assistant: Sorry, I faced an error:", str(e))
