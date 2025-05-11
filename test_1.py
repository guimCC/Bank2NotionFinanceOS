if __name__ == "__main__":
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
    #     amount="-24.99",
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