import imaplib
import email
from email.header import decode_header
from .config import Config
import time

class EmailClient:
    def __init__(self):
        self.server = Config.IMAP_SERVER
        self.user = Config.IMAP_USER
        self.password = Config.IMAP_PASSWORD
        self.imap = None

    def connect(self):
        """Connects to the IMAP server."""
        try:
            self.imap = imaplib.IMAP4_SSL(self.server)
            self.imap.login(self.user, self.password)
            print(f"Connected to {self.server} as {self.user}")
        except Exception as e:
            print(f"Connection failed: {e}")
            raise

    def disconnect(self):
        """Disconnects from the IMAP server."""
        if self.imap:
            try:
                self.imap.logout()
            except:
                pass

    def fetch_emails(self, limit=10, folder="INBOX"):
        """Fetches a batch of emails from the specified folder."""
        if not self.imap:
            self.connect()
        
        self.imap.select(folder)
        
        # Search for all emails (ALL) or Unseen (UNSEEN)
        # For this tool, we probably want to process everything in INBOX that isn't already organized?
        # Or just process the latest N emails.
        status, messages = self.imap.search(None, "ALL")
        
        email_ids = messages[0].split()
        # Process latest first
        email_ids = email_ids[::-1]
        
        fetched_emails = []
        count = 0
        
        for e_id in email_ids:
            if count >= limit:
                break
                
            try:
                res, msg = self.imap.fetch(e_id, "(RFC822)")
                for response in msg:
                    if isinstance(response, tuple):
                        msg = email.message_from_bytes(response[1])
                        
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                            
                        sender = msg.get("From")
                        
                        # Get a snippet of the body
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))
                                
                                if "attachment" not in content_disposition:
                                    if content_type == "text/plain":
                                        try:
                                            body = part.get_payload(decode=True).decode()
                                        except:
                                            pass
                                        break # Only take the first text part
                        else:
                            try:
                                body = msg.get_payload(decode=True).decode()
                            except:
                                pass
                                
                        # Truncate body for snippet
                        snippet = body[:500].replace("\n", " ")
                        
                        fetched_emails.append({
                            "id": e_id,
                            "subject": subject,
                            "sender": sender,
                            "snippet": snippet
                        })
                        count += 1
            except Exception as e:
                print(f"Error fetching email {e_id}: {e}")
                continue
                
        return fetched_emails

    def create_folder(self, folder_name):
        """Creates a folder if it doesn't exist."""
        if not self.imap:
            self.connect()
            
        try:
            self.imap.create(folder_name)
        except imaplib.IMAP4.error:
            # Folder likely already exists
            pass

    def move_email(self, email_id, folder_name):
        """Moves an email to the specified folder."""
        if not self.imap:
            self.connect()
            
        # Ensure folder exists
        self.create_folder(folder_name)
        
        try:
            # Copy to new folder
            result = self.imap.copy(email_id, folder_name)
            if result[0] == 'OK':
                # Mark for deletion in original folder
                self.imap.store(email_id, '+FLAGS', '\\Deleted')
                self.imap.expunge()
                return True
        except Exception as e:
            print(f"Error moving email {email_id} to {folder_name}: {e}")
            return False
        return False
