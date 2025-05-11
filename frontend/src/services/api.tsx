import axios from 'axios';
import { ApiData, Transaction, CSVProcessResponse } from '../types';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Fetch all required reference data
export const fetchAllData = async (): Promise<ApiData> => {
  try {
    const [accounts, expenseTypes, incomeTypes, months, subscriptions, debts, savings] = 
      await Promise.all([
        api.get('/accounts'),
        api.get('/expense-types'),
        api.get('/income-types'),
        api.get('/months'),
        api.get('/subscriptions'),
        api.get('/debts'),
        api.get('/savings')
      ]);
    
    return {
      accounts: accounts.data,
      expenseTypes: expenseTypes.data,
      incomeTypes: incomeTypes.data,
      months: months.data,
      subscriptions: subscriptions.data,
      debts: debts.data,
      savings: savings.data
    };
  } catch (error) {
    console.error('Error fetching data:', error);
    throw new Error('Failed to load required data');
  }
};

// Process CSV file
export const processCSVFile = async (file: File): Promise<CSVProcessResponse> => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/process-csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('Error processing CSV:', error);
    throw new Error('Failed to process CSV file');
  }
};

// Save transaction
export const saveTransaction = async (transaction: Transaction) => {
  try {
    const response = await api.post('/save-transaction', transaction);
    
    if (response.data.status === 'error') {
      throw new Error(response.data.message);
    }
    
    return response.data;
  } catch (error) {
    console.error('Error saving transaction:', error);
    throw new Error('Failed to save transaction');
  }
};

export default api;