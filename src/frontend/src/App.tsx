import React from 'react';
import { ChakraProvider, CSSReset, Box } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { theme } from './theme';

// Layout
import Layout from './components/Layout';

// Pages
import Dashboard from './pages/Dashboard';
import Blocks from './pages/Blocks';
import Transactions from './pages/Transactions';
import Validators from './pages/Validators';
import Contracts from './pages/Contracts';
import Wallet from './pages/Wallet';
import Bridge from './pages/Bridge';
import APIDocs from './pages/APIDocs';
import MintingPlatform from './pages/MintingPlatform';
import TokenDetails from './pages/TokenDetails';

// Initialize React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5000,
    },
  },
});

// Add debugging
console.log('Rendering App component');

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ChakraProvider theme={theme}>
        <CSSReset />
        <Router>
          <Layout>
            <Box>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/blocks" element={<Blocks />} />
                <Route path="/transactions" element={<Transactions />} />
                <Route path="/validators" element={<Validators />} />
                <Route path="/wallet" element={<Wallet />} />
                <Route path="/contracts" element={<Contracts />} />
                <Route path="/bridge" element={<Bridge />} />
                <Route path="/api-docs" element={<APIDocs />} />
                <Route path="/minting" element={<MintingPlatform />} />
                <Route path="/tokens/:tokenId" element={<TokenDetails />} />
              </Routes>
            </Box>
          </Layout>
        </Router>
      </ChakraProvider>
    </QueryClientProvider>
  );
}

export default App; 