import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

def create_typing_assistant():
    """Create a typing assistant with OpenAI's Assistant API"""
    try:
        assistant = client.beta.assistants.create(
            name="Adaptive Typing Assistant",
            description="An intelligent typing assistant that helps users with motor control challenges and cognitive disabilities",
            model="gpt-4o-mini",  # Using the more cost-efficient model
            instructions="""You are an adaptive typing assistant designed to help users with motor control challenges and cognitive disabilities. Your role is to:
            1. Provide real-time text correction and suggestions
            2. Adapt to the user's typing patterns and common mistakes
            3. Offer clear, supportive feedback
            4. Help improve text clarity while maintaining the user's intended meaning
            5. Support multiple correction modes (spelling, grammar, clarity)
            6. Be patient and encouraging in all interactions""",
            tools=[{
                "type": "function",
                "function": {
                    "name": "correct_text",
                    "description": "Corrects text based on user's input and preferences",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "The text to be corrected"
                            },
                            "correction_mode": {
                                "type": "string",
                                "enum": ["spelling", "grammar", "clarity", "comprehensive"],
                                "description": "The type of correction to apply"
                            },
                            "severity": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "How aggressive the corrections should be"
                            }
                        },
                        "required": ["text", "correction_mode", "severity"]
                    }
                }
            }],
            metadata={
                "version": "2.0",
                "max_text_length": "2000",
                "supports_streaming": "true"
            }
        )
        
        print(f"Assistant created successfully with ID: {assistant.id}")
        print(f"Name: {assistant.name}")
        print(f"Description: {assistant.description}")
        return assistant.id
        
    except Exception as e:
        print(f"Error creating assistant: {str(e)}")
        return None

if __name__ == "__main__":
    assistant_id = create_typing_assistant()
    if assistant_id:
        print("\nAssistant is ready to help with typing assistance!")
