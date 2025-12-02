from openai import OpenAI, AzureOpenAI
from .config import Config
import time

class EmailClassifier:
    def __init__(self):
        self.use_azure = False
        
        if Config.AZURE_OPENAI_API_KEY:
            self.use_azure = True
            self.client = AzureOpenAI(
                api_key=Config.AZURE_OPENAI_API_KEY,
                api_version=Config.AZURE_OPENAI_API_VERSION,
                azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
            )
            self.model_name = Config.AZURE_DEPLOYMENT_NAME
            print(f"Using Azure OpenAI (Deployment: {self.model_name})")
        elif Config.OPENAI_API_KEY:
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            self.model_name = "gpt-4o-mini"
            print("Using Standard OpenAI")
        else:
            raise ValueError("No valid API Key found for OpenAI or Azure.")
        
    def classify(self, subject, sender, snippet):
        """
        Classifies an email into one of the predefined categories.
        """
        categories_str = ", ".join(Config.CATEGORIES)
        
        prompt = f"""
        You are an email organization assistant. 
        Classify the following email into exactly one of these categories: {categories_str}.
        If none fit perfectly, choose the closest one or "Personal".
        
        Email Details:
        Sender: {sender}
        Subject: {subject}
        Content Snippet: {snippet}
        
        Return ONLY the category name. Do not add any explanation or punctuation.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that categorizes emails."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=20,

            )
            
            category = response.choices[0].message.content.strip()
            clean_category = self._clean_category(category)
            return clean_category
            
        except Exception as e:
            print(f"Error classifying email: {e}")
            return "Uncategorized"

    def _clean_category(self, category):
        """
        Ensures the category matches one of the allowed ones, or defaults to Personal.
        """
        # Remove any potential extra whitespace or punctuation
        category = category.strip().replace(".", "")
        
        # Case-insensitive match
        for valid_cat in Config.CATEGORIES:
            if valid_cat.lower() == category.lower():
                return valid_cat
        
        # If no match found, default to Personal
        return "Personal"
