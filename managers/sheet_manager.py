import gspread
from oauth2client.service_account import ServiceAccountCredentials
import uuid
import os
from dotenv import load_dotenv
from datetime import datetime
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
            sheet_A_processed.append_row(processed_data)
            
            # # Clear the original sheet A
            # sheet_A.clear()
            print("Processing complete: Data moved to 'A_processed' with ID column added.")
        
        except Exception as e:
            print(f"Error processing sheet: {e}")

    def get_person_id(self, name, phone):
        sheet_person = self.sheet.worksheet("registered")
        data = sheet_person.get_all_values()
        for row in data[1:]:
            if row[1]!=name or row[2]!=phone:
                continue
            return row[3]
        return ''

    def get_person_name(self, id):
        sheet_person = self.sheet.worksheet("registered")
        data = sheet_person.get_all_values()
        for row in data[1:]:
            if (row[3]!=id):
                continue
            return row[1],row[2]
        return "",""

    def insert_item(self, item_name, description, owner_id):
        sheet_items = self.sheet.worksheet("items")
        sheet_items.append_row([datetime.now().strftime("%d/%m/%Y %H:%M:%S"), str(uuid.uuid4()), item_name, description, owner_id, "X"])
    
    def look_for_item(self, item_id):
        sheet_items = self.sheet.worksheet("items")
        data = sheet_items.get_all_values()
        for i, row in enumerate(data, start=2):
            if row[1] == item_id:
                return row
        return []
    
    def look_for_owner_items(self, owner_id):
        sheet_items = self.sheet.worksheet("items")
        data = sheet_items.get_all_values()
        ret = []        
        for i, row in enumerate(data, start=2):
            if row[4] == owner_id:
                ret.append(row)
        return ret

    def take_item(self, item_id):
        sheet_items = self.sheet.worksheet("items")
        data = sheet_items.get_all_values()
        for i, row in enumerate(data, start=2):
            if row[1] == item_id:
                sheet_items.update_cell(i, 6, "V")
                return 1
        return 0

# Example usage
# Create a .env file with GOOGLE_CREDENTIALS_FILE and GOOGLE_SHEET_URL
processor = GoogleSheetProcessor()
# print("ids:")

# print(processor.get_person_id("dsg", "3"))
# print(processor.get_person_id("tu", "5"))
# print(processor.get_person_id("tu", "6"))

# print("names:")
# print(processor.get_person_name("7786eea8-bc0d-47f7-84c3-f2ab422c9631"))
# print(processor.get_person_name("d3cf5ad5-3859-412f-b6fd-f119c819059d"))
# print(processor.get_person_name("d3cf5ad5-3859-412f-b6fd-f1191239059d"))

# print("inserts:")
# processor.insert_item("art","blue with flowers",processor.get_person_id("dsg", "3"))
# processor.insert_item("paint","blue with flowers",processor.get_person_id("tu", "5"))
# processor.insert_item("friend","blue with flowers",processor.get_person_id("tu", "5"))

# print("look item:")
# print(processor.look_for_item("016b249c-1a6c-4094-b94e-ce287392b534"))

# print("look owner items:")
# print(processor.look_for_owner_items(processor.get_person_id("tu", "5")))
# print(processor.look_for_owner_items(processor.get_person_id("dsg", "3")))


# print("take:")
processor.take_item("0aab2adb-ff9f-469c-814f-e9b90f09045e")
