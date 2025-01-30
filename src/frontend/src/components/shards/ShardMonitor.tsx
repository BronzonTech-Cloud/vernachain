import React, { useMemo } from 'react';
import {
  Box,
  SimpleGrid,
  Card,
  CardBody,
  Heading,
  useColorModeValue,
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
} from '@chakra-ui/react';
import { useQuery } from '@tanstack/react-query';
import { statsAPI } from '../../api/stats';
import ErrorBoundary from '../common/ErrorBoundary';
import LoadingSkeleton from '../common/LoadingSkeleton';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';

const ShardMonitor: React.FC = () => {
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const { data: shardAnalytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['shard-analytics'],
    queryFn: () => statsAPI.getShardAnalyticsCached(),
    refetchInterval: 30000
  });

  const { isLoading: statsLoading } = useQuery({
    queryKey: ['network-stats'],
    queryFn: () => statsAPI.getNetworkStats(),
    refetchInterval: 30000
  });

  const shardSizeData = useMemo(() => {
    if (!shardAnalytics?.shard_sizes) return [];
    return shardAnalytics.shard_sizes.map((size, index) => ({
      name: `Shard ${index}`,
      size
    }));
  }, [shardAnalytics]);

  const shardTpsData = useMemo(() => {
    if (!shardAnalytics?.shard_tps) return [];
    return shardAnalytics.shard_tps.map((tps, index) => ({
      name: `Shard ${index}`,
      tps
    }));
  }, [shardAnalytics]);

  if (analyticsLoading || statsLoading) {
    return <LoadingSkeleton type="detail" />;
  }

  const getShardHealth = (tps: number) => {
    if (tps > 100) return 'excellent';
    if (tps > 50) return 'good';
    if (tps > 20) return 'fair';
    return 'poor';
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'excellent':
        return 'green';
      case 'good':
        return 'blue';
      case 'fair':
        return 'yellow';
      case 'poor':
        return 'red';
      default:
        return 'gray';
    }
  };

  return (
    <ErrorBoundary>
      <Box>
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={4} mb={4}>
          <Card bg={cardBg} borderColor={borderColor} borderWidth={1}>
            <CardBody>
              <Stat>
                <StatLabel>Total Shards</StatLabel>
                <StatNumber>{shardAnalytics?.total_shards ?? 0}</StatNumber>
                <StatHelpText>
                  Active: {shardAnalytics?.active_shards ?? 0}
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={borderColor} borderWidth={1}>
            <CardBody>
              <Stat>
                <StatLabel>Cross-Shard TXs (24h)</StatLabel>
                <StatNumber>
                  {shardAnalytics?.cross_shard_txs_24h.toLocaleString()}
                </StatNumber>
                <StatHelpText>
                  Transactions between shards
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={borderColor} borderWidth={1}>
            <CardBody>
              <Stat>
                <StatLabel>Average TPS</StatLabel>
                <StatNumber>
                  {((shardAnalytics?.shard_tps?.reduce((a, b) => a + b, 0) ?? 0) / 
                    (shardAnalytics?.total_shards ?? 1)).toFixed(1)}
                </StatNumber>
                <StatHelpText>
                  Per shard
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={borderColor} borderWidth={1}>
            <CardBody>
              <Stat>
                <StatLabel>Network Load</StatLabel>
                <StatNumber>
                  {((shardAnalytics?.active_shards || 0) / 
                    (shardAnalytics?.total_shards || 1) * 100).toFixed(1)}%
                </StatNumber>
                <Progress
                  value={(shardAnalytics?.active_shards || 0) / 
                    (shardAnalytics?.total_shards || 1) * 100}
                  colorScheme="blue"
                  size="sm"
                  mt={2}
                />
              </Stat>
            </CardBody>
          </Card>
        </SimpleGrid>

        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={4}>
          <Card bg={cardBg} borderColor={borderColor} borderWidth={1}>
            <CardBody>
              <Heading size="md" mb={4}>Shard Sizes</Heading>
              <Box height="300px">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={shardSizeData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="size" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={borderColor} borderWidth={1}>
            <CardBody>
              <Heading size="md" mb={4}>Shard TPS</Heading>
              <Box height="300px">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={shardTpsData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="tps"
                      stroke="#82ca9d"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardBody>
          </Card>
        </SimpleGrid>

        <Card bg={cardBg} borderColor={borderColor} borderWidth={1} mt={4}>
          <CardBody>
            <Heading size="md" mb={4}>Shard Details</Heading>
            <Box overflowX="auto">
              <Table variant="simple" size="sm">
                <Thead>
                  <Tr>
                    <Th>Shard ID</Th>
                    <Th isNumeric>Size</Th>
                    <Th isNumeric>TPS</Th>
                    <Th>Health</Th>
                    <Th isNumeric>Cross-Shard TXs</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {shardAnalytics?.shard_sizes.map((size, index) => {
                    const tps = shardAnalytics.shard_tps[index];
                    const health = getShardHealth(tps);
                    return (
                      <Tr key={index}>
                        <Td>Shard {index}</Td>
                        <Td isNumeric>{size.toLocaleString()}</Td>
                        <Td isNumeric>{tps.toFixed(1)}</Td>
                        <Td>
                          <Badge colorScheme={getHealthColor(health)}>
                            {health}
                          </Badge>
                        </Td>
                        <Td isNumeric>
                          {Math.floor(shardAnalytics.cross_shard_txs_24h / 
                            shardAnalytics.total_shards).toLocaleString()}
                        </Td>
                      </Tr>
                    );
                  })}
                </Tbody>
              </Table>
            </Box>
          </CardBody>
        </Card>
      </Box>
    </ErrorBoundary>
  );
};

export default ShardMonitor; 