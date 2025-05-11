import requests
from datetime import datetime
import csv
import os

# Load Notion token from file
try:
    with open("../api_token.txt", "r") as token_file:
        tokenNotion = token_file.read().strip()
except FileNotFoundError:
    print("Error: api_token.txt file not found")
    exit(1)


# Define a function to load database IDs from CSV
def load_database_ids(file_path):
    database_ids = {}
    try:
        with open(file_path, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                database_ids[f"{row['database_name']}_DATABASE_ID"] = row['database_id']
        return database_ids
    except FileNotFoundError:
        print(f"Error: {file_path} file not found")
        exit(1)
    except Exception as e:
        print(f"Error loading database IDs: {e}")
        exit(1)

# Load database IDs from CSV file
csv_path = "../database_ids.csv"
db_ids = load_database_ids(csv_path)

# Set variables for each database ID
EXPENSES_DATABASE_ID = db_ids.get("EXPENSES_DATABASE_ID")
ACCOUNTS_DATABASE_ID = db_ids.get("ACCOUNTS_DATABASE_ID")
EXPENSE_TYPES_DATABASE_ID = db_ids.get("EXPENSE_TYPES_DATABASE_ID")
MONTHS_DATABASE_ID = db_ids.get("MONTHS_DATABASE_ID")
INCOMES_DATABASE_ID = db_ids.get("INCOMES_DATABASE_ID")
INCOME_TARGET_DATABASE_ID = db_ids.get("INCOME_TARGET_DATABASE_ID")
DEBTS_DATABASE_ID = db_ids.get("DEBTS_DATABASE_ID")
SUBSCRIPTIONS_DATABASE_ID = db_ids.get("SUBSCRIPTIONS_DATABASE_ID")
TRANSFER_DATABASE_ID = db_ids.get("TRANSFER_DATABASE_ID")
SAVINGS_DATABASE_ID = db_ids.get("SAVINGS_DATABASE_ID")

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

######################### MONTHS ########################
def get_months():
    """Retrieve all months from the database"""
    url = f"https://api.notion.com/v1/databases/{MONTHS_DATABASE_ID}/query"
    payload = {"page_size": 100}
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def list_months():
    """List all available months with their IDs"""
    months_data = get_months()
    
    if "results" not in months_data:
        print("Error retrieving months:", months_data.get("message", ""))
        return []
    
    months = []
    for month in months_data["results"]:
        # Find the title property (adjust based on your database structure)
        title_property = "Month"
        
        if title_property and month["properties"][title_property]["title"]:
            month_name = month["properties"][title_property]["title"][0]["text"]["content"]
            month_id = month["id"]
            months.append({"id": month_id, "name": month_name})
    
    return months

######################### INCOME TYPES ########################
def get_income_types():
    """Retrieve all income types from the database"""
    url = f"https://api.notion.com/v1/databases/{INCOME_TARGET_DATABASE_ID}/query"
    
    payload = {
        "page_size": 100  # Adjust if you have more income types
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def list_income_types():
    """List all available income types with their IDs"""
    income_types_data = get_income_types()
    
    if "results" not in income_types_data:
        print("Error retrieving income types:", income_types_data.get("message", ""))
        return []
    
    income_types = []
    for income_type in income_types_data["results"]:
        title_property = "Income Type"
        
        if title_property and income_type["properties"][title_property]["title"]:
            type_name = income_type["properties"][title_property]["title"][0]["text"]["content"]
            type_id = income_type["id"]
            income_types.append({"id": type_id, "name": type_name})
    
    return income_types

######################### SUBSCRIPTIONS ########################
def get_subscriptions():
    """Retrieve all subscriptions from the database"""
    url = f"https://api.notion.com/v1/databases/{SUBSCRIPTIONS_DATABASE_ID}/query"
    
    payload = {
        "page_size": 100
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def list_subscriptions():
    """List all available subscriptions with their IDs"""
    subscriptions_data = get_subscriptions()
    
    if "results" not in subscriptions_data:
        print("Error retrieving subscriptions:", subscriptions_data.get("message", ""))
        return []
    
    subscriptions = []
    for subscription in subscriptions_data["results"]:
        title_property = "Name"
        
        if title_property and subscription["properties"][title_property]["title"]:
            sub_name = subscription["properties"][title_property]["title"][0]["text"]["content"]
            sub_id = subscription["id"]
            subscriptions.append({"id": sub_id, "name": sub_name})
    
    return subscriptions

######################### DEBTS ########################
def get_debts():
    """Retrieve all debts from the database"""
    url = f"https://api.notion.com/v1/databases/{DEBTS_DATABASE_ID}/query"
    
    payload = {
        "page_size": 100
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def list_debts():
    """List all available debts with their IDs"""
    debts_data = get_debts()
    
    if "results" not in debts_data:
        print("Error retrieving debts:", debts_data.get("message", ""))
        return []
    
    debts = []
    for debt in debts_data["results"]:
        title_property = "Debt"
        
        if title_property and debt["properties"][title_property]["title"]:
            debt_name = debt["properties"][title_property]["title"][0]["text"]["content"]
            debt_id = debt["id"]
            debts.append({"id": debt_id, "name": debt_name})
    
    return debts

######################### SAVINGS ########################
def get_savings():
    """Retrieve all savings accounts from the database"""
    url = f"https://api.notion.com/v1/databases/{SAVINGS_DATABASE_ID}/query"
    
    payload = {
        "page_size": 100
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def list_savings():
    """List all available savings with their IDs"""
    savings_data = get_savings()
    
    if "results" not in savings_data:
        print("Error retrieving savings:", savings_data.get("message", ""))
        return []
    
    savings = []
    for saving in savings_data["results"]:
        title_property = "Name"  # Adjust based on your actual title property
        
        if title_property and saving["properties"][title_property]["title"]:
            saving_name = saving["properties"][title_property]["title"][0]["text"]["content"]
            saving_id = saving["id"]
            savings.append({"id": saving_id, "name": saving_name})
    
    return savings

######################## EXPENSES ########################

def create_expense(operation_date, name, concept, amount, account_id=None, expense_type_id=None, month_id=None, subscription_id=None, debt_id=None, split=False, subs=False):
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
            "checkbox": split
        },
        "Subs": {
            "checkbox": subs
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
        properties["Expenses Type"] = {  # Make sure this matches exactly from your schema
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
    
    # Add subscription relation if provided
    if subscription_id:
        properties["Subscription"] = {  # Make sure this matches exactly from your schema
            "relation": [
                {
                    "id": subscription_id
                }
            ]
        }
    
    # Add debt relation if provided
    if debt_id:
        properties["Debts"] = {  # Make sure this matches exactly from your schema
            "relation": [
                {
                    "id": debt_id
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

######################## INCOMES ########################

def create_income(operation_date, name, concept, amount, account_id=None, month_id=None, income_type_id=None):
    """Create a new income entry in Notion Incomes database"""
    
    # Format the date properly for Notion
    iso_date = datetime.strptime(operation_date, "%d/%m/%Y").strftime("%Y-%m-%d")
    
    # Build the properties object
    properties = {
        "Income Name": {
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
        }
    }
    
    if account_id:
        properties["Account"] = {
            "relation": [
                {
                    "id": account_id
                }
            ]
        }
    
    if income_type_id:
        properties["Incomes Type"] = {
            "relation": [
                {
                    "id": income_type_id
                }
            ]
        }
    
    if month_id:
        properties["Months"] = {
            "relation": [
                {
                    "id": month_id
                }
            ]
        }
    
    # Prepare the payload
    payload = {
        "parent": {"database_id": INCOMES_DATABASE_ID},
        "properties": properties,
        "icon": {
            "type": "external",
            "external": {
                "url": "https://www.notion.so/icons/arrow-down_green.svg"
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

######################### TRANSFERS ########################
def create_transfer(
    name,
    operation_date, 
    amount, 
    from_account_id=None, 
    from_saving_id=None, 
    to_account_id=None, 
    to_saving_id=None,
    transfer_type=None,
    month_id=None
):
    """Create a new transfer entry in Notion Transfer database"""
    
    # Format the date properly for Notion
    iso_date = datetime.strptime(operation_date, "%d/%m/%Y").strftime("%Y-%m-%d")
    
    # Build the properties object
    properties = {
        "Transfer": {
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
        "Amount": {
            "number": float(amount)
        }
    }
    
    # Add from account relation if provided
    if from_account_id:
        properties["From Acc"] = {
            "relation": [
                {
                    "id": from_account_id
                }
            ]
        }
    
    # Add from saving relation if provided
    if from_saving_id:
        properties["From Sav"] = {
            "relation": [
                {
                    "id": from_saving_id
                }
            ]
        }
    
    # Add to account relation if provided
    if to_account_id:
        properties["To Acc"] = {
            "relation": [
                {
                    "id": to_account_id
                }
            ]
        }
    
    # Add to saving relation if provided
    if to_saving_id:
        properties["To Sav"] = {
            "relation": [
                {
                    "id": to_saving_id
                }
            ]
        }
    
    # Add transfer type selection if provided
    if transfer_type:
        properties["Transfer Type"] = {
            "select": {
                "name": transfer_type # Studies, Return, Moving, Saving, Funding, Other
            }
        }
    
    # Add month relation if provided
    if month_id:
        properties["Month"] = {
            "relation": [
                {
                    "id": month_id
                }
            ]
        }
    
    # Prepare the payload
    payload = {
        "parent": {"database_id": TRANSFER_DATABASE_ID},
        "properties": properties,
        "icon": {
            "type": "external",
            "external": {
                "url": "https://www.notion.so/icons/arrow-right_blue.svg"
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
    import json
    # Read CSV file
    # with open("your_transactions.csv", "r") as file:
    #     reader = csv.DictReader(file)
    #     for row in reader:
    #         process_csv_row(row)
    
    # For testing, just create one expense
    # get_database_schema(INCOMES_DATABASE_ID)
    
    print("Available accounts:")
    accounts = list_accounts()
    for account in accounts:
        print(f"- {account['name']} (ID: {account['id']})")
        
    # print("\nAvailable expense types:")
    # expense_types = list_expense_types()
    # for expense_type in expense_types:
    #     print(f"- {expense_type['name']} (ID: {expense_type['id']})")
        
    print("\nAvailable months:")
    months = list_months()
    for month in months:
        print(f"- {month['name']} (ID: {month['id']})")
    
    # print("\nAvailable income types:")
    # income_types = list_income_types()
    # for i, income_type in enumerate(income_types):
    #     print(f"{i+1}. {income_type['name']}")
    
    # print("\nAvailable subscriptions:")
    # subscriptions = list_subscriptions()
    # for i, sub in enumerate(subscriptions):
    #     print(f"{i+1}. {sub['name']}")
    
    # print("\nAvailable debts:")
    # debts = list_debts()
    # for i, debt in enumerate(debts):
    #     print(f"{i+1}. {debt['name']}")
    
    print("\nAvailable savings:")
    savings = list_savings()
    for i, saving in enumerate(savings):
        print(f"{i+1}. {saving['name']}")
    
    # test_result = create_expense(
    #     name="Test Expense",
    #     operation_date="01/05/2025",
    #     concept="Test expense from API",
    #     amount="24.99",
    #     account_id=accounts[0]["id"],
    #     expense_type_id=expense_types[0]["id"],
    #     month_id=months[0]["id"], 
    #     subscription_id=subscriptions[0]["id"],
    #     debt_id=debts[0]["id"]
    # )
    # print(json.dumps(test_result, indent=2))
    
    # test_result = create_income(
    #     name="Test Income",
    #     operation_date="01/05/2025",
    #     concept="Test income from API",
    #     amount="1500.00",
    #     account_id=accounts[0]["id"],
    #     month_id=months[0]["id"],
    #     income_type_id=income_types[0]["id"]
    # )
    # print(json.dumps(test_result, indent=2))
    
    test_result = create_transfer(
        operation_date="01/05/2025",
        name="Test Transfer",
        amount="100.00",
        to_account_id=accounts[0]["id"],
        from_saving_id=savings[0]["id"],
        
        transfer_type="Other",
        month_id=months[0]["id"]
    )
    print(json.dumps(test_result, indent=2))