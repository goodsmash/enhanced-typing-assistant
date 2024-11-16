from modules.api_manager import APIManager

def set_api_key():
    api_manager = APIManager()
    api_key = input("Enter your OpenAI API Key: ")
    if api_manager.set_openai_api_key(api_key):
        print("API key set and encrypted successfully.")
    else:
        print("Failed to set API key.")

if __name__ == "__main__":
    set_api_key()
