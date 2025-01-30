import React, { useEffect, useState, useCallback, useMemo } from 'react';
import {
  Box,
  Card,
  CardBody,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  Text,
  useColorModeValue,
  Link,
  Flex,
  IconButton,
  Tooltip,
  Select,
  HStack,
} from '@chakra-ui/react';
import { FiExternalLink, FiPause, FiPlay } from 'react-icons/fi';
import { useQuery } from '@tanstack/react-query';
import { statsAPI } from '../../api/stats';
import { Transaction } from '../../api/stats';
import ErrorBoundary from '../common/ErrorBoundary';
import LoadingSkeleton from '../common/LoadingSkeleton';
import { formatDistance } from 'date-fns';

const MAX_TRANSACTIONS = 50;

interface TransactionMonitorProps {
  initialFilter?: string;
}

const TransactionMonitor: React.FC<TransactionMonitorProps> = ({
  initialFilter = 'all'
}) => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isPaused, setIsPaused] = useState(false);
  const [filter, setFilter] = useState(initialFilter);
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const { data: txStats, isLoading } = useQuery({
    queryKey: ['transaction-stats'],
    queryFn: () => statsAPI.getTransactionStats(),
    refetchInterval: 10000
  });

  const addTransaction = useCallback((tx: Transaction) => {
    setTransactions(prev => {
      const newTxs = [tx, ...prev];
      if (newTxs.length > MAX_TRANSACTIONS) {
        newTxs.pop();
      }
      return newTxs;
    });
  }, []);

  useEffect(() => {
    if (isPaused) return;

    const unsubscribe = statsAPI.subscribeToUpdates(['transactions'], (update) => {
      if (update.type === 'new_transaction') {
        const tx = update.data as Transaction;
        if (filter === 'all' || tx.status === filter) {
          addTransaction(tx);
        }
      }
    });

    return () => unsubscribe();
  }, [addTransaction, filter, isPaused]);

  const filteredTransactions = useMemo(() => {
    return filter === 'all'
      ? transactions
      : transactions.filter(tx => tx.status === filter);
  }, [transactions, filter]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'green';
      case 'failed':
        return 'red';
      case 'pending':
        return 'yellow';
      default:
        return 'gray';
    }
  };

  if (isLoading) {
    return <LoadingSkeleton type="list" count={5} />;
  }

  return (
    <ErrorBoundary>
      <Card bg={cardBg} borderColor={borderColor} borderWidth={1}>
        <CardBody>
          <Flex justify="space-between" align="center" mb={4}>
            <Heading size="md">Live Transactions</Heading>
            <HStack spacing={4}>
              <Select
                size="sm"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                width="auto"
              >
                <option value="all">All Transactions</option>
                <option value="success">Successful</option>
                <option value="failed">Failed</option>
                <option value="pending">Pending</option>
              </Select>
              <Tooltip label={isPaused ? 'Resume monitoring' : 'Pause monitoring'}>
                <IconButton
                  aria-label="Toggle monitoring"
                  icon={isPaused ? <FiPlay /> : <FiPause />}
                  size="sm"
                  onClick={() => setIsPaused(!isPaused)}
                />
              </Tooltip>
            </HStack>
          </Flex>

          <Box overflowX="auto">
            <Table variant="simple" size="sm">
              <Thead>
                <Tr>
                  <Th>Hash</Th>
                  <Th>From</Th>
                  <Th>To</Th>
                  <Th isNumeric>Value</Th>
                  <Th>Status</Th>
                  <Th>Time</Th>
                  <Th></Th>
                </Tr>
              </Thead>
              <Tbody>
                {filteredTransactions.map((tx) => (
                  <Tr key={tx.hash}>
                    <Td>
                      <Text isTruncated maxW="150px">
                        {tx.hash}
                      </Text>
                    </Td>
                    <Td>
                      <Text isTruncated maxW="150px">
                        {tx.from_address}
                      </Text>
                    </Td>
                    <Td>
                      <Text isTruncated maxW="150px">
                        {tx.to_address}
                      </Text>
                    </Td>
                    <Td isNumeric>
                      {parseFloat(tx.value).toFixed(6)}
                    </Td>
                    <Td>
                      <Badge colorScheme={getStatusColor(tx.status)}>
                        {tx.status}
                      </Badge>
                    </Td>
                    <Td>
                      {formatDistance(new Date(tx.timestamp), new Date(), {
                        addSuffix: true,
                      })}
                    </Td>
                    <Td>
                      <Link
                        href={`/transaction/${tx.hash}`}
                        isExternal
                      >
                        <IconButton
                          aria-label="View transaction"
                          icon={<FiExternalLink />}
                          size="sm"
                          variant="ghost"
                        />
                      </Link>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </Box>

          {filteredTransactions.length === 0 && (
            <Text textAlign="center" mt={4} color="gray.500">
              No transactions to display
            </Text>
          )}

          <Flex justify="space-between" mt={4}>
            <Text fontSize="sm" color="gray.500">
              Showing last {filteredTransactions.length} of {MAX_TRANSACTIONS} transactions
            </Text>
            <Text fontSize="sm" color="gray.500">
              TPS: {txStats?.average_tps_24h.toFixed(2)} | 
              Peak: {txStats?.peak_tps_24h.toFixed(2)}
            </Text>
          </Flex>
        </CardBody>
      </Card>
    </ErrorBoundary>
  );
};

export default TransactionMonitor; 