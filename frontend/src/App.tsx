import React, { useState, useEffect, ChangeEvent, FormEvent, KeyboardEvent } from 'react';
import './App.css';

// Import API functions from api.ts
import {
  fetchAccounts, fetchExpenseTypes, fetchIncomeTypes, fetchMonths,
  fetchSubscriptions, fetchDebts, fetchSavings, processCsvFile, saveTransaction,
} from './api';

// Import types from types.tsx
import type {
  Account, ExpenseType, IncomeType, Month, Subscription, Debt, Saving,
  TransactionEntryData, CSVProcessResponseData, CSVProcessStatsData
} from './types';

import Papa from 'papaparse'; // For CSV parsing and generation

// Type for raw CSV row data stored in frontend
interface RawCsvRow {
  [key: string]: string; // Allows any header names
  LOADED?: string; // Ensure LOADED is potentially present
}

const getMonthIdForDate = (dateString: string, months: Month[]): string | undefined => {
  if (!dateString || !months.length) return undefined;
  try {
    const parts = dateString.split('-');
    if (parts.length !== 3) return undefined;
    const day = parseInt(parts[2], 10);
    const month = parseInt(parts[1], 10);
    const year = parseInt(parts[0], 10);

    if (isNaN(day) || isNaN(month) || isNaN(year)) return undefined;

    const dateObj = new Date(year, month - 1, day);
    const monthName = dateObj.toLocaleString('default', { month: 'long' });
    const formattedMonthYear = `${monthName} ${year}`;

    const foundMonth = months.find(m => m.name === formattedMonthYear);
    return foundMonth?.id;
  } catch (e) {
    console.error("Error parsing date for month ID:", e);
    return undefined;
  }
};

function App() {
  // Initial data "cache"
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [expenseTypes, setExpenseTypes] = useState<ExpenseType[]>([]);
  const [incomeTypes, setIncomeTypes] = useState<IncomeType[]>([]);
  const [months, setMonths] = useState<Month[]>([]);
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [debts, setDebts] = useState<Debt[]>([]);
  const [savings, setSavings] = useState<Saving[]>([]);
  const [isLoadingInitialData, setIsLoadingInitialData] = useState(true);

  // CSV processing state
  const [selectedCsvFile, setSelectedCsvFile] = useState<File | null>(null);
  const [originalCsvFileName, setOriginalCsvFileName] = useState<string>("");
  const [rawCsvData, setRawCsvData] = useState<RawCsvRow[]>([]); // Parsed CSV content
  const [csvHeaders, setCsvHeaders] = useState<string[]>([]);    // Headers from CSV

  const [processedEntries, setProcessedEntries] = useState<TransactionEntryData[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [currentEntryData, setCurrentEntryData] = useState<TransactionEntryData | null>(null);
  const [isProcessingCsv, setIsProcessingCsv] = useState(false);
  const [isSubmittingEntry, setIsSubmittingEntry] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [uploadStats, setUploadStats] = useState<CSVProcessStatsData | null>(null);
  const [submittedCount, setSubmittedCount] = useState(0);

  // Load all entity data on component mount
  useEffect(() => {
    async function loadAllEntities() {
      setIsLoadingInitialData(true);
      setError(null);
      
      try {
        // Fetch all entity data in parallel
        const [
          accountsData, 
          expenseTypesData, 
          incomeTypesData, 
          monthsData, 
          subscriptionsData, 
          debtsData, 
          savingsData
        ] = await Promise.all([
          fetchAccounts(),
          fetchExpenseTypes(),
          fetchIncomeTypes(),
          fetchMonths(),
          fetchSubscriptions(),
          fetchDebts(),
          fetchSavings()
        ]);
        
        // Set state with fetched data
        setAccounts(accountsData);
        setExpenseTypes(expenseTypesData);
        setIncomeTypes(incomeTypesData);
        setMonths(monthsData);
        setSubscriptions(subscriptionsData);
        setDebts(debtsData);
        setSavings(savingsData);
        
        console.log("Entity data loaded:", {
          accounts: accountsData.length,
          expenseTypes: expenseTypesData.length,
          months: monthsData.length,
          // etc.
        });
      } catch (err) {
        console.error("Failed to load entity data:", err);
        setError("Failed to load required data. Please reload the page.");
      } finally {
        setIsLoadingInitialData(false);
      }
    }
    
    loadAllEntities();
  }, []); // Empty dependency array = only runs once on mount

  useEffect(() => { /* ... Update currentEntryData (same as before) ... */
    if (processedEntries.length > 0 && currentIndex < processedEntries.length) {
      const entry = processedEntries[currentIndex];
      const initialMonthId = entry.month_id || getMonthIdForDate(entry.date, months);
    
    console.log("Original date:", entry.date);

    setCurrentEntryData({ 
      ...entry, 
      month_id: initialMonthId,
      date: entry.date 
    });
    } else {
      setCurrentEntryData(null);
    }
  }, [currentIndex, processedEntries, months]);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      setSelectedCsvFile(file);
      setOriginalCsvFileName(file.name);
      setProcessedEntries([]);
      setCurrentIndex(0);
      setSubmittedCount(0);
      setUploadStats(null);
      setError(null);
      setSuccessMessage(null);

      // Parse CSV for frontend use
      Papa.parse<RawCsvRow>(file, {
        header: true,
        skipEmptyLines: true,
        complete: (results) => {
          if (results.errors.length > 0) {
            setError("Error parsing CSV file: " + results.errors.map(e => e.message).join(", "));
            setRawCsvData([]);
            setCsvHeaders([]);
            return;
          }
          if (!results.meta.fields) {
             setError("Could not determine CSV headers.");
             setRawCsvData([]);
             setCsvHeaders([]);
             return;
          }
          // Ensure LOADED column exists for future updates
          const headers = results.meta.fields;
          if (!headers.includes('LOADED')) {
            headers.push('LOADED');
          }
          setCsvHeaders(headers);
          // Initialize LOADED for rows if not present, or keep existing
          const dataWithLoaded = results.data.map(row => ({
            ...row,
            LOADED: row.LOADED || '' // Default to empty string if not present
          }));
          setRawCsvData(dataWithLoaded);
        },
        error: (err) => {
          setError("PapaParse Error: " + err.message);
          setRawCsvData([]);
          setCsvHeaders([]);
        }
      });
    }
  };

  const handleProcessCsvOnBackend = async () => {
    if (!selectedCsvFile) {
      setError("Please select a CSV file first.");
      return;
    }
    if (rawCsvData.length === 0 && csvHeaders.length === 0) {
        setError("CSV data not parsed correctly on frontend. Please re-select the file.");
        return;
    }
    setIsProcessingCsv(true);
    setError(null);
    setSuccessMessage(null);
    try {
      const response = await processCsvFile(selectedCsvFile);
      setProcessedEntries(response.entries);
      setUploadStats(response.stats);
      setCurrentIndex(0);
      setSubmittedCount(0);
      if (response.entries.length === 0) {
        setSuccessMessage(`CSV processed by backend. ${response.message}. No new entries to load.`);
      } else {
         setSuccessMessage(`CSV processed successfully by backend. ${response.entries.length} entries ready for review.`);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.response?.data?.message || err.message || "Error processing CSV file on backend.");
      setProcessedEntries([]);
    } finally {
      setIsProcessingCsv(false);
    }
  };

  const handleInputChange = (event: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => { /* ... same as before ... */
    if (!currentEntryData) return;
    const { name, value, type } = event.target;
    let newValue: string | boolean = value;
    if (type === 'checkbox') {
        newValue = (event.target as HTMLInputElement).checked;
    }
    const updatedEntry = { ...currentEntryData, [name]: newValue };
    if (name === 'date') {
      updatedEntry.month_id = getMonthIdForDate(value, months);
    }
    setCurrentEntryData(updatedEntry);
  };

  const handleTransactionTypeChange = (newType: 'expense' | 'income' | 'transfer') => { /* ... same as before ... */
    if (!currentEntryData) return;
    const commonData = {
        name: currentEntryData.name,
        date: currentEntryData.date,
        amount: currentEntryData.amount,
        concept: currentEntryData.concept,
        account_id: currentEntryData.account_id,
        month_id: currentEntryData.month_id,
        original_csv_filename: currentEntryData.original_csv_filename,
        csv_row_index: currentEntryData.csv_row_index,
    };
    let newEntryData: TransactionEntryData;
    switch (newType) {
        case 'expense':
            newEntryData = { ...commonData, type: 'expense', expense_type_id: expenseTypes[0]?.id || null, subscription_id: null, debt_id: null, split: false, subs: false, };
            break;
        case 'income':
            newEntryData = { ...commonData, type: 'income', income_type_id: incomeTypes[0]?.id || null, };
            break;
        case 'transfer':
            newEntryData = { ...commonData, type: 'transfer', from_account_id: null, from_saving_id: null, to_account_id: currentEntryData.account_id, to_saving_id: null, transfer_type: 'Other', };
            break;
        default: return;
    }
    setCurrentEntryData(newEntryData);
  };

  const handleSubmitEntry = async (event?: FormEvent) => {
    if (event) event.preventDefault();
    if (!currentEntryData) return;

    setIsSubmittingEntry(true);
    setError(null);
    setSuccessMessage(null);

    try {
      await saveTransaction(currentEntryData);
      setSuccessMessage(`Entry "${currentEntryData.name}" saved to Notion!`);
      setSubmittedCount(prev => prev + 1);

      // Update in-memory CSV data
      setRawCsvData(prevRawData => {
        const newData = [...prevRawData];
        if (newData[currentEntryData.csv_row_index]) {
          newData[currentEntryData.csv_row_index] = {
            ...newData[currentEntryData.csv_row_index],
            LOADED: 'true' // Or '1'
          };
        }
        return newData;
      });

      if (currentIndex < processedEntries.length - 1) {
        setCurrentIndex(prev => prev + 1);
      } else {
        setCurrentEntryData(null);
        setSuccessMessage('All entries processed and saved to Notion! You can now download the updated CSV.');
      }
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || `Failed to save entry "${currentEntryData.name}".`);
    } finally {
      setIsSubmittingEntry(false);
    }
  };
  
  const handleKeyPress = (event: KeyboardEvent<HTMLFormElement>) => { /* ... same as before ... */
    if (event.key === 'Enter' && !isSubmittingEntry && currentEntryData) {
        const target = event.target as HTMLElement;
        if (target.nodeName !== 'TEXTAREA' && target.nodeName !== 'BUTTON') {
            event.preventDefault();
            handleSubmitEntry();
        }
    }
  };

  const handleCopyFromPrevious = () => { /* ... same as before ... */
    if (currentIndex > 0 && processedEntries[currentIndex - 1] && currentEntryData) {
      const prevEntry = processedEntries[currentIndex - 1];
      if (currentEntryData.type === 'expense' && prevEntry.type === 'expense') {
        setCurrentEntryData({ ...currentEntryData, name: prevEntry.name || currentEntryData.name, expense_type_id: prevEntry.expense_type_id || currentEntryData.expense_type_id, account_id: prevEntry.account_id || currentEntryData.account_id, });
        setSuccessMessage("Copied relevant fields from previous expense.");
      } else if (currentEntryData.type === 'income' && prevEntry.type === 'income') {
         setCurrentEntryData({ ...currentEntryData, name: prevEntry.name || currentEntryData.name, income_type_id: prevEntry.income_type_id || currentEntryData.income_type_id, account_id: prevEntry.account_id || currentEntryData.account_id, });
        setSuccessMessage("Copied relevant fields from previous income.");
      } else {
        setError("Cannot copy: Previous entry is of a different type or no relevant fields to copy for this type.");
      }
    } else {
      setError("No previous entry to copy from or current entry type mismatch.");
    }
  };

  const handleDownloadUpdatedCsv = () => {
    if (rawCsvData.length === 0 || csvHeaders.length === 0) {
      setError("No CSV data to download.");
      return;
    }
    // Ensure LOADED is a header if it wasn't originally but we added it
    const finalHeaders = [...csvHeaders];
    if (!finalHeaders.includes('LOADED') && rawCsvData.some(row => row.hasOwnProperty('LOADED'))) {
        finalHeaders.push('LOADED');
    }

    const csvString = Papa.unparse(rawCsvData, { header: true, columns: finalHeaders });
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", `updated_${originalCsvFileName || 'transactions.csv'}`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setSuccessMessage("Updated CSV downloaded.");
  };


  if (isLoadingInitialData) { /* ... same as before ... */ return <div className="container">Loading initial application data...</div>;}

  return (
    <div className="container">
      <h1>Notion CSV Uploader</h1>

      {error && <div className="message error-message">{error}</div>}
      {successMessage && <div className="message success-message">{successMessage}</div>}

      <div className="section file-upload-section">
        <h2>1. Upload CSV</h2>
        <input type="file" accept=".csv" onChange={handleFileChange} />
        <button onClick={handleProcessCsvOnBackend} disabled={!selectedCsvFile || isProcessingCsv || rawCsvData.length === 0}>
          {isProcessingCsv ? 'Processing...' : 'Process CSV with Backend'}
        </button>
      </div>

      {uploadStats && (
        <div className="section stats-section">
            <h3>CSV Stats (from backend processing):</h3>
            <p>Total Rows in original CSV: {uploadStats.total_rows_in_csv}</p>
            <p>Entries Marked 'LOADED' in CSV: {uploadStats.already_loaded_in_csv}</p>
            <p>New Entries for Review: {uploadStats.processed_for_review}</p>
            <p>Detected Types: Expenses: {uploadStats.expenses_found}, Incomes: {uploadStats.incomes_found}, Transfers: {uploadStats.transfers_found}, Unknown: {uploadStats.unknown_type}</p>
        </div>
      )}

      {/* ... (The form rendering logic for currentEntryData remains largely the same) ... */}
      {processedEntries.length > 0 && currentEntryData && (
        <div className="section entry-form-section">
          <h2>2. Review and Submit Entry ({currentIndex + 1} of {processedEntries.length})</h2>
          <p>Submitted to Notion: {submittedCount} / {processedEntries.length}</p>
          
          <form onSubmit={handleSubmitEntry} onKeyDown={handleKeyPress}>
            {/* ... form groups for type, name, date, amount, concept, month_id ... */}
            {/* ... conditional rendering for expense, income, transfer fields ... */}
            {/* Example for common fields - rest is same as previous App.tsx */}
            <div className="form-group">
                <label>Transaction Type:</label>
                <select name="type" value={currentEntryData.type} onChange={(e) => handleTransactionTypeChange(e.target.value as 'expense'|'income'|'transfer')}>
                    <option value="expense">Expense</option>
                    <option value="income">Income</option>
                    <option value="transfer">Transfer</option>
                </select>
            </div>
            <div className="form-group">
              <label htmlFor="name">Name:</label>
              <input type="text" id="name" name="name" value={currentEntryData.name} onChange={handleInputChange} required />
            </div>
            <div className="form-group">
              <label htmlFor="date">Date (YYYY-MM-DD):</label>
              <input 
                type="text" 
                id="date" 
                name="date" 
                value={currentEntryData.date} 
                onChange={handleInputChange} 
                required 
                pattern="\d{4}-\d{2}-\d{2}" 
              />
            </div>
            <div className="form-group">
              <label htmlFor="amount">Amount:</label>
              <input type="number" id="amount" name="amount" value={currentEntryData.amount} onChange={handleInputChange} required step="0.01" />
            </div>
            <div className="form-group">
              <label htmlFor="concept">Concept/Note:</label>
              <textarea id="concept" name="concept" value={currentEntryData.concept} onChange={handleInputChange} />
            </div>
             <div className="form-group">
                <label htmlFor="month_id">Month:</label>
                <select id="month_id" name="month_id" value={currentEntryData.month_id || ''} onChange={handleInputChange} required>
                    <option value="">Select Month</option>
                    {months.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
                </select>
            </div>

            {/* Expense Fields */}
            {currentEntryData.type === 'expense' && (
              <>
                <div className="form-group">
                  <label htmlFor="account_id">Account:</label>
                  <select id="account_id" name="account_id" value={currentEntryData.account_id || ''} onChange={handleInputChange}> <option value="">Select Account</option> {accounts.map(acc => <option key={acc.id} value={acc.id}>{acc.name}</option>)} </select>
                </div>
                <div className="form-group">
                  <label htmlFor="expense_type_id">Expense Type:</label>
                  <select id="expense_type_id" name="expense_type_id" value={currentEntryData.expense_type_id || ''} onChange={handleInputChange}> <option value="">Select Expense Type</option> {expenseTypes.map(et => <option key={et.id} value={et.id}>{et.name}</option>)} </select>
                </div>
                <div className="form-group">
                  <label htmlFor="subscription_id">Subscription:</label>
                  <select id="subscription_id" name="subscription_id" value={currentEntryData.subscription_id || ''} onChange={handleInputChange}> <option value="">None</option> {subscriptions.map(s => <option key={s.id} value={s.id}>{s.name}</option>)} </select>
                </div>
                <div className="form-group">
                  <label htmlFor="debt_id">Debt:</label>
                  <select id="debt_id" name="debt_id" value={currentEntryData.debt_id || ''} onChange={handleInputChange}> <option value="">None</option> {debts.map(d => <option key={d.id} value={d.id}>{d.name}</option>)} </select>
                </div>
                <div className="form-group checkbox-group"> <input type="checkbox" id="split" name="split" checked={currentEntryData.split} onChange={handleInputChange} /> <label htmlFor="split">Split</label> </div>
                <div className="form-group checkbox-group"> <input type="checkbox" id="subs" name="subs" checked={currentEntryData.subs} onChange={handleInputChange} /> <label htmlFor="subs">Subs</label> </div>
              </>
            )}
            {/* Income Fields */}
            {currentEntryData.type === 'income' && (
              <>
                <div className="form-group">
                  <label htmlFor="account_id">Account:</label>
                  <select id="account_id" name="account_id" value={currentEntryData.account_id || ''} onChange={handleInputChange}> <option value="">Select Account</option> {accounts.map(acc => <option key={acc.id} value={acc.id}>{acc.name}</option>)} </select>
                </div>
                <div className="form-group">
                  <label htmlFor="income_type_id">Income Type:</label>
                  <select id="income_type_id" name="income_type_id" value={currentEntryData.income_type_id || ''} onChange={handleInputChange}> <option value="">Select Income Type</option> {incomeTypes.map(it => <option key={it.id} value={it.id}>{it.name}</option>)} </select>
                </div>
              </>
            )}
            {/* Transfer Fields */}
            {currentEntryData.type === 'transfer' && (
              <>
                 <div className="form-group">
                  <label htmlFor="transfer_type">Transfer Type:</label>
                  <select id="transfer_type" name="transfer_type" value={currentEntryData.transfer_type || ''} onChange={handleInputChange}> <option value="">Select Type</option> <option value="Studies">Studies</option> <option value="Return">Return</option> <option value="Moving">Moving</option> <option value="Saving">Saving</option> <option value="Funding">Funding</option> <option value="Other">Other</option> </select>
                </div>
                <div className="form-group">
                  <label htmlFor="from_account_id">From Account:</label>
                  <select id="from_account_id" name="from_account_id" value={currentEntryData.from_account_id || ''} onChange={handleInputChange}> <option value="">None</option> {accounts.map(acc => <option key={acc.id} value={acc.id}>{acc.name}</option>)} </select>
                </div>
                 <div className="form-group">
                  <label htmlFor="from_saving_id">From Saving Account:</label>
                  <select id="from_saving_id" name="from_saving_id" value={currentEntryData.from_saving_id || ''} onChange={handleInputChange}> <option value="">None</option> {savings.map(s => <option key={s.id} value={s.id}>{s.name}</option>)} </select>
                </div>
                <div className="form-group">
                  <label htmlFor="to_account_id">To Account:</label>
                  <select id="to_account_id" name="to_account_id" value={currentEntryData.to_account_id || ''} onChange={handleInputChange}> <option value="">None</option> {accounts.map(acc => <option key={acc.id} value={acc.id}>{acc.name}</option>)} </select>
                </div>
                <div className="form-group">
                  <label htmlFor="to_saving_id">To Saving Account:</label>
                  <select id="to_saving_id" name="to_saving_id" value={currentEntryData.to_saving_id || ''} onChange={handleInputChange}> <option value="">None</option> {savings.map(s => <option key={s.id} value={s.id}>{s.name}</option>)} </select>
                </div>
              </>
            )}
            
            <div className="form-actions">
                <button type="button" onClick={handleCopyFromPrevious} disabled={currentIndex === 0 || isSubmittingEntry}>
                    Copy from Previous
                </button>
                <button type="submit" disabled={isSubmittingEntry}>
                    {isSubmittingEntry ? 'Submitting...' : 'Submit to Notion'}
                </button>
            </div>
          </form>
        </div>
      )}
      
      {processedEntries.length > 0 && !currentEntryData && submittedCount === processedEntries.length && (
        <div className="section">
            <h2>All entries have been processed for Notion!</h2>
            <button onClick={handleDownloadUpdatedCsv} disabled={rawCsvData.length === 0}>
                Download Updated CSV
            </button>
        </div>
      )}
      { rawCsvData.length > 0 && submittedCount < processedEntries.length && submittedCount > 0 && (
           <div className="section">
            <button onClick={handleDownloadUpdatedCsv} disabled={rawCsvData.length === 0}>
                Download Partially Updated CSV
            </button>
          </div>
      )}
    </div>
  );
}

export default App;