import { FC } from 'react';
import {
  Box,
  Grid,
  Heading,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Card,
  CardBody,
  SimpleGrid,
  useColorModeValue,
  Input,
  InputGroup,
  InputLeftElement,
  VStack,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  Flex,
  Text,
} from '@chakra-ui/react';
import { useQuery } from '@tanstack/react-query';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { FiSearch, FiClock } from 'react-icons/fi';
import { fetchNetworkStats, NetworkStats } from '../api/stats';

interface StatCardProps {
  label: string;
  value: string | number;
  helpText?: string;
  change?: number;
}

const StatCard: FC<StatCardProps> = ({ label, value, helpText, change }) => (
  <Card>
    <CardBody>
      <Stat>
        <StatLabel>{label}</StatLabel>
        <StatNumber>{value}</StatNumber>
        {helpText && <StatHelpText>{helpText}</StatHelpText>}
        {change !== undefined && (
          <StatHelpText color={change >= 0 ? 'green.500' : 'red.500'}>
            {change >= 0 ? '↑' : '↓'} {Math.abs(change)}%
          </StatHelpText>
        )}
      </Stat>
    </CardBody>
  </Card>
);

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

const Dashboard: FC = () => {
  const { data: stats, isLoading } = useQuery<NetworkStats>({
    queryKey: ['networkStats'],
    queryFn: fetchNetworkStats
  });
  const chartColor = useColorModeValue('brand.500', 'brand.200');

  // Mock data for charts
  const transactionData = [
    { time: '00:00', value: 150 },
    { time: '04:00', value: 200 },
    { time: '08:00', value: 350 },
    { time: '12:00', value: 400 },
    { time: '16:00', value: 500 },
    { time: '20:00', value: 450 },
    { time: '24:00', value: 300 },
  ];

  const validatorDistribution = [
    { name: 'Staked', value: 65 },
    { name: 'Delegated', value: 25 },
    { name: 'Unbonding', value: 10 },
  ];

  const recentTransactions = [
    { hash: '0x1234...5678', type: 'Transfer', amount: '100', time: '2 mins ago', status: 'success' },
    { hash: '0x8765...4321', type: 'Contract', amount: '50', time: '5 mins ago', status: 'pending' },
    { hash: '0x9876...1234', type: 'Stake', amount: '1000', time: '10 mins ago', status: 'success' },
  ];

  if (isLoading) {
    return <Box>Loading...</Box>;
  }

  return (
    <Box>
      <Flex justify="space-between" align="center" mb={6}>
        <Heading>Network Overview</Heading>
        <InputGroup maxW="300px">
          <InputLeftElement pointerEvents="none">
            <FiSearch />
          </InputLeftElement>
          <Input placeholder="Search tx, block, or address" />
        </InputGroup>
      </Flex>

      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={4} mb={8}>
        <StatCard
          label="Total Transactions"
          value={stats?.total_transactions.toLocaleString() || 0}
          change={2.5}
        />
        <StatCard
          label="Total Blocks"
          value={stats?.total_blocks.toLocaleString() || 0}
          change={1.8}
        />
        <StatCard
          label="Active Validators"
          value={stats?.active_validators || 0}
          change={-0.5}
        />
        <StatCard
          label="TPS"
          value={stats?.tps || 0}
          helpText="Transactions per second"
          change={3.2}
        />
      </SimpleGrid>

      <Grid templateColumns={{ base: '1fr', lg: '2fr 1fr' }} gap={8} mb={8}>
        <Card>
          <CardBody>
            <Heading size="md" mb={4}>Transaction History</Heading>
            <Box h="300px">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={transactionData}>
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke={chartColor}
                    fill={chartColor}
                    fillOpacity={0.2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </Box>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <Heading size="md" mb={4}>Validator Distribution</Heading>
            <Box h="300px">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={validatorDistribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    fill="#8884d8"
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {validatorDistribution.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </CardBody>
        </Card>
      </Grid>

      <Grid templateColumns={{ base: '1fr', lg: '2fr 1fr' }} gap={8}>
        <Card>
          <CardBody>
            <Heading size="md" mb={4}>Recent Transactions</Heading>
            <Table variant="simple">
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
                {recentTransactions.map((tx) => (
                  <Tr key={tx.hash}>
                    <Td>{tx.hash}</Td>
                    <Td>{tx.type}</Td>
                    <Td>{tx.amount}</Td>
                    <Td>
                      <Flex align="center" gap={2}>
                        <FiClock />
                        <Text>{tx.time}</Text>
                      </Flex>
                    </Td>
                    <Td>
                      <Badge
                        colorScheme={tx.status === 'success' ? 'green' : 'yellow'}
                      >
                        {tx.status}
                      </Badge>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <Heading size="md" mb={4}>Market Data</Heading>
            <VStack spacing={4} align="stretch">
              <StatCard
                label="Price"
                value={`$${stats?.market_data?.price?.toFixed(2) ?? 0}`}
                change={1.2}
              />
              <StatCard
                label="Market Cap"
                value={`$${((stats?.market_data?.market_cap ?? 0) / 1e9).toFixed(2)}B`}
                change={-0.8}
              />
              <StatCard
                label="24h Volume"
                value={`$${((stats?.market_data?.volume_24h ?? 0) / 1e6).toFixed(2)}M`}
                change={2.5}
              />
            </VStack>
          </CardBody>
        </Card>
      </Grid>
    </Box>
  );
};

export default Dashboard; 