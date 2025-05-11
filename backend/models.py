# models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class ResponseModel(BaseModel):
    status: str
    message: str
    data: Optional[Any] = None

class BaseItem(BaseModel):
    id: str
    name: str

class AccountBase(BaseItem): pass
class ExpenseTypeBase(BaseItem): pass
class MonthBase(BaseItem): pass
class IncomeTypeBase(BaseItem): pass
class SubscriptionBase(BaseItem): pass
class DebtBase(BaseItem): pass
class SavingBase(BaseItem): pass

# For creating entries - These are sent TO Notion
class ExpenseCreatePayload(BaseModel): # Renamed to avoid conflict
    date: str
    name: str
    concept: Optional[str] = ""
    amount: float
    account_id: Optional[str] = None
    expense_type_id: Optional[str] = None
    month_id: Optional[str] = None
    subscription_id: Optional[str] = None
    debt_id: Optional[str] = None
    split: bool = False
    subs: bool = False

class IncomeCreatePayload(BaseModel):
    date: str
    name: str
    concept: Optional[str] = ""
    amount: float
    account_id: Optional[str] = None
    month_id: Optional[str] = None
    income_type_id: Optional[str] = None

class TransferCreatePayload(BaseModel):
    date: str
    name: str
    amount: float
    from_account_id: Optional[str] = None
    from_saving_id: Optional[str] = None
    to_account_id: Optional[str] = None
    to_saving_id: Optional[str] = None
    transfer_type: Optional[str] = None
    month_id: Optional[str] = None


# Model for an entry processed from CSV, used by frontend
# This is what the backend /process-csv returns and what /save-transaction receives
class TransactionEntry(BaseModel):
    type: str  # 'expense', 'income', 'transfer'
    date: str #= Field(..., alias="operation_date")
    amount: str # Kept as string from CSV, converted to float for Notion payload
    concept: Optional[str] = ""
    month_id: Optional[str] = None
    account_id: Optional[str] = None
    name: str

    # For frontend to map back to its in-memory CSV data
    original_csv_filename: str # Filename as uploaded by the user
    csv_row_index: int         # 0-based index of the data row in the original CSV

    # Expense specific
    expense_type_id: Optional[str] = None
    subscription_id: Optional[str] = None
    debt_id: Optional[str] = None
    split: bool = False
    subs: bool = False

    # Income specific
    income_type_id: Optional[str] = None

    # Transfer specific
    from_account_id: Optional[str] = None
    from_saving_id: Optional[str] = None
    to_account_id: Optional[str] = None
    to_saving_id: Optional[str] = None
    transfer_type: Optional[str] = None

    class Config:
        populate_by_name = True


class CSVProcessStats(BaseModel):
    total_rows_in_csv: int
    processed_for_review: int
    already_loaded_in_csv: int
    expenses_found: int
    incomes_found: int
    transfers_found: int
    unknown_type: int

class CSVProcessResponse(BaseModel):
    status: str
    message: str
    entries: List[TransactionEntry]
    stats: CSVProcessStats