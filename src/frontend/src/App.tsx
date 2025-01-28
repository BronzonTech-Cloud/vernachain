import { ChakraProvider, CSSReset } from '@chakra-ui/react';
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
import Bridge from './pages/Bridge';
import APIDocs from './pages/APIDocs';

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

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ChakraProvider theme={theme}>
        <CSSReset />
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/blocks" element={<Blocks />} />
              <Route path="/transactions" element={<Transactions />} />
              <Route path="/validators" element={<Validators />} />
              <Route path="/contracts" element={<Contracts />} />
              <Route path="/bridge" element={<Bridge />} />
              <Route path="/api-docs" element={<APIDocs />} />
            </Routes>
          </Layout>
        </Router>
      </ChakraProvider>
    </QueryClientProvider>
  );
}

export default App; 