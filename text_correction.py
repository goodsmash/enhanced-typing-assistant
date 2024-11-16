import os
import time
import asyncio
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TextCorrector:
    def __init__(self):
        self.client = OpenAI()
        self.assistant_id = "asst_tXilod6dvj2WtdMO3u6zpDLj"
        
    async def correct_text(self, text: str, mode: str = "comprehensive", severity: str = "medium", language: str = "English") -> str:
        """
        Correct text using the OpenAI Assistant.
        
        Args:
            text (str): The text to correct
            mode (str): One of ["spelling", "grammar", "clarity", "comprehensive"]
            severity (str): One of ["low", "medium", "high"]
            language (str): The language of the text
            
        Returns:
            str: The corrected text
        """
        try:
            # Input validation
            if not text or not isinstance(text, str):
                raise ValueError("Invalid input text")
                
            if mode not in ["spelling", "grammar", "clarity", "comprehensive"]:
                mode = "comprehensive"
                
            if severity not in ["low", "medium", "high"]:
                severity = "medium"
            
            # Create a thread
            thread = await self.client.beta.threads.create()
            
            # Add the message to the thread
            message = await self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=f"Please correct this {language} text. Mode: {mode}, Severity: {severity}\n\nText: {text}"
            )
            
            # Run the assistant
            run = await self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id
            )
            
            # Wait for completion with timeout
            timeout = 30  # 30 seconds timeout
            start_time = time.time()
            while True:
                run = await self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                
                if run.status == "completed":
                    break
                elif run.status in ["failed", "cancelled", "expired"]:
                    raise Exception(f"Assistant run failed with status: {run.status}")
                elif time.time() - start_time > timeout:
                    await self.client.beta.threads.runs.cancel(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                    raise TimeoutError("Assistant response timed out")
                    
                await asyncio.sleep(1)  # Wait 1 second before checking again
            
            # Get the assistant's response
            messages = await self.client.beta.threads.messages.list(
                thread_id=thread.id
            )
            
            if not messages.data:
                raise Exception("No response from assistant")
                
            # Return the corrected text from the assistant's last message
            corrected_text = messages.data[0].content[0].text.value
            
            # Clean up the thread
            await self.client.beta.threads.delete(thread.id)
            
            return corrected_text
            
        except Exception as e:
            print(f"Error in text correction: {str(e)}")
            return text  # Return original text if correction fails
            
    async def cleanup(self):
        """Clean up any resources"""
        pass  # Add cleanup code if needed
