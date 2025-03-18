import gspread
from oauth2client.service_account import ServiceAccountCredentials
import uuid
import os
from dotenv import load_dotenv
from datetime import datetime

TIME_FORMAT = "'%d/%m/%Y %H:%M:%S"

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
                time = row[0]
                row[0] = str(uuid.uuid4())  # Add unique ID
                row.append(time)
                processed_data.append(row)
                sheet_A.update_cell(i-1, 4, "V")
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
            return row[0]
        return ''

    def get_person_name(self, id):
        sheet_person = self.sheet.worksheet("registered")
        data = sheet_person.get_all_values()
        for row in data[1:]:
            if (row[0]!=id):
                continue
            return row[1],row[2]
        return "",""

    def add_item(self, item_name, owner_id, receipt_number,cell_id, description):
        sheet_items = self.sheet.worksheet("items")
        item_id = str(uuid.uuid4()) 
        time_added=datetime.now().strftime(TIME_FORMAT)
        self.cell_change_status(cell_id, True)
        sheet_items.append_row([item_id, item_name, owner_id, receipt_number, cell_id, description, time_added, "X"])
        return add_item

    def take_item(self, item_id):
        sheet_items = self.sheet.worksheet("items")
        data = sheet_items.get_all_values()
        for i, row in enumerate(data, start=2):
            if row[0] == item_id:
                sheet_items.update_cell(i-1, 8, "V")
                sheet_items.update_cell(i-1, 9, datetime.now().strftime(TIME_FORMAT))
                self.cell_change_status(row[4], False)
                return 1
        return 0

    def look_for_item(self, item_id):
        sheet_items = self.sheet.worksheet("items")
        data = sheet_items.get_all_values()
        for i, row in enumerate(data, start=2):
            if row[0] == item_id:
                return row
        return []
    
    def look_for_owner_items(self, owner_id):
        sheet_items = self.sheet.worksheet("items")
        data = sheet_items.get_all_values()
        ret = []        
        for i, row in enumerate(data, start=2):
            if row[2] == owner_id:
                ret.append(row)
        return ret

    def cell_change_status(self, cell_id, status):
        sheet_cells = self.sheet.worksheet("cells")
        data = sheet_cells.get_all_values()
        for i, row in enumerate(data, start=2):
            if row[0] == cell_id:
                sheet_cells.update_cell(i -1, 6, status)
                return 1
        return 0
    
    def find_cell_id(self, room, row, column, level):
        sheet_cells = self.sheet.worksheet("cells")
        data = sheet_cells.get_all_values()
        for _row in data[1:]:
            if (_row[1] == room \
               and _row[2] == row \
               and _row[3] == column \
               and _row[4] == level):
                return _row[0]
        return ""
    def find_cell_info(self, cell_id):
        sheet_cells = self.sheet.worksheet("cells")
        data = sheet_cells.get_all_values()
        for row in data[1:]:
            if row[0] == cell_id:
                return row
        return ""
    
    
    def print_stock(self):
        registered = self.sheet.worksheet("registered")
        items = self.sheet.worksheet("items")
        cells = self.sheet.worksheet("cells")

        print("registered")
        for row in registered.get_all_values():
            print("\t",row)
        
        print("items")
        for row in items.get_all_values():
            print("\t",row)
        
        print("cells")
        for row in cells.get_all_values():
            print("\t",row)
# Example usage
# Create a .env file with GOOGLE_CREDENTIALS_FILE and GOOGLE_SHEET_URL
processor = GoogleSheetProcessor()
# processor.print_stock()

# print("cell function check:")
# cell = "7"
# status = processor.find_cell_info(cell)[-1]=="TRUE"
# print(processor.find_cell_info(cell))
# processor.cell_change_status(cell,not status)
# print(processor.find_cell_info(cell))
# processor.cell_change_status(cell,status)
# print(processor.find_cell_info(cell))

# print(processor.find_cell_id( '1', '1', '1', '1'))
# print(processor.find_cell_id( '1', '1', '2', '1'))
# print(processor.find_cell_id( '2', '2', '3', '3'))

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
# processor.add_item("item_name", "d3cf5ad5-3859-412f-b6fd-f1191239059d", "0999","7", "something nice")
processor.take_item("e47846c3-b992-43a6-8efa-f4ceb08fcdec")
# print("look item:")
# print(processor.look_for_item("016b249c-1a6c-4094-b94e-ce287392b534"))
# print("look owner items:")
# print(processor.look_for_owner_items(processor.get_person_id("tu", "5")))
# print(processor.look_for_owner_items(processor.get_person_id("dsg", "3")))


# print("take:")
# processor.take_item("0aab2adb-ff9f-469c-814f-e9b90f09045e")

