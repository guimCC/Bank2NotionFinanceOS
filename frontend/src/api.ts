// src/api.ts
import axios from 'axios';
import type{
  Account, ExpenseType, IncomeType, Month, Subscription, Debt, Saving,
  TransactionEntryData, CSVProcessResponseData, CSVProcessStatsData
} from './types';
const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});


// API Functions (fetchAccounts, etc., remain the same)
export const fetchAccounts = async (): Promise<Account[]> => (await apiClient.get('/accounts')).data;
export const fetchExpenseTypes = async (): Promise<ExpenseType[]> => (await apiClient.get('/expense-types')).data;
export const fetchIncomeTypes = async (): Promise<IncomeType[]> => (await apiClient.get('/income-types')).data;
export const fetchMonths = async (): Promise<Month[]> => (await apiClient.get('/months')).data;
export const fetchSubscriptions = async (): Promise<Subscription[]> => (await apiClient.get('/subscriptions')).data;
export const fetchDebts = async (): Promise<Debt[]> => (await apiClient.get('/debts')).data;
export const fetchSavings = async (): Promise<Saving[]> => (await apiClient.get('/savings')).data;


export const processCsvFile = async (file: File): Promise<CSVProcessResponseData> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await apiClient.post('/process-csv', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

// This function now sends the complete TransactionEntryData object from the frontend
// The backend will extract necessary fields for its *CreatePayload models
export const saveTransaction = async (transactionData: TransactionEntryData): Promise<any> => {
  // Convert DD/MM/YYYY to YYYY-MM-DD format

  
  const payload = {
    ...transactionData,
    amount: transactionData.amount,
  };
  
  console.log("Sending payload to save-transaction:", payload);
  return (await apiClient.post('/save-transaction', payload)).data;
};