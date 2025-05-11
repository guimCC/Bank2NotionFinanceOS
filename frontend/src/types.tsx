// Base entities from backend
export interface Account {
    id: string;
    name: string;
  }
  
  export interface ExpenseType {
    id: string;
    name: string;
  }
  
  export interface IncomeType {
    id: string;
    name: string;
  }
  
  export interface Month {
    id: string;
    name: string;
  }
  
  export interface Subscription {
    id: string;
    name: string;
  }
  
  export interface Debt {
    id: string;
    name: string;
  }
  
  export interface Saving {
    id: string;
    name: string;
  }
  
  // Transaction data
  export interface Transaction {
    type: 'expense' | 'income' | 'transfer';
    date: string;
    concept: string;
    amount: string;
    name: string;
    
    // Common fields
    account_id: string | null;
    month_id: string | null;
    
    // Expense fields
    expense_type_id: string | null;
    subscription_id: string | null;
    debt_id: string | null;
    split: boolean | false;
    subs: boolean | false;
    
    // Income fields
    income_type_id: string | null;
    
    // Transfer fields
    from_account_id: string | null;
    from_saving_id: string | null;
    to_account_id: string | null;
    to_saving_id: string | null;
    transfer_type: string | null;
    
    // UI state
    saved?: boolean;
    
    // CSV tracking
    csv_row_id?: number;
    csv_filename?: string;
  }
  
  // API data structure
  export interface ApiData {
    accounts: Account[];
    expenseTypes: ExpenseType[];
    incomeTypes: IncomeType[];
    months: Month[];
    subscriptions: Subscription[];
    debts: Debt[];
    savings: Saving[];
  }
  
  // CSV Processing response
  export interface CSVStats {
    total: number;
    expenses: number;
    incomes: number;
    transfers: number;
    unknown: number;
    already_loaded: number;
  }
  
  export interface CSVProcessResponse {
    status: string;
    message: string;
    entries: Transaction[];
    stats: CSVStats;
  }