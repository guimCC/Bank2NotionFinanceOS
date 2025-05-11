
export interface BaseItem { id: string; name: string; }
export interface Account extends BaseItem {}
export interface ExpenseType extends BaseItem {}
export interface IncomeType extends BaseItem {}
export interface Month extends BaseItem {}
export interface Subscription extends BaseItem {}
export interface Debt extends BaseItem {}
export interface Saving extends BaseItem {}

export interface TransactionEntryData {
  type: 'expense' | 'income' | 'transfer';
  date: string;
  amount: string;
  concept: string;
  month_id?: string | null;
  account_id?: string | null;
  name: string;

  original_csv_filename: string;
  csv_row_index: number; // Index in the originally parsed CSV data

  expense_type_id?: string | null;
  subscription_id?: string | null;
  debt_id?: string | null;
  split: boolean;
  subs: boolean;

  income_type_id?: string | null;

  from_account_id?: string | null;
  from_saving_id?: string | null;
  to_account_id?: string | null;
  to_saving_id?: string | null;
  transfer_type?: string | null;
}

export interface CSVProcessStatsData {
    total_rows_in_csv: number;
    processed_for_review: number;
    already_loaded_in_csv: number;
    expenses_found: number;
    incomes_found: number;
    transfers_found: number;
    unknown_type: number;
}

export interface CSVProcessResponseData {
  status: string;
  message: string;
  entries: TransactionEntryData[];
  stats: CSVProcessStatsData;
}