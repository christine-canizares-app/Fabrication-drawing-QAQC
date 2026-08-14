from google import genai

# Paste your API key inside the quotes below
API_KEY = "AQ.Ab8RN6IvEhkBO5K4P_ojKTG-9zEmsiled3INIe-IOVwxVcbzxQ"

client = genai.Client(api_key=API_KEY)

print("--- AVAILABLE MODELS ---")
for model in client.models.list():
    if "generateContent" in model.supported_actions:
        print(model.name)
