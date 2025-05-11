import csv
import io
import re
from datetime import datetime
import calendar
from typing import Dict, List, Any, Tuple, Optional
import os

# Import functions to get Notion entities
from .notionAPI import (
    list_accounts, list_expense_types, list_months, 
    list_income_types, list_subscriptions, list_debts
)

# Configuration for categorization rules
EXPENSE_KEYWORDS = {
    'rally': 'Gasofa',
    'trenes': 'Transportation',
    'condis': 'Groceries',
    'moneynet': 'Coffee',
    'frankfurt': 'Restaurant',
    'jimman': 'Party',
    'aramark': 'Coffee',
    'bar': 'Restaurant',
    'saf': 'Health - Gym - Beauty'
}

INCOME_KEYWORDS = {
    'nomina': 'Salary',
    'traspas': 'Transfer',
}

DEFAULT_EXPENSE_TYPE = None  # Will be set dynamically
DEFAULT_INCOME_TYPE = None   # Will be set dynamically
DEFAULT_ACCOUNT = None       # Will be set dynamically

def init_defaults():
    """Initialize default values from Notion data"""
    global DEFAULT_EXPENSE_TYPE, DEFAULT_INCOME_TYPE, DEFAULT_ACCOUNT
    
    # Get accounts
    accounts = list_accounts()
    # Set default account to Caixa Enginyers if exists, otherwise first account
    DEFAULT_ACCOUNT = next((acc for acc in accounts if acc["name"] == "Caixa Enginyers"), 
                           accounts[0] if accounts else None)
    
    # Get expense types
    expense_types = list_expense_types()
    DEFAULT_EXPENSE_TYPE = expense_types[0] if expense_types else None
    
    # Get income types
    income_types = list_income_types()
    DEFAULT_INCOME_TYPE = income_types[0] if income_types else None

def process_csv(contents: bytes) -> Dict:
    """Process CSV file contents and return categorized transactions"""
    # Initialize defaults if needed
    if DEFAULT_ACCOUNT is None:
        init_defaults()
    
    # Parse CSV
    csv_text = contents.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(csv_text))
    
    # Get all required data from Notion for categorization
    accounts = list_accounts()
    expense_types = list_expense_types()
    income_types = list_income_types()
    months = list_months()
    subscriptions = list_subscriptions()
    debts = list_debts()

    
    processed_entries = []
    stats = {
        "total": 0,
        "expenses": 0,
        "incomes": 0,
        "transfers": 0,
        "unknown": 0,
        "already_loaded": 0
    }
    
    for i, row in enumerate(csv_reader):
        stats["total"] += 1
        
        # Skip already loaded entries
        if row.get('LOADED') == 'true' or row.get('LOADED') == '1':
            stats["already_loaded"] += 1
            continue
        
        # Process the entry
        entry = categorize_transaction(row, i, accounts, expense_types, income_types, months, subscriptions, debts)
        if entry:
            processed_entries.append(entry)
            stats[entry.get("type", "unknown")] += 1
        else:
            stats["unknown"] += 1

    # Sort entries by date (oldest first)
    processed_entries.sort(key=lambda x: datetime.strptime(x["date"], "%d/%m/%Y"))
    
    return {
        "entries": processed_entries,
        "stats": stats
    }

def categorize_transaction(
    row: Dict[str, str], 
    row_id: int,
    accounts: List[Dict[str, str]],
    expense_types: List[Dict[str, str]],
    income_types: List[Dict[str, str]],
    months: List[Dict[str, str]],
    subscriptions: List[Dict[str, str]],
    debts: List[Dict[str, str]]
) -> Optional[Dict[str, Any]]:
    """Categorize a transaction row based on its content"""
    if not all(key in row for key in ['DATE', 'CONCEPT', 'IMPORT']):
        return None
    
    date = row['DATE']
    concept = row['CONCEPT']
    amount_str = row['IMPORT'].replace(',', '.')  # Ensure proper decimal format
    
    try:
        amount = float(amount_str)
    except ValueError:
        return None
    
    # Get month id from date
    month_id = get_month_from_date(date, months)
    
    # Find default account (Caixa Enginyers)
    default_account = next((acc for acc in accounts if acc["name"] == "Caixa Enginyers"), 
                          accounts[0] if accounts else None)
    
    default_account_id = default_account["id"] if default_account else None
    
    # Base transaction entry
    transaction = {
        "csv_row_id": row_id,
        "csv_filename": "transactions.csv",  # Default name, can be overridden
        "date": date,
        "concept": concept,
        "amount": str(abs(amount)),  # Store as absolute value string
        "account_id": default_account_id,
        "month_id": month_id
    }
    
    # DETERMINE TRANSACTION TYPE AND DETAILS
    
    # 1. Check for expense patterns
    if (concept.startswith("TARGETA") and amount < 0) or (concept.startswith("BIZUM A") and amount < 0) or (concept.startswith("R") and amount < 0):
        # It's an expense
        expense_type_id = find_expense_type(concept, expense_types)
        
        # Extract name from TARGETA concept
        name = ""
        if concept.startswith("TARGETA"):
            # Example: "TARGETA *1234 ... RESTAURANT NAME"
            match = re.search(r'TARGETA \*\d+ (.*)', concept)
            if match:
                name = match.group(1)
        elif concept.startswith("BIZUM A"):
            # Example: "BIZUM A: PERSON NAME"
            match = re.search(r'BIZUM A: (.*)', concept)
            if match:
                name = match.group(1)
        
        # If no name extracted, use concept
        if not name:
            name = concept
            
        return {
            **transaction,
            "type": "expense",
            "name": name,
            "expense_type_id": expense_type_id,
            "subscription_id": None,
            "debt_id": None,
            "split": False,
            "subs": False
        }
        
    # 2. Check for income patterns  
    elif (concept.startswith("TRASPAS") or concept.startswith("NOMINA")) and amount > 0:
        # It's an income
        income_type_id = find_income_type(concept, income_types)
        
        return {
            **transaction,
            "type": "income",
            "name": concept,
            "income_type_id": income_type_id
        }
        
    # 3. Check for transfer patterns
    elif concept.startswith("BIZUM DE") and amount > 0 or concept.startswith("INGRES") and amount > 0:
        # It's a transfer (return)
        name = ""
        # Example: "BIZUM DE: PERSON NAME"
        match = re.search(r'BIZUM DE: (.*)', concept)
        if match:
            name = match.group(1)
        
        return {
            **transaction,
            "type": "transfer",
            "name": name if name else concept,
            "from_account_id": None,
            "from_saving_id": None,
            "to_account_id": default_account_id,
            "to_saving_id": None,
            "transfer_type": "Return"
        }
    
    # 4. Default case: unidentified transaction
    # Base decision on amount sign
    if amount < 0:
        # Negative amount, likely an expense
        return {
            **transaction,
            "type": "expense",
            "name": concept,
            "expense_type_id": None,
            "subscription_id": None,
            "debt_id": None,
            "split": False,
            "subs": False
        }
    else:
        # Positive amount, likely an income
        return {
            **transaction,
            "type": "income",
            "name": concept,
            "income_type_id": None
        }

def find_expense_type(concept: str, expense_types: List[Dict[str, str]]) -> Optional[str]:
    """Find appropriate expense type based on concept text"""
    concept_lower = concept.lower()
    
    # Check against keywords
    for keyword, category in EXPENSE_KEYWORDS.items():
        if keyword in concept_lower:
            # Find expense type ID matching this category
            matching_type = next((et for et in expense_types if et["name"].lower() == category.lower()), None)
            if matching_type:
                return matching_type["id"]
    
    # Default to None if no match
    return None

def find_income_type(concept: str, income_types: List[Dict[str, str]]) -> Optional[str]:
    """Find appropriate income type based on concept text"""
    concept_lower = concept.lower()
    
    # Check against keywords
    for keyword, category in INCOME_KEYWORDS.items():
        if keyword in concept_lower:
            # Find income type ID matching this category
            matching_type = next((it for it in income_types if it["name"].lower() == category.lower()), None)
            if matching_type:
                return matching_type["id"]
    
    # Default to None if no match
    return None

def get_month_from_date(date_str: str, months: List[Dict[str, str]]) -> Optional[str]:
    """Extract month from date string and find its ID"""
    try:
        # Assuming date_str is in format dd/mm/yyyy
        dt = datetime.strptime(date_str, "%d/%m/%Y")
        month_name = dt.strftime("%B")  # Full month name
        year = dt.strftime("%Y")
        
        # Format to match your month names pattern (e.g., "May 2025")
        formatted_month = f"{month_name} {year}"
        
        # Find matching month ID
        matching_month = next((m for m in months if m["name"] == formatted_month), None)
        if matching_month:
            return matching_month["id"]
        
        # Try just the month name
        matching_month = next((m for m in months if m["name"] == month_name), None)
        return matching_month["id"] if matching_month else None
        
    except Exception:
        return None

def update_csv_with_loaded_flag(filename: str, row_id: int, date: str = None, concept: str = None, amount: str = None) -> bool:
    """Update CSV file to mark a row as loaded"""
    try:
        # Assuming the CSV is in a specified directory
        csv_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
        os.makedirs(csv_dir, exist_ok=True)
        
        filepath = os.path.join(csv_dir, filename)
        
        # If file doesn't exist yet, it's a new CSV
        if not os.path.exists(filepath):
            return True
            
        # Read the existing CSV
        rows = []
        with open(filepath, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames
            
            # Ensure LOADED is in fieldnames
            if 'LOADED' not in fieldnames:
                fieldnames.append('LOADED')
                
            # Read all rows
            for i, row in enumerate(reader):
                if i == row_id:
                    # This is our target row to mark as loaded
                    # Double-check it's the right row if identifiers were provided
                    if (date is None or row.get('DATE') == date) and \
                       (concept is None or row.get('CONCEPT') == concept) and \
                       (amount is None or row.get('IMPORT') == amount):
                        row['LOADED'] = 'true'
                rows.append(row)
        
        # Write back the updated CSV
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            
        return True
    except Exception as e:
        print(f"Error updating CSV: {e}")
        return False