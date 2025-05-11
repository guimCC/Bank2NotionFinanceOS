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


EXPENSES_DATABASE_ID = "1f0d083e-48b1-81ca-be97-ebd634742618"

headers = {
    "Authorization": f"Bearer {tokenNotion}",
    "Content-Type": "application/json",
    "Notion-Version": "2021-08-16"
}

def create_expense(operation_date, name, concept, amount, account_id=None, expense_type_id=None):
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
        properties["accounts"] = {
            "relation": [
                {
                    "id": account_id
                }
            ]
        }
    
    # Add expense type relation if provided
    if expense_type_id:
        properties["expense type"] = {
            "relation": [
                {
                    "id": expense_type_id
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

if __name__ == "__main__":
    # Read CSV file
    # with open("your_transactions.csv", "r") as file:
    #     reader = csv.DictReader(file)
    #     for row in reader:
    #         process_csv_row(row)
    
    # For testing, just create one expense
    test_result = create_expense(
        name="Test Expense",
        operation_date="01/05/2025",
        concept="Test expense from API",
        amount="-24.99"
    )
    print(json.dumps(test_result, indent=2))