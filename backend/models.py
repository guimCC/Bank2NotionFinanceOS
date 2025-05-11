from pydantic import BaseModel
from typing import Optional, List, Union, Dict, Any
from datetime import date

class AccountBase(BaseModel):
    id: Optional[str] = None
    name: str

class ExpenseTypeBase(BaseModel):
    id: Optional[str] = None
    name: str

class MonthBase(BaseModel):
    id: Optional[str] = None
    name: str

class IncomeTypeBase(BaseModel):
    id: Optional[str] = None
    name: str

class SubscriptionBase(BaseModel):
    id: Optional[str] = None
    name: str

class DebtBase(BaseModel):
    id: Optional[str] = None
    name: str

class SavingBase(BaseModel):
    id: Optional[str] = None
    name: str

class ExpenseCreate(BaseModel):
    name: str
    operation_date: str  # Format: "dd/mm/yyyy"
    concept: str
    amount: str  # Positive number as string
    account_id: Optional[str] = None
    expense_type_id: Optional[str] = None
    month_id: Optional[str] = None
    subscription_id: Optional[str] = None
    debt_id: Optional[str] = None
    split: Optional[bool] = False
    subs: Optional[bool] = False

class IncomeCreate(BaseModel):
    name: str
    operation_date: str  # Format: "dd/mm/yyyy"
    concept: str
    amount: str  # Positive number as string
    account_id: Optional[str] = None
    month_id: Optional[str] = None
    income_type_id: Optional[str] = None

class TransferCreate(BaseModel):
    name: str
    operation_date: str  # Format: "dd/mm/yyyy"
    amount: str
    from_account_id: Optional[str] = None
    from_saving_id: Optional[str] = None
    to_account_id: Optional[str] = None
    to_saving_id: Optional[str] = None
    transfer_type: Optional[str] = None  # Studies, Return, Moving, Saving, Funding, Other
    month_id: Optional[str] = None

class ResponseModel(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None
    
class TransactionEntry(BaseModel):
    """Model for a transaction entry from CSV processing"""
    type: str  # "expense", "income", or "transfer"
    date: str
    concept: str
    amount: str
    name: str
    
    # Common fields
    account_id: Optional[str] = None
    month_id: Optional[str] = None
    
    # For expenses
    expense_type_id: Optional[str] = None
    subscription_id: Optional[str] = None
    debt_id: Optional[str] = None
    split: Optional[bool] = False
    subs: Optional[bool] = False
    
    # For incomes
    income_type_id: Optional[str] = None
    
    # For transfers
    from_account_id: Optional[str] = None
    from_saving_id: Optional[str] = None
    to_account_id: Optional[str] = None
    to_saving_id: Optional[str] = None
    transfer_type: Optional[str] = None
    
    # CSV tracking
    csv_row_id: Optional[int] = None
    csv_filename: Optional[str] = None

class CSVStats(BaseModel):
    """Statistics of CSV processing"""
    total: int
    expenses: int
    incomes: int
    transfers: int
    unknown: int
    already_loaded: int

class CSVProcessResponse(BaseModel):
    """Response model for CSV processing endpoint"""
    status: str
    message: str
    entries: List[Dict[str, Any]]
    stats: CSVStats