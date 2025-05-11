import { useState, useEffect, useRef } from 'react';
import { 
  Box, ThemeProvider, CssBaseline, createTheme, 
  Typography, Button, Container, CircularProgress,
  Paper, Alert, Stack, LinearProgress
} from '@mui/material';
import { UploadFile as UploadIcon } from '@mui/icons-material';
import TransactionForm from './components/TransactionForm';
import { fetchAllData, processCSVFile, saveTransaction } from './services/api';
import { Transaction, ApiData } from './types';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [loading, setLoading] = useState<boolean>(false);
  const [dataLoaded, setDataLoaded] = useState<boolean>(false);
  const [apiData, setApiData] = useState<ApiData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [stats, setStats] = useState<{
    total: number;
    processed: number;
    remaining: number;
    success: number;
    failed: number;
  }>({
    total: 0,
    processed: 0,
    remaining: 0,
    success: 0,
    failed: 0,
  });
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load all required data when app initializes
  useEffect(() => {
    async function loadInitialData() {
      setLoading(true);
      try {
        const data = await fetchAllData();
        setApiData(data);
        setDataLoaded(true);
      } catch (err: any) {
        setError(`Failed to load required data: ${err.message}`);
      } finally {
        setLoading(false);
      }
    }
    
    loadInitialData();
  }, []);
  
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files || !event.target.files[0]) return;
    
    const file = event.target.files[0];
    if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
      setError('Please upload a CSV file');
      return;
    }
    
    setLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      const result = await processCSVFile(file);
      setTransactions(result.entries.map(entry => ({ ...entry, saved: false })));
      setCurrentIndex(0);
      setStats({
        total: result.entries.length,
        processed: 0,
        remaining: result.entries.length,
        success: 0,
        failed: 0,
      });
      setSuccess(`Successfully loaded ${result.entries.length} transactions`);
    } catch (err: any) {
      setError(`Failed to process CSV: ${err.message}`);
    } finally {
      setLoading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };
  
  const handleSaveTransaction = async () => {
    if (!transactions.length || currentIndex >= transactions.length) return;
    
    const currentTransaction = transactions[currentIndex];
    if (currentTransaction.saved) {
      // Already saved, move to next
      handleNext();
      return;
    }
    
    setLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      await saveTransaction(currentTransaction);
      
      // Update transaction as saved
      const updatedTransactions = [...transactions];
      updatedTransactions[currentIndex] = { ...currentTransaction, saved: true };
      setTransactions(updatedTransactions);
      
      // Update stats
      setStats(prevStats => ({
        ...prevStats,
        processed: prevStats.processed + 1,
        remaining: prevStats.remaining - 1,
        success: prevStats.success + 1
      }));
      
      setSuccess('Transaction saved successfully');
      
      // Auto-advance to next transaction after short delay
      setTimeout(() => {
        handleNext();
      }, 1000);
    } catch (err: any) {
      setError(`Failed to save transaction: ${err.message}`);
      // Update stats for failure
      setStats(prevStats => ({
        ...prevStats,
        processed: prevStats.processed + 1,
        remaining: prevStats.remaining - 1,
        failed: prevStats.failed + 1
      }));
    } finally {
      setLoading(false);
    }
  };
  
  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setError(null);
      setSuccess(null);
    }
  };
  
  const handleNext = () => {
    if (currentIndex < transactions.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setError(null);
      setSuccess(null);
    }
  };
  
  const handleTransactionUpdate = (updatedTransaction: Transaction) => {
    const updatedTransactions = [...transactions];
    updatedTransactions[currentIndex] = updatedTransaction;
    setTransactions(updatedTransactions);
  };
  
  const handleCopyFromPrevious = () => {
    if (currentIndex === 0 || !transactions.length) return;
    
    const current = transactions[currentIndex];
    const previous = transactions[currentIndex - 1];
    
    // Only copy relevant fields based on transaction type
    let updatedTransaction = { ...current };
    
    if (current.type === 'expense' && previous.type === 'expense') {
      updatedTransaction = {
        ...current,
        expense_type_id: previous.expense_type_id,
        name: previous.name
      };
    } else if (current.type === 'income' && previous.type === 'income') {
      updatedTransaction = {
        ...current,
        income_type_id: previous.income_type_id,
        name: previous.name
      };
    } else if (current.type === 'transfer' && previous.type === 'transfer') {
      updatedTransaction = {
        ...current,
        transfer_type: previous.transfer_type,
        from_account_id: previous.from_account_id,
        from_saving_id: previous.from_saving_id,
        to_account_id: previous.to_account_id,
        to_saving_id: previous.to_saving_id
      };
    }
    
    handleTransactionUpdate(updatedTransaction);
  };
  
  const progressPercentage = stats.total > 0 
    ? (stats.processed / stats.total) * 100 
    : 0;
  
  const currentTransaction = transactions[currentIndex];
  const hasPrevious = currentIndex > 0;
  const hasNext = currentIndex < transactions.length - 1;

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Notion Finance - CSV Transaction Processor
        </Typography>
        
        {/* File Upload Section */}
        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Stack direction="row" spacing={2} alignItems="center">
            <Button 
              variant="contained" 
              startIcon={<UploadIcon />}
              onClick={() => fileInputRef.current?.click()}
              disabled={loading || !dataLoaded}
            >
              Upload CSV File
            </Button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
            <Typography variant="body2" color="text.secondary">
              Upload a CSV file with DATE, CONCEPT, IMPORT, LOADED columns
            </Typography>
          </Stack>
          
          {loading && <LinearProgress sx={{ mt: 2 }} />}
        </Paper>
        
        {/* Status Messages */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}
        
        {/* Progress Stats */}
        {transactions.length > 0 && (
          <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>Progress</Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Box sx={{ width: '100%', mr: 1 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={progressPercentage} 
                  sx={{ height: 10, borderRadius: 1 }}
                />
              </Box>
              <Box sx={{ minWidth: 35 }}>
                <Typography variant="body2" color="text.secondary">
                  {Math.round(progressPercentage)}%
                </Typography>
              </Box>
            </Box>
            
            <Stack direction="row" spacing={3} justifyContent="space-between">
              <Typography>Total: {stats.total}</Typography>
              <Typography>Processed: {stats.processed}</Typography>
              <Typography>Remaining: {stats.remaining}</Typography>
              <Typography color="success.main">Success: {stats.success}</Typography>
              <Typography color="error.main">Failed: {stats.failed}</Typography>
              <Typography>
                Transaction {currentIndex + 1} of {transactions.length}
              </Typography>
            </Stack>
          </Paper>
        )}
        
        {/* Transaction Form */}
        {transactions.length > 0 && currentTransaction && apiData && (
          <>
            <TransactionForm
              transaction={currentTransaction}
              apiData={apiData}
              onUpdate={handleTransactionUpdate}
            />
            
            <Paper elevation={3} sx={{ p: 3, mt: 3, display: 'flex', justifyContent: 'space-between' }}>
              <Button 
                variant="outlined" 
                onClick={handlePrevious} 
                disabled={!hasPrevious || loading}
              >
                Previous
              </Button>
              
              <Stack direction="row" spacing={2}>
                <Button
                  variant="outlined"
                  onClick={handleCopyFromPrevious}
                  disabled={!hasPrevious || loading}
                >
                  Copy from Previous
                </Button>
                
                <Button 
                  variant="contained" 
                  onClick={handleSaveTransaction}
                  disabled={loading || currentTransaction.saved}
                  color={currentTransaction.saved ? "success" : "primary"}
                >
                  {currentTransaction.saved ? "Saved ✓" : "Save"}
                </Button>
              </Stack>
              
              <Button 
                variant="outlined" 
                onClick={handleNext} 
                disabled={!hasNext || loading}
              >
                Next
              </Button>
            </Paper>
          </>
        )}
      </Container>
    </ThemeProvider>
  );
}

export default App;