from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional, Any # Dict might not be needed directly in signatures now

# Import models from your models.py file
from models import (
    # Base types for GET requests (listing options)
    AccountBase,
    ExpenseTypeBase,
    MonthBase,
    IncomeTypeBase,
    SubscriptionBase,
    DebtBase,
    SavingBase,

    # Payloads for CREATING entries in Notion (used within /save-transaction)
    ExpenseCreatePayload,
    IncomeCreatePayload,
    TransferCreatePayload, # Note: If your create_transfer function in notionAPI expects fields matching this, this is correct.

    # General API response structure
    ResponseModel,

    # For CSV processing
    CSVProcessResponse, # This is the response from /process-csv
    TransactionEntry    # This is the model for an individual entry that /process-csv returns in a list,
                        # and also what /save-transaction will receive from the frontend.
)

# Your notionAPI functions (ensure these are correctly imported)
from utils.notionAPI import (
    list_accounts,
    list_expense_types,
    create_expense, # Takes parameters matching ExpenseCreatePayload
    list_income_types,
    create_income,  # Takes parameters matching IncomeCreatePayload
    list_months,
    list_subscriptions,
    list_debts,
    list_savings,
    create_transfer # Takes parameters matching TransferCreatePayload
)

# Your CSV processing functions
from utils.csv_processor import (
    process_csv # Takes CSV content bytes and original filename
    # categorize_transaction is used internally by process_csv
    # get_month_from_date is used internally
    # update_csv_with_loaded_flag is REMOVED
)

router = APIRouter()

# Health check endpoint
@router.get("/", response_model=ResponseModel)
async def root():
    return ResponseModel(
        status="success",
        message="Financial Management API is running"
    )

# ==================== Listing Routes (GET) ====================
@router.get("/accounts", response_model=List[AccountBase])
async def get_accounts_route(): # Renamed to avoid conflict if you had a function named get_accounts
    try:
        return list_accounts()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/expense-types", response_model=List[ExpenseTypeBase])
async def get_expense_types_route():
    try:
        return list_expense_types()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/income-types", response_model=List[IncomeTypeBase])
async def get_income_types_route():
    try:
        return list_income_types()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/months", response_model=List[MonthBase])
async def get_months_route():
    try:
        return list_months()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subscriptions", response_model=List[SubscriptionBase])
async def get_subscriptions_route():
    try:
        return list_subscriptions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debts", response_model=List[DebtBase])
async def get_debts_route():
    try:
        return list_debts()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/savings", response_model=List[SavingBase])
async def get_savings_route():
    try:
        return list_savings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CSV Processing Route ====================
@router.post("/process-csv", response_model=CSVProcessResponse)
async def process_csv_file_route(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        # The process_csv function in csv_processor.py should now take 'contents' and 'file.filename'
        # and return a dictionary matching CSVProcessResponse structure.
        processed_data_dict = process_csv(contents, file.filename)

        # Validate and return (Pydantic handles validation here if types match)
        return CSVProcessResponse(**processed_data_dict)
    except ValueError as ve: # Catch specific errors like missing CSV headers
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error processing CSV: {type(e).__name__} - {str(e)}") # For debugging
        # traceback.print_exc() # More detailed traceback for server logs
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")


# ==================== Save Transaction Route ====================
@router.post("/save-transaction", response_model=ResponseModel)
async def save_transaction_route(transaction: TransactionEntry):
    """
    Receives a processed transaction entry from the frontend (which originated from the CSV)
    and saves it to the appropriate Notion database.
    """
    print("aaaaaaaaaaaaaaaaaaa")
    print("Received transaction for saving:", transaction.dict()) # For debugging
    try:
        result = None
        notion_response_data = None # To store the actual Notion response
        print("Saving transaction:", transaction) # For debugging
        if transaction.type == "expense":
            # Prepare payload for create_expense
            payload = ExpenseCreatePayload(
                date=transaction.date,
                name=transaction.name,
                concept=transaction.concept,
                amount=float(transaction.amount), # Convert string amount to float
                account_id=transaction.account_id,
                expense_type_id=transaction.expense_type_id,
                month_id=transaction.month_id,
                subscription_id=transaction.subscription_id,
                debt_id=transaction.debt_id,
                split=transaction.split,
                subs=transaction.subs
            )
            
            notion_response_data = create_expense(**payload.dict(exclude_none=True))
        elif transaction.type == "income":
            payload = IncomeCreatePayload(
                date=transaction.date,
                name=transaction.name,
                concept=transaction.concept,
                amount=float(transaction.amount),
                account_id=transaction.account_id,
                month_id=transaction.month_id,
                income_type_id=transaction.income_type_id
            )
            notion_response_data = create_income(**payload.dict(exclude_none=True))
        elif transaction.type == "transfer":
            payload = TransferCreatePayload(
                date=transaction.date,
                name=transaction.name,
                amount=float(transaction.amount),
                from_account_id=transaction.from_account_id,
                from_saving_id=transaction.from_saving_id,
                to_account_id=transaction.to_account_id,
                to_saving_id=transaction.to_saving_id,
                transfer_type=transaction.transfer_type,
                month_id=transaction.month_id
            )
            notion_response_data = create_transfer(**payload.dict(exclude_none=True))
        else:
            raise HTTPException(status_code=400, detail=f"Unknown transaction type: {transaction.type}")

        # Check Notion API response
        if notion_response_data and notion_response_data.get("object") == "error":
            error_message = notion_response_data.get("message", "Unknown error from Notion API")
            print(f"Notion API Error for {transaction.type} ({transaction.name}): {error_message}") # Log error
            print(f"Payload sent: {payload.model_dump_json(indent=2)}") # Log payload for debugging
            # Consider returning a more specific error code if Notion provides one
            return ResponseModel(
                status="error",
                message=f"Notion API Error: {error_message}",
                data=notion_response_data # Send full Notion error back if helpful
            )
            # Alternative: raise HTTPException(status_code=502, detail=f"Notion API Error: {error_message}")


        return ResponseModel(
            status="success",
            message=f"{transaction.type.capitalize()} '{transaction.name}' created successfully in Notion.",
            data=notion_response_data # Return the Notion page object
        )
    except ValueError as ve: # e.g. float conversion error
        raise HTTPException(status_code=400, detail=f"Invalid data for transaction: {str(ve)}")
    except Exception as e:
        print(f"Error saving transaction: {type(e).__name__} - {str(e)}")
        # traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error saving transaction: {str(e)}")