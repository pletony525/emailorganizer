import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
    IMAP_USER = os.getenv("IMAP_USER")
    IMAP_PASSWORD = os.getenv("IMAP_PASSWORD")
    
    # OpenAI Config
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Azure Config
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4o-mini")
    
    # Load categories from env or use defaults
    _categories_env = os.getenv("EMAIL_CATEGORIES")
    if _categories_env:
        CATEGORIES = [c.strip() for c in _categories_env.split(",") if c.strip()]
    else:
        CATEGORIES = [
            "Jobs",
            "School",
            "Finance",
            "Promotions",
            "Social",
            "Personal",
            "Travel",
            "Receipts"
        ]

    # Batch size for processing
    BATCH_SIZE = 10
    
    # Delay between batches to avoid rate limits (seconds)
    BATCH_DELAY = 1

    @staticmethod
    def validate():
        missing = []
        if not Config.IMAP_USER:
            missing.append("IMAP_USER")
        if not Config.IMAP_PASSWORD:
            missing.append("IMAP_PASSWORD")
            
        # Check for either OpenAI or Azure
        if not Config.OPENAI_API_KEY and not Config.AZURE_OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY or AZURE_OPENAI_API_KEY")
            
        if Config.AZURE_OPENAI_API_KEY:
            if not Config.AZURE_OPENAI_ENDPOINT:
                missing.append("AZURE_OPENAI_ENDPOINT")
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
