import requests
import json
from datetime import datetime

# Load Notion token from file
try:
    with open("api_token.txt", "r") as token_file:
        tokenNotion = token_file.read().strip()
except FileNotFoundError:
    print("Error: api_token.txt file not found")
    exit(1)


EXPENSES_DATABASE_ID        = "1f0d083e-48b1-81ca-be97-ebd634742618"
ACCOUNTS_DATABASE_ID        = "1f0d083e-48b1-81c7-988c-d15cea95fe6d"
EXPENSE_TYPES_DATABASE_ID   = "1f0d083e-48b1-817e-a433-e071435d6c50"
MONTHS_DATABASE_ID          = "1f0d083e-48b1-8169-9d7b-fb8025113fe6"

headers = {
    "Authorization": f"Bearer {tokenNotion}",
    "Content-Type": "application/json",
    "Notion-Version": "2021-08-16"
}

######################## ACCOUNTS ########################

def get_accounts():
    """Retrieve all accounts from the Accounts database"""
    url = f"https://api.notion.com/v1/databases/{ACCOUNTS_DATABASE_ID}/query"
    
    payload = {
        "page_size": 10
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def list_accounts():
    """List all available accounts with their IDs"""
    accounts_data = get_accounts()
    
    if "results" not in accounts_data:
        print("Error retrieving accounts:", accounts_data.get("message", ""))
        return []
    
    accounts = []
    for account in accounts_data["results"]:
        title_property = "Account Name"
        
        if title_property and account["properties"][title_property]["title"]:
            account_name = account["properties"][title_property]["title"][0]["text"]["content"]
            account_id = account["id"]
            accounts.append({"id": account_id, "name": account_name})
    
    return accounts

######################### EXPENSE TYPES ########################
def get_expense_types():
    """Retrieve all expense types from the database"""
    url = f"https://api.notion.com/v1/databases/{EXPENSE_TYPES_DATABASE_ID}/query"
    
    payload = {
        "page_size": 100  # Adjust if you have more expense types
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def list_expense_types():
    """List all available expense types with their IDs"""
    expense_types_data = get_expense_types()
    
    if "results" not in expense_types_data:
        print("Error retrieving expense types:", expense_types_data.get("message", ""))
        return []
    
    expense_types = []
    for expense_type in expense_types_data["results"]:
        # Find the title property (adjust based on your database structure)
        title_property = "Expense Type"
        
        if title_property and expense_type["properties"][title_property]["title"]:
            type_name = expense_type["properties"][title_property]["title"][0]["text"]["content"]
            type_id = expense_type["id"]
            expense_types.append({"id": type_id, "name": type_name})
    
    return expense_types

######################## EXPENSES ########################

def create_expense(operation_date, name, concept, amount, account_id=None, expense_type_id=None, month_id=None):
    """Create a new expense entry in Notion Expenses database"""
    
    # Format the date properly for Notion
    iso_date = datetime.strptime(operation_date, "%d/%m/%Y").strftime("%Y-%m-%d")
    
    # Build the properties object
    properties = {
        "Expense Name":{
            "title": [
                {
                    "text": {
                        "content": name
                    }
                }
            ]
        },
        "Date": {
            "date": {
                "start": iso_date
            }
        },
        "Note": {
            "rich_text": [
                {
                    "text": {
                        "content": concept
                    }
                }
            ]
        },
        "Amount": {
            "number": float(amount)
        },
        "Split": {
            "checkbox": False
        },
        "Subs": {
            "checkbox": False
        }
    }
    
    # Add account relation if provided
    if account_id:
        properties["Accounts"] = {
            "relation": [
                {
                    "id": account_id
                }
            ]
        }
    
    # Add expense type relation if provided
    if expense_type_id:
        properties["Expense Type"] = {  # Make sure this matches exactly from your schema
            "relation": [
                {
                    "id": expense_type_id
                }
            ]
        }
    
    # Add month relation if provided
    if month_id:
        properties["Month"] = {  # Make sure this matches exactly from your schema
            "relation": [
                {
                    "id": month_id
                }
            ]
        }
    
    # Prepare the payload
    payload = {
        "parent": {"database_id": EXPENSES_DATABASE_ID},
        "properties": properties,
        "icon": {
            "type": "external",
            "external": {
                "url": "https://www.notion.so/icons/arrow-up_red.svg"
            }
        }
    }
    
    # Send the request to create the page
    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        json=payload
    )
    
    return response.json()

def get_database_schema(database_id):
    """Get the schema of a database to see exact property names"""
    url = f"https://api.notion.com/v1/databases/{database_id}"
    response = requests.get(url, headers=headers)
    data = response.json()
    
    if "properties" in data:
        print("\nAvailable properties:")
        for prop_name, prop_data in data["properties"].items():
            prop_type = prop_data["type"]
            print(f"- {prop_name} ({prop_type})")
    else:
        print("Error retrieving database schema:", data.get("message", ""))
    
    return data

if __name__ == "__main__":
    # Read CSV file
    # with open("your_transactions.csv", "r") as file:
    #     reader = csv.DictReader(file)
    #     for row in reader:
    #         process_csv_row(row)
    
    # For testing, just create one expense
    
    print("Available accounts:")
    accounts = list_accounts()
    for account in accounts:
        print(f"- {account['name']} (ID: {account['id']})")
        
    print("\nAvailable expense types:")
    expense_types = list_expense_types()
    for expense_type in expense_types:
        print(f"- {expense_type['name']} (ID: {expense_type['id']})")
    
    test_result = create_expense(
        name="Test Expense",
        operation_date="01/05/2025",
        concept="Test expense from API",
        amount="-24.99",
        account_id=accounts[0]["id"],  # Use the first account for testing
        expense_type_id=expense_types[0]["id"],  # Use the first expense type for testing
    )
    print(json.dumps(test_result, indent=2))