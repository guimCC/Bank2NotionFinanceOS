from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Dict, Any, Optional
from models import (
    AccountBase, ExpenseTypeBase, MonthBase, IncomeTypeBase,
    SubscriptionBase, DebtBase, SavingBase, ExpenseCreate, 
    IncomeCreate, TransferCreate, ResponseModel, CSVProcessResponse, TransactionEntry
)
from utils.notionAPI import (
    # Account functions
    list_accounts,
    
    # Expense functions
    list_expense_types,
    create_expense,
    
    # Income functions
    list_income_types,
    create_income,
    
    # Month functions
    list_months,
    
    # Subscription functions
    list_subscriptions,
    
    # Debt functions
    list_debts,
    
    # Savings functions
    list_savings,
    
    # Transfer functions
    create_transfer
)

from utils.csv_processor import (
    process_csv, categorize_transaction, 
    get_month_from_date, update_csv_with_loaded_flag
)

router = APIRouter()

# Health check endpoint
@router.get("/", response_model=ResponseModel)
async def root():
    return ResponseModel(
        status="success",
        message="Financial Management API is running"
    )

# ==================== Account Routes ====================
@router.get("/accounts", response_model=List[AccountBase])
async def get_accounts():
    try:
        accounts = list_accounts()
        return accounts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Expense Routes ====================
@router.get("/expense-types", response_model=List[ExpenseTypeBase])
async def get_expense_types():
    try:
        expense_types = list_expense_types()
        return expense_types
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/expenses", response_model=ResponseModel)
async def add_expense(expense: ExpenseCreate):
    try:
        result = create_expense(
            operation_date=expense.operation_date,
            name=expense.name,
            concept=expense.concept,
            amount=expense.amount,
            account_id=expense.account_id,
            expense_type_id=expense.expense_type_id,
            month_id=expense.month_id,
            subscription_id=expense.subscription_id,
            debt_id=expense.debt_id
        )
        
        if "object" in result and result["object"] == "error":
            return ResponseModel(
                status="error",
                message=result.get("message", "Unknown error"),
                data=result
            )
            
        return ResponseModel(
            status="success",
            message="Expense created successfully",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Income Routes ====================
@router.get("/income-types", response_model=List[IncomeTypeBase])
async def get_income_types():
    try:
        income_types = list_income_types()
        return income_types
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/incomes", response_model=ResponseModel)
async def add_income(income: IncomeCreate):
    try:
        result = create_income(
            operation_date=income.operation_date,
            name=income.name,
            concept=income.concept,
            amount=income.amount,
            account_id=income.account_id,
            month_id=income.month_id,
            income_type_id=income.income_type_id
        )
        
        if "object" in result and result["object"] == "error":
            return ResponseModel(
                status="error",
                message=result.get("message", "Unknown error"),
                data=result
            )
            
        return ResponseModel(
            status="success",
            message="Income created successfully",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Month Routes ====================
@router.get("/months", response_model=List[MonthBase])
async def get_months():
    try:
        months = list_months()
        return months
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Subscription Routes ====================
@router.get("/subscriptions", response_model=List[SubscriptionBase])
async def get_subscriptions():
    try:
        subscriptions = list_subscriptions()
        return subscriptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Debt Routes ====================
@router.get("/debts", response_model=List[DebtBase])
async def get_debts():
    try:
        debts = list_debts()
        return debts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Savings Routes ====================
@router.get("/savings", response_model=List[SavingBase])
async def get_savings():
    try:
        savings = list_savings()
        return savings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Transfer Routes ====================
@router.post("/transfers", response_model=ResponseModel)
async def add_transfer(transfer: TransferCreate):
    try:
        result = create_transfer(
            operation_date=transfer.operation_date,
            amount=transfer.amount,
            from_account_id=transfer.from_account_id,
            from_saving_id=transfer.from_saving_id,
            to_account_id=transfer.to_account_id,
            to_saving_id=transfer.to_saving_id,
            transfer_type=transfer.transfer_type,
            month_id=transfer.month_id
        )
        
        if "object" in result and result["object"] == "error":
            return ResponseModel(
                status="error",
                message=result.get("message", "Unknown error"),
                data=result
            )
            
        return ResponseModel(
            status="success",
            message="Transfer created successfully",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== CSV Processing Routes ====================
@router.post("/process-csv", response_model=CSVProcessResponse)
async def process_csv_file(file: UploadFile = File(...)):
    """Process uploaded CSV file and return categorized transactions"""
    try:
        # Read the CSV file
        contents = await file.read()
        
        # Process the CSV contents
        processed_data = process_csv(contents)
        
        return CSVProcessResponse(
            status="success",
            message=f"Successfully processed {len(processed_data['entries'])} entries",
            entries=processed_data["entries"],
            stats=processed_data["stats"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")

@router.post("/save-transaction", response_model=ResponseModel)
async def save_transaction(transaction: TransactionEntry):
    """Save a single transaction to Notion based on its type"""
    try:
        result = None
        
        if transaction.type == "expense":
            result = create_expense(
                operation_date=transaction.date,
                name=transaction.name,
                concept=transaction.concept,
                amount=transaction.amount,
                account_id=transaction.account_id,
                expense_type_id=transaction.expense_type_id,
                month_id=transaction.month_id,
                subscription_id=transaction.subscription_id,
                debt_id=transaction.debt_id,
                split=transaction.split,
                subs=transaction.subs
            )
        elif transaction.type == "income":
            result = create_income(
                operation_date=transaction.date,
                name=transaction.name,
                concept=transaction.concept,
                amount=transaction.amount,
                account_id=transaction.account_id,
                month_id=transaction.month_id,
                income_type_id=transaction.income_type_id
            )
        elif transaction.type == "transfer":
            result = create_transfer(
                name=transaction.name,
                operation_date=transaction.date,
                amount=transaction.amount,
                from_account_id=transaction.from_account_id,
                from_saving_id=transaction.from_saving_id,
                to_account_id=transaction.to_account_id,
                to_saving_id=transaction.to_saving_id,
                transfer_type=transaction.transfer_type,
                month_id=transaction.month_id
            )
        else:
            return ResponseModel(
                status="error",
                message=f"Unknown transaction type: {transaction.type}"
            )
        
        if "object" in result and result["object"] == "error":
            return ResponseModel(
                status="error",
                message=result.get("message", "Unknown error"),
                data=result
            )
            
        # Mark as processed in the CSV file
        if transaction.csv_row_id is not None:
            update_csv_with_loaded_flag(transaction.csv_filename, transaction.csv_row_id)
            
        return ResponseModel(
            status="success",
            message=f"{transaction.type.capitalize()} created successfully",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mark-csv-loaded", response_model=ResponseModel)
async def mark_csv_loaded(
    filename: str = Form(...), 
    row_id: int = Form(...),
    date: str = Form(...), 
    concept: str = Form(...), 
    amount: str = Form(...)
):
    """Mark a specific row in a CSV file as loaded"""
    try:
        success = update_csv_with_loaded_flag(filename, row_id, date, concept, amount)
        if success:
            return ResponseModel(
                status="success",
                message="Transaction marked as loaded in CSV"
            )
        else:
            return ResponseModel(
                status="error",
                message="Failed to mark transaction as loaded"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))