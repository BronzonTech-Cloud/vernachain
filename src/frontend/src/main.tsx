import React from 'react'
import ReactDOM from 'react-dom/client'
import { ChakraProvider } from '@chakra-ui/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { theme } from './theme'

console.log('Starting application...');

console.log('Environment Variables:', {
  API_URL: import.meta.env.VITE_API_URL,
  EXPLORER_URL: import.meta.env.VITE_EXPLORER_URL,
  NODE_URL: import.meta.env.VITE_NODE_URL,
  API_KEY: import.meta.env.VITE_API_KEY ? '[REDACTED]' : 'Not set'
});

const queryClient = new QueryClient()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ChakraProvider theme={theme}>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    </ChakraProvider>
  </React.StrictMode>
) 