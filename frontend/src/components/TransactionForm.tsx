import { useState } from 'react';
import {
  Paper, Box, TextField, FormControl, InputLabel, Select, MenuItem,
  FormControlLabel, Checkbox, Typography, Divider,
  RadioGroup, Radio, FormLabel, SelectChangeEvent,
  Grid
} from '@mui/material';
import { Transaction, ApiData } from '../types';

interface TransactionFormProps {
  transaction: Transaction;
  apiData: ApiData;
  onUpdate: (transaction: Transaction) => void;
}

const TransactionForm = ({ transaction, apiData, onUpdate }: TransactionFormProps) => {
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    onUpdate({
      ...transaction,
      [e.target.name]: e.target.value
    });
  };

  const handleSelectChange = (e: SelectChangeEvent<string | null>) => {
    onUpdate({
      ...transaction,
      [e.target.name]: e.target.value === '' ? null : e.target.value
    });
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onUpdate({
      ...transaction,
      [e.target.name]: e.target.checked
    });
  };

  const handleTypeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Create a new transaction object with the updated type
    // and reset type-specific fields
    const newType = e.target.value as 'expense' | 'income' | 'transfer';
    
    // Find default account (Caixa Enginyers or first)
    const defaultAccount = apiData.accounts.find(acc => acc.name === 'Caixa Enginyers') || 
                          apiData.accounts[0];
    
    let updatedTransaction: Transaction = {
      ...transaction,
      type: newType
    };
    
    // Reset type-specific fields based on the new type
    if (newType === 'expense') {
      updatedTransaction = {
        ...updatedTransaction,
        expense_type_id: null,
        subscription_id: null,
        debt_id: null,
        split: false,
        subs: false,
        income_type_id: null,
        from_account_id: null,
        from_saving_id: null,
        to_account_id: null,
        to_saving_id: null,
        transfer_type: null,
        account_id: defaultAccount?.id || null
      };
    } else if (newType === 'income') {
      updatedTransaction = {
        ...updatedTransaction,
        income_type_id: null,
        expense_type_id: null,
        subscription_id: null,
        debt_id: null,
        split: false,
        subs: false,
        from_account_id: null,
        from_saving_id: null,
        to_account_id: null,
        to_saving_id: null,
        transfer_type: null,
        account_id: defaultAccount?.id || null
      };
    } else if (newType === 'transfer') {
      updatedTransaction = {
        ...updatedTransaction,
        from_account_id: null,
        from_saving_id: null,
        to_account_id: defaultAccount?.id || null,
        to_saving_id: null,
        transfer_type: 'Return',
        expense_type_id: null,
        subscription_id: null,
        debt_id: null,
        split: false,
        subs: false,
        income_type_id: null,
        account_id: null
      };
    }
    
    onUpdate(updatedTransaction);
  };

  // Get background color based on transaction type
  const getHeaderBgColor = () => {
    switch (transaction.type) {
      case 'expense': return '#ffebee'; // Light red
      case 'income': return '#e8f5e9'; // Light green
      case 'transfer': return '#e3f2fd'; // Light blue
      default: return '#f5f5f5'; // Light grey
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      {/* Header with transaction type selection */}
      <Box sx={{ bgcolor: getHeaderBgColor(), p: 2, borderRadius: 1, mb: 3 }}>
        <FormControl component="fieldset">
          <FormLabel component="legend">Transaction Type</FormLabel>
          <RadioGroup row value={transaction.type} onChange={handleTypeChange}>
            <FormControlLabel value="expense" control={<Radio />} label="Expense" />
            <FormControlLabel value="income" control={<Radio />} label="Income" />
            <FormControlLabel value="transfer" control={<Radio />} label="Transfer" />
          </RadioGroup>
        </FormControl>
      </Box>
      
      {/* Common fields */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Date"
            name="date"
            value={transaction.date}
            onChange={handleInputChange}
            InputProps={{ readOnly: true }}
            margin="normal"
            helperText="Format: DD/MM/YYYY"
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Amount"
            name="amount"
            value={transaction.amount}
            onChange={handleInputChange}
            InputProps={{ readOnly: true }}
            margin="normal"
          />
        </Grid>
        
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Concept"
            name="concept"
            value={transaction.concept}
            onChange={handleInputChange}
            InputProps={{ readOnly: true }}
            margin="normal"
            multiline
            rows={2}
          />
        </Grid>
        
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Name"
            name="name"
            value={transaction.name}
            onChange={handleInputChange}
            margin="normal"
            placeholder="Transaction name"
          />
        </Grid>
        
        <Grid item xs={12}>
          <FormControl fullWidth margin="normal">
            <InputLabel>Month</InputLabel>
            <Select
              name="month_id"
              value={transaction.month_id || ''}
              onChange={handleSelectChange}
              label="Month"
            >
              <MenuItem value="">
                <em>None</em>
              </MenuItem>
              {apiData.months.map(month => (
                <MenuItem key={month.id} value={month.id}>
                  {month.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      </Grid>
      
      <Divider sx={{ my: 3 }} />
      
      {/* Expense specific fields */}
      {transaction.type === 'expense' && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <FormControl fullWidth margin="normal">
              <InputLabel>Account</InputLabel>
              <Select
                name="account_id"
                value={transaction.account_id || ''}
                onChange={handleSelectChange}
                label="Account"
              >
                <MenuItem value="">
                  <em>None</em>
                </MenuItem>
                {apiData.accounts.map(account => (
                  <MenuItem key={account.id} value={account.id}>
                    {account.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12}>
            <FormControl fullWidth margin="normal">
              <InputLabel>Expense Type</InputLabel>
              <Select
                name="expense_type_id"
                value={transaction.expense_type_id || ''}
                onChange={handleSelectChange}
                label="Expense Type"
              >
                <MenuItem value="">
                  <em>None</em>
                </MenuItem>
                {apiData.expenseTypes.map(type => (
                  <MenuItem key={type.id} value={type.id}>
                    {type.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={transaction.split || false}
                  onChange={handleCheckboxChange}
                  name="split"
                />
              }
              label="Split"
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={transaction.subs || false}
                  onChange={handleCheckboxChange}
                  name="subs"
                />
              }
              label="Subscription"
            />
          </Grid>
          
          {transaction.subs && (
            <Grid item xs={12}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Subscription</InputLabel>
                <Select
                  name="subscription_id"
                  value={transaction.subscription_id || ''}
                  onChange={handleSelectChange}
                  label="Subscription"
                >
                  <MenuItem value="">
                    <em>None</em>
                  </MenuItem>
                  {apiData.subscriptions.map(sub => (
                    <MenuItem key={sub.id} value={sub.id}>
                      {sub.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          )}
          
          <Grid item xs={12}>
            <FormControl fullWidth margin="normal">
              <InputLabel>Debt</InputLabel>
              <Select
                name="debt_id"
                value={transaction.debt_id || ''}
                onChange={handleSelectChange}
                label="Debt"
              >
                <MenuItem value="">
                  <em>None</em>
                </MenuItem>
                {apiData.debts.map(debt => (
                  <MenuItem key={debt.id} value={debt.id}>
                    {debt.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      )}
      
      {/* Income specific fields */}
      {transaction.type === 'income' && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <FormControl fullWidth margin="normal">
              <InputLabel>Account</InputLabel>
              <Select
                name="account_id"
                value={transaction.account_id || ''}
                onChange={handleSelectChange}
                label="Account"
              >
                <MenuItem value="">
                  <em>None</em>
                </MenuItem>
                {apiData.accounts.map(account => (
                  <MenuItem key={account.id} value={account.id}>
                    {account.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12}>
            <FormControl fullWidth margin="normal">
              <InputLabel>Income Type</InputLabel>
              <Select
                name="income_type_id"
                value={transaction.income_type_id || ''}
                onChange={handleSelectChange}
                label="Income Type"
              >
                <MenuItem value="">
                  <em>None</em>
                </MenuItem>
                {apiData.incomeTypes.map(type => (
                  <MenuItem key={type.id} value={type.id}>
                    {type.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      )}
      
      {/* Transfer specific fields */}
      {transaction.type === 'transfer' && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth margin="normal">
              <InputLabel>From Account</InputLabel>
              <Select
                name="from_account_id"
                value={transaction.from_account_id || ''}
                onChange={handleSelectChange}
                label="From Account"
              >
                <MenuItem value="">
                  <em>None</em>
                </MenuItem>
                {apiData.accounts.map(account => (
                  <MenuItem key={account.id} value={account.id}>
                    {account.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl fullWidth margin="normal">
              <InputLabel>From Saving</InputLabel>
              <Select
                name="from_saving_id"
                value={transaction.from_saving_id || ''}
                onChange={handleSelectChange}
                label="From Saving"
              >
                <MenuItem value="">
                  <em>None</em>
                </MenuItem>
                {apiData.savings.map(saving => (
                  <MenuItem key={saving.id} value={saving.id}>
                    {saving.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl fullWidth margin="normal">
              <InputLabel>To Account</InputLabel>
              <Select
                name="to_account_id"
                value={transaction.to_account_id || ''}
                onChange={handleSelectChange}
                label="To Account"
              >
                <MenuItem value="">
                  <em>None</em>
                </MenuItem>
                {apiData.accounts.map(account => (
                  <MenuItem key={account.id} value={account.id}>
                    {account.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl fullWidth margin="normal">
              <InputLabel>To Saving</InputLabel>
              <Select
                name="to_saving_id"
                value={transaction.to_saving_id || ''}
                onChange={handleSelectChange}
                label="To Saving"
              >
                <MenuItem value="">
                  <em>None</em>
                </MenuItem>
                {apiData.savings.map(saving => (
                  <MenuItem key={saving.id} value={saving.id}>
                    {saving.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12}>
            <FormControl fullWidth margin="normal">
              <InputLabel>Transfer Type</InputLabel>
              <Select
                name="transfer_type"
                value={transaction.transfer_type || ''}
                onChange={handleSelectChange}
                label="Transfer Type"
              >
                <MenuItem value="">
                  <em>None</em>
                </MenuItem>
                <MenuItem value="Studies">Studies</MenuItem>
                <MenuItem value="Return">Return</MenuItem>
                <MenuItem value="Moving">Moving</MenuItem>
                <MenuItem value="Saving">Saving</MenuItem>
                <MenuItem value="Funding">Funding</MenuItem>
                <MenuItem value="Other">Other</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      )}
      
      {/* Show saved status */}
      {transaction.saved && (
        <Box sx={{ mt: 3, p: 2, bgcolor: '#e8f5e9', borderRadius: 1 }}>
          <Typography color="success.main" sx={{ display: 'flex', alignItems: 'center' }}>
            <Box component="span" sx={{ mr: 1, fontSize: '1.2rem' }}>✓</Box>
            Transaction saved successfully
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default TransactionForm;