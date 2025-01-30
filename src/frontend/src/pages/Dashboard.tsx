import { FC } from 'react';
import {
  Box,
  Grid,
  Heading,
  SimpleGrid,
  useColorModeValue,
  VStack,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Flex,
  Text,
} from '@chakra-ui/react';
import { useQuery } from '@tanstack/react-query';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { FiClock, FiActivity, FiBox, FiUsers, FiLayers } from 'react-icons/fi';
import StatCard from '../components/common/StatCard';
import DataCard from '../components/common/DataCard';
import StatusBadge from '../components/common/StatusBadge';
import SearchBar from '../components/common/SearchBar';
import { formatDistance } from 'date-fns';

interface NetworkStats {
  network: {
    blocks: number;
    transactions: number;
    validators: number;
    shards: number;
    tps: number;
    peak_tps: number;
    block_time: number;
  };
  status: {
    version: string;
    uptime: number;
    sync_status: 'synced' | 'syncing' | 'error';
    peers: number;
  };
  market_data: {
    price: number;
    price_change_24h: number;
    market_cap: number;
    volume_24h: number;
  };
  recent_transactions: Array<{
    hash: string;
    type: string;
    amount: string;
    timestamp: string;
    status: 'success' | 'pending' | 'error';
  }>;
  chart_data: {
    transactions: Array<{ timestamp: string; value: number }>;
    tps: Array<{ timestamp: string; value: number }>;
  };
}

const Dashboard: FC = () => {
  const { data: stats, isLoading } = useQuery<NetworkStats>({
    queryKey: ['networkStats'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8001/api/stats');
      if (!response.ok) throw new Error('Network response was not ok');
      return response.json();
    },
    refetchInterval: 5000,
  });

  const cardBg = useColorModeValue('white', 'gray.800');
  const textColor = useColorModeValue('gray.600', 'gray.400');

  return (
    <Box>
      <Flex justify="space-between" align="center" mb={6}>
        <Heading>Network Overview</Heading>
        <Box maxW="300px" w="100%" bg={cardBg} borderRadius="md">
          <SearchBar />
        </Box>
      </Flex>

      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={4} mb={8}>
        <StatCard
          label="Total Blocks"
          value={stats?.network.blocks ?? 0}
          icon={FiBox}
          helpText={`${stats?.network.block_time ?? 0}s block time`}
          isLoading={isLoading}
          bg={cardBg}
        />
        <StatCard
          label="Transactions"
          value={stats?.network.transactions ?? 0}
          icon={FiActivity}
          helpText={`${stats?.network.tps ?? 0} TPS`}
          change={stats?.network.peak_tps}
          isLoading={isLoading}
          bg={cardBg}
        />
        <StatCard
          label="Active Validators"
          value={stats?.network.validators ?? 0}
          icon={FiUsers}
          helpText={`${stats?.status.peers ?? 0} connected peers`}
          isLoading={isLoading}
          bg={cardBg}
        />
        <StatCard
          label="Active Shards"
          value={stats?.network.shards ?? 0}
          icon={FiLayers}
          helpText="Network shards"
          isLoading={isLoading}
          bg={cardBg}
        />
      </SimpleGrid>

      <Grid templateColumns={{ base: '1fr', lg: '2fr 1fr' }} gap={8} mb={8}>
        <DataCard
          title="Transaction History"
          isLoading={isLoading}
          showRefresh
        >
          <Box h="300px">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={stats?.chart_data.transactions}
                margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
              >
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                />
                <YAxis />
                <Tooltip
                  labelFormatter={(value) => new Date(value).toLocaleString()}
                />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#3182ce"
                  fill="#3182ce"
                  fillOpacity={0.2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </Box>
        </DataCard>

        <DataCard
          title="Network Status"
          isLoading={isLoading}
        >
          <VStack spacing={4} align="stretch">
            <Flex justify="space-between">
              <Text color={textColor}>Version:</Text>
              <Text>{stats?.status.version}</Text>
            </Flex>
            <Flex justify="space-between">
              <Text color={textColor}>Status:</Text>
              <StatusBadge 
                status={stats?.status.sync_status === 'synced' ? 'success' : 
                        stats?.status.sync_status === 'syncing' ? 'pending' : 'error'} 
              />
            </Flex>
            <Flex justify="space-between">
              <Text color={textColor}>Uptime:</Text>
              <Text>{formatDistance(0, (stats?.status.uptime ?? 0) * 1000)}</Text>
            </Flex>
            <Flex justify="space-between">
              <Text color={textColor}>Connected Peers:</Text>
              <Text>{stats?.status.peers}</Text>
            </Flex>
          </VStack>
        </DataCard>
      </Grid>

      <Grid templateColumns={{ base: '1fr', lg: '2fr 1fr' }} gap={8}>
        <DataCard
          title="Recent Transactions"
          isLoading={isLoading}
        >
          <Table variant="simple" size="sm">
            <Thead>
              <Tr>
                <Th>Hash</Th>
                <Th>Type</Th>
                <Th>Amount</Th>
                <Th>Time</Th>
                <Th>Status</Th>
              </Tr>
            </Thead>
            <Tbody>
              {stats?.recent_transactions.map((tx) => (
                <Tr key={tx.hash}>
                  <Td>{tx.hash}</Td>
                  <Td>{tx.type}</Td>
                  <Td>{tx.amount}</Td>
                  <Td>
                    <Flex align="center" gap={2}>
                      <FiClock />
                      <Text>
                        {formatDistance(new Date(tx.timestamp), new Date(), { addSuffix: true })}
                      </Text>
                    </Flex>
                  </Td>
                  <Td>
                    <StatusBadge status={tx.status} />
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </DataCard>

        <VStack spacing={4}>
          <DataCard
            title="Market Overview"
            isLoading={isLoading}
          >
            <VStack spacing={4} align="stretch">
              <StatCard
                label="Price"
                value={`$${stats?.market_data.price.toFixed(2) ?? 0}`}
                change={stats?.market_data.price_change_24h}
                helpText="24h change"
                isLoading={isLoading}
                bg={cardBg}
              />
              <StatCard
                label="Market Cap"
                value={`$${((stats?.market_data.market_cap ?? 0) / 1e9).toFixed(2)}B`}
                helpText="Total market capitalization"
                isLoading={isLoading}
                bg={cardBg}
              />
              <StatCard
                label="24h Volume"
                value={`$${((stats?.market_data.volume_24h ?? 0) / 1e6).toFixed(2)}M`}
                helpText="Trading volume"
                isLoading={isLoading}
                bg={cardBg}
              />
            </VStack>
          </DataCard>

          <DataCard
            title="Network TPS"
            isLoading={isLoading}
          >
            <Box h="200px">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={stats?.chart_data.tps}
                  margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
                >
                  <XAxis
                    dataKey="timestamp"
                    tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                  />
                  <YAxis />
                  <Tooltip
                    labelFormatter={(value) => new Date(value).toLocaleString()}
                  />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#38a169"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </DataCard>
        </VStack>
      </Grid>
    </Box>
  );
};

export default Dashboard;