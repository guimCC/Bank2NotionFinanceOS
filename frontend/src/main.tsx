// This imports your App component and renders it to the DOM element with id "root"
import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import App from './App'  // This is correct

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)