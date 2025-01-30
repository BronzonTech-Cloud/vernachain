import React, { useMemo } from 'react';
import {
  Box,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Progress,
  Badge,
  useColorModeValue,
  Card,
  CardBody,
  Heading,
  Tooltip,
  Icon,
} from '@chakra-ui/react';
import { FiActivity, FiCpu, FiHardDrive, FiWifi } from 'react-icons/fi';
import { useQuery } from '@tanstack/react-query';
import { statsAPI } from '../../api/stats';
import LoadingSkeleton from '../common/LoadingSkeleton';
import ErrorBoundary from '../common/ErrorBoundary';

const NetworkStatus: React.FC = () => {
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const { data: health, isLoading: healthLoading } = useQuery({
    queryKey: ['network-health'],
    queryFn: () => statsAPI.getNetworkHealth(),
    refetchInterval: 10000
  });

  const { data: resources, isLoading: resourcesLoading } = useQuery({
    queryKey: ['resource-usage'],
    queryFn: () => statsAPI.getResourceUsage(),
    refetchInterval: 30000
  });

  const { data: networkStats, isLoading: statsLoading } = useQuery({
    queryKey: ['network-analytics'],
    queryFn: () => statsAPI.getNetworkAnalytics(),
    refetchInterval: 15000
  });

  const healthStatus = useMemo(() => {
    if (!health) return 'unknown';
    const score = (
      health.block_time_health +
      health.validator_health +
      health.transaction_health +
      health.node_health
    ) / 4;
    return score > 0.8 ? 'healthy' : score > 0.5 ? 'degraded' : 'unhealthy';
  }, [health]);

  const healthColor = useMemo(() => {
    switch (healthStatus) {
      case 'healthy':
        return 'green';
      case 'degraded':
        return 'yellow';
      case 'unhealthy':
        return 'red';
      default:
        return 'gray';
    }
  }, [healthStatus]);

  if (healthLoading || resourcesLoading || statsLoading) {
    return <LoadingSkeleton type="detail" />;
  }

  return (
    <ErrorBoundary>
      <Box>
        <Card bg={cardBg} mb={4} borderColor={borderColor} borderWidth={1}>
          <CardBody>
            <Heading size="md" mb={4}>Network Health</Heading>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={4}>
              <Stat>
                <StatLabel>Block Time Health</StatLabel>
                <Progress
                  value={health?.block_time_health ? health.block_time_health * 100 : 0}
                  colorScheme={healthColor}
                  size="lg"
                  mb={2}
                />
                <StatHelpText>
                  <Badge colorScheme={healthColor}>
                    {(health?.block_time_health || 0).toFixed(2)}
                  </Badge>
                </StatHelpText>
              </Stat>

              <Stat>
                <StatLabel>Validator Health</StatLabel>
                <Progress
                  value={health?.validator_health ? health.validator_health * 100 : 0}
                  colorScheme={healthColor}
                  size="lg"
                  mb={2}
                />
                <StatHelpText>
                  <Badge colorScheme={healthColor}>
                    {(health?.validator_health || 0).toFixed(2)}
                  </Badge>
                </StatHelpText>
              </Stat>

              <Stat>
                <StatLabel>Transaction Health</StatLabel>
                <Progress
                  value={health?.transaction_health ? health.transaction_health * 100 : 0}
                  colorScheme={healthColor}
                  size="lg"
                  mb={2}
                />
                <StatHelpText>
                  <Badge colorScheme={healthColor}>
                    {(health?.transaction_health || 0).toFixed(2)}
                  </Badge>
                </StatHelpText>
              </Stat>

              <Stat>
                <StatLabel>Node Health</StatLabel>
                <Progress
                  value={health?.node_health ? health.node_health * 100 : 0}
                  colorScheme={healthColor}
                  size="lg"
                  mb={2}
                />
                <StatHelpText>
                  <Badge colorScheme={healthColor}>
                    {(health?.node_health || 0).toFixed(2)}
                  </Badge>
                </StatHelpText>
              </Stat>
            </SimpleGrid>
          </CardBody>
        </Card>

        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
          <Card bg={cardBg} borderColor={borderColor} borderWidth={1}>
            <CardBody>
              <Heading size="md" mb={4}>Resource Usage</Heading>
              <SimpleGrid columns={2} spacing={4}>
                <Tooltip label="Memory Usage">
                  <Stat>
                    <StatLabel>
                      <Icon as={FiHardDrive} mr={2} />
                      Memory
                    </StatLabel>
                    <StatNumber>
                      {(resources?.memory_usage ?? 0).toFixed(1)}%
                    </StatNumber>
                    <Progress
                      value={resources?.memory_usage ?? 0}
                      colorScheme={(resources?.memory_usage ?? 0) > 80 ? 'red' : 'blue'}
                      size="sm"
                    />
                  </Stat>
                </Tooltip>

                <Tooltip label="CPU Usage">
                  <Stat>
                    <StatLabel>
                      <Icon as={FiCpu} mr={2} />
                      CPU
                    </StatLabel>
                    <StatNumber>
                      {(resources?.cpu_usage ?? 0).toFixed(1)}%
                    </StatNumber>
                    <Progress
                      value={resources?.cpu_usage ?? 0}
                      colorScheme={(resources?.cpu_usage ?? 0) > 80 ? 'red' : 'blue'}
                      size="sm"
                    />
                  </Stat>
                </Tooltip>

                <Tooltip label="Disk Usage">
                  <Stat>
                    <StatLabel>
                      <Icon as={FiHardDrive} mr={2} />
                      Disk
                    </StatLabel>
                    <StatNumber>
                      {(resources?.disk_usage ?? 0).toFixed(1)}%
                    </StatNumber>
                    <Progress
                      value={resources?.disk_usage ?? 0}
                      colorScheme={(resources?.disk_usage ?? 0) > 80 ? 'red' : 'blue'}
                      size="sm"
                    />
                  </Stat>
                </Tooltip>

                <Tooltip label="Bandwidth Usage">
                  <Stat>
                    <StatLabel>
                      <Icon as={FiWifi} mr={2} />
                      Bandwidth
                    </StatLabel>
                    <StatNumber>
                      {((resources?.bandwidth_usage ?? 0) / 1024 / 1024).toFixed(1)} MB/s
                    </StatNumber>
                    <Progress
                      value={((resources?.bandwidth_usage ?? 0) / 1024 / 1024 / 10) * 100}
                      colorScheme="blue"
                      size="sm"
                    />
                  </Stat>
                </Tooltip>
              </SimpleGrid>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={borderColor} borderWidth={1}>
            <CardBody>
              <Heading size="md" mb={4}>Network Metrics</Heading>
              <SimpleGrid columns={2} spacing={4}>
                <Tooltip label="Network Latency">
                  <Stat>
                    <StatLabel>
                      <Icon as={FiActivity} mr={2} />
                      Latency
                    </StatLabel>
                    <StatNumber>
                      {(networkStats?.network_latency ?? 0).toFixed(2)}ms
                    </StatNumber>
                    <StatHelpText>
                      Average network delay
                    </StatHelpText>
                  </Stat>
                </Tooltip>

                <Tooltip label="Connected Peers">
                  <Stat>
                    <StatLabel>Peers</StatLabel>
                    <StatNumber>
                      {resources?.peer_count}
                    </StatNumber>
                    <StatHelpText>
                      Active connections
                    </StatHelpText>
                  </Stat>
                </Tooltip>

                <Tooltip label="Node Distribution">
                  <Stat>
                    <StatLabel>Nodes</StatLabel>
                    <StatNumber>
                      {resources?.node_count}
                    </StatNumber>
                    <StatHelpText>
                      Active nodes
                    </StatHelpText>
                  </Stat>
                </Tooltip>

                <Tooltip label="Average Peer Count">
                  <Stat>
                    <StatLabel>Avg Peers</StatLabel>
                    <StatNumber>
                      {networkStats?.peer_count_average.toFixed(1)}
                    </StatNumber>
                    <StatHelpText>
                      Per node
                    </StatHelpText>
                  </Stat>
                </Tooltip>
              </SimpleGrid>
            </CardBody>
          </Card>
        </SimpleGrid>
      </Box>
    </ErrorBoundary>
  );
};

export default NetworkStatus; 