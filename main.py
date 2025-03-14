import gspread
from oauth2client.service_account import ServiceAccountCredentials
import uuid
import os
from dotenv import load_dotenv

class GoogleSheetProcessor:
    def __init__(self):
        """
        Initialize connection to the Google Sheet using credentials from .env file
        """
        load_dotenv()
        creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE")
        sheet_url = os.getenv("GOOGLE_SHEET_URL")
        
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_url(sheet_url)
    
    def process(self):
        """
        Moves all rows from 'A' sheet to 'A_processed' sheet with an added ID column.
        """
        try:
            sheet_A = self.sheet.worksheet("responses")
            sheet_A_processed = self.sheet.worksheet("registered")
            
            # Check if "A_processed" sheet exists, otherwise create it
            try:
                sheet_A_processed = self.sheet.worksheet("registered")
            except gspread.exceptions.WorksheetNotFound:
                sheet_A_processed = self.sheet.add_worksheet(title="registered", rows="100", cols="20")
            
            data = sheet_A.get_all_values()
            if not data:
                print("No data found in 'A' sheet.")
                return
            
            # Add ID column header
            # headers = data[0] + ["ID"]
            # processed_data = [headers]
            processed_data = []
            
            # Process rows
            for i, row in enumerate(data[1:], start=2):  # Exclude headers
                print(row)
                if (row[1]=='' or row[3]=='V'):
                    continue
                row[-1] = str(uuid.uuid4())  # Add unique ID
                processed_data.append(row)
                sheet_A.update_cell(i, 4, "V")
            # Clear A_processed and insert new data
            sheet_A_processed.insert_rows(processed_data, row=2)
            
            # # Clear the original sheet A
            # sheet_A.clear()
            print("Processing complete: Data moved to 'A_processed' with ID column added.")
        
        except Exception as e:
            print(f"Error processing sheet: {e}")

# Example usage
# Create a .env file with GOOGLE_CREDENTIALS_FILE and GOOGLE_SHEET_URL
processor = GoogleSheetProcessor()
processor.process()
