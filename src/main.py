import argparse
import time
from .config import Config
from .email_client import EmailClient
from .classifier import EmailClassifier

def main():
    parser = argparse.ArgumentParser(description="AI Email Organizer")
    parser.add_argument("--dry-run", action="store_true", help="Run without moving emails")
    parser.add_argument("--limit", type=int, default=10, help="Number of emails to process")
    parser.add_argument("--batch-delay", type=float, default=1.0, help="Delay between emails")
    
    args = parser.parse_args()
    
    print("Starting AI Email Organizer...")
    if args.dry_run:
        print("MODE: DRY RUN (No emails will be moved)")
    else:
        print("MODE: LIVE (Emails WILL be moved)")
        
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        return

    client = EmailClient()
    classifier = EmailClassifier()
    
    try:
        client.connect()
        
        print(f"Fetching last {args.limit} emails...")
        emails = client.fetch_emails(limit=args.limit)
        
        print(f"Found {len(emails)} emails. Starting classification...")
        
        for i, email_data in enumerate(emails):
            print(f"\nProcessing {i+1}/{len(emails)}: {email_data['subject'][:50]}...")
            
            category = classifier.classify(
                email_data['subject'], 
                email_data['sender'], 
                email_data['snippet']
            )
            
            print(f"  -> Classified as: {category}")
            
            if not args.dry_run:
                success = client.move_email(email_data['id'], category)
                if success:
                    print(f"  -> Moved to {category}")
                else:
                    print(f"  -> FAILED to move")
            else:
                print(f"  -> [Dry Run] Would move to {category}")
                
            time.sleep(args.batch_delay)
            
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        client.disconnect()
        print("\nDone.")

if __name__ == "__main__":
    main()
