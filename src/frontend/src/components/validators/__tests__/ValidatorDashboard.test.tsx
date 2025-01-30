import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ChakraProvider } from '@chakra-ui/react';
import ValidatorDashboard from '../ValidatorDashboard';
import { statsAPI } from '../../../api/stats';

// Mock the statsAPI
jest.mock('../../../api/stats');

const mockValidatorData = {
  validators: [
    {
      address: '0x1234567890abcdef',
      total_stake: '1000000',
      delegators: 100,
      status: 'active',
      uptime: 99.9,
      blocks_proposed: 1000,
      rewards_earned: '50000',
      commission_rate: 0.05,
      self_stake: '100000'
    },
    // Add more mock validators as needed
  ],
  total_stake: '5000000',
  active_count: 1
};

const mockValidatorStats = {
  total_validators: 100,
  active_validators: 95,
  total_staked: '10000000',
  average_uptime: 99.5,
  average_performance: 98.7
};

describe('ValidatorDashboard', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    // Reset all mocks before each test
    jest.clearAllMocks();

    // Setup API mock responses
    (statsAPI.getAllValidators as jest.Mock).mockResolvedValue(mockValidatorData);
    (statsAPI.getValidatorStats as jest.Mock).mockResolvedValue(mockValidatorStats);
  });

  const renderComponent = () => {
    return render(
      <ChakraProvider>
        <QueryClientProvider client={queryClient}>
          <ValidatorDashboard />
        </QueryClientProvider>
      </ChakraProvider>
    );
  };

  it('renders loading state initially', () => {
    renderComponent();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('renders validator data after loading', async () => {
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText('Total Validators')).toBeInTheDocument();
      expect(screen.getByText('100')).toBeInTheDocument(); // total validators
      expect(screen.getByText('Active: 95')).toBeInTheDocument();
    });
  });

  it('handles pagination correctly', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Total Validators')).toBeInTheDocument();
    });

    // Test page size change
    const pageSizeSelect = screen.getByRole('combobox');
    fireEvent.change(pageSizeSelect, { target: { value: '20' } });
    expect(pageSizeSelect).toHaveValue('20');

    // Test pagination buttons
    const nextButton = screen.getByText('Next');
    const prevButton = screen.getByText('Previous');
    
    expect(prevButton).toBeDisabled(); // First page
    fireEvent.click(nextButton);
    expect(prevButton).not.toBeDisabled();
  });

  it('handles error state correctly', async () => {
    // Mock API error
    (statsAPI.getAllValidators as jest.Mock).mockRejectedValue(new Error('Failed to fetch'));
    
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Failed to Load Validator Data')).toBeInTheDocument();
      expect(screen.getByText(/An error occurred/)).toBeInTheDocument();
    });

    // Test retry functionality
    const retryButton = screen.getByText('Retry');
    fireEvent.click(retryButton);
    expect(statsAPI.getAllValidators).toHaveBeenCalledTimes(2);
  });

  it('displays correct validator status colors', async () => {
    renderComponent();

    await waitFor(() => {
      const statusBadge = screen.getByText('active');
      expect(statusBadge).toHaveStyle({ backgroundColor: expect.stringContaining('green') });
    });
  });
}); 
