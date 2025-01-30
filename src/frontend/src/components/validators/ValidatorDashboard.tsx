import React, { useMemo, useState } from 'react';
import {
  Box,
  SimpleGrid,
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
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Spinner,
  Center,
  Button,
  Flex,
  Select,
  ButtonGroup,
  StatArrow,
  Link,
  IconButton,
} from '@chakra-ui/react';
import { FiExternalLink } from 'react-icons/fi';
import { useQuery } from '@tanstack/react-query';
import { statsAPI } from '../../api/stats';
import { Validator } from '../../api/stats';
import ErrorBoundary from '../common/ErrorBoundary';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
} from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const ValidatorDashboard: React.FC = () => {
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const {
    data: validators,
    isLoading: validatorsLoading,
    error: validatorsError,
    refetch: refetchValidators
  } = useQuery({
    queryKey: ['validators', page, pageSize],
    queryFn: () => statsAPI.getAllValidators(),
    refetchInterval: 30000,
    retry: 3,
    staleTime: 60000, // Data stays fresh for 1 minute
    gcTime: 300000, // Cache data for 5 minutes
  });

  const { 
    data: validatorStats, 
    isLoading: statsLoading,
    error: statsError,
    refetch: refetchStats 
  } = useQuery({
    queryKey: ['validator-stats'],
    queryFn: () => statsAPI.getValidatorStats(),
    refetchInterval: 30000,
    retry: 3,
    staleTime: 60000, // Data stays fresh for 1 minute
    gcTime: 300000, // Cache data for 5 minutes
  });

  const pieData = useMemo(() => {
    if (!validators?.validators) return [];
    return validators.validators
      .sort((a: Validator, b: Validator) => parseFloat(b.total_stake) - parseFloat(a.total_stake))
      .slice(0, 5)
      .map((validator: Validator) => ({
        name: validator.address.slice(0, 8) + '...',
        value: parseFloat(validator.total_stake)
      }));
  }, [validators?.validators]);

  const totalStake = useMemo(() => {
    if (!validators?.validators) return 0;
    return validators.validators.reduce(
      (sum: number, validator: Validator) => sum + parseFloat(validator.total_stake),
      0
    );
  }, [validators?.validators]);

  // Pagination controls
  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const handlePageSizeChange = (newSize: number) => {
    setPageSize(newSize);
    setPage(1); // Reset to first page when changing page size
  };

  // Memoized table data
  const paginatedValidators = useMemo(() => {
    if (!validators?.validators) return [];
    const startIndex = (page - 1) * pageSize;
    return validators.validators.slice(startIndex, startIndex + pageSize);
  }, [validators?.validators, page, pageSize]);

  if (validatorsLoading || statsLoading) {
    return (
      <Center h="50vh">
        <Spinner
          thickness="4px"
          speed="0.65s"
          emptyColor="gray.200"
          color="blue.500"
          size="xl"
        />
      </Center>
    );
  }

  if (validatorsError || statsError) {
    return (
      <Alert
        status="error"
        variant="subtle"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        textAlign="center"
        height="200px"
        borderRadius="md"
      >
        <AlertIcon boxSize="40px" mr={0} />
        <AlertTitle mt={4} mb={1} fontSize="lg">
          Failed to Load Validator Data
        </AlertTitle>
        <AlertDescription maxWidth="sm">
          An error occurred while fetching validator information. 
          Please try again later or contact support if the problem persists.
        </AlertDescription>
        <Button
          mt={4}
          onClick={() => {
            refetchValidators();
            refetchStats();
          }}
        >
          Retry
        </Button>
      </Alert>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'green';
      case 'jailed':
        return 'red';
      case 'inactive':
        return 'yellow';
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
                <StatLabel>Total Validators</StatLabel>
                <StatNumber>{validatorStats?.total_validators}</StatNumber>
                <StatHelpText>
                  Active: {validatorStats?.active_validators}
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={borderColor} borderWidth={1}>
            <CardBody>
              <Stat>
                <StatLabel>Total Staked</StatLabel>
                <StatNumber>
                  {parseFloat(validatorStats?.total_staked.toString() || '0').toFixed(2)}
                </StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  {((validatorStats?.active_validators || 0) / 
                    (validatorStats?.total_validators || 1) * 100).toFixed(1)}% Active
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={borderColor} borderWidth={1}>
            <CardBody>
              <Stat>
                <StatLabel>Average Uptime</StatLabel>
                <StatNumber>
                  {(validatorStats?.average_uptime || 0).toFixed(2)}%
                </StatNumber>
                <Progress
                  value={validatorStats?.average_uptime || 0}
                  colorScheme="green"
                  size="sm"
                  mt={2}
                />
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={borderColor} borderWidth={1}>
            <CardBody>
              <Stat>
                <StatLabel>Average Performance</StatLabel>
                <StatNumber>
                  {(validatorStats?.average_performance || 0).toFixed(2)}%
                </StatNumber>
                <Progress
                  value={validatorStats?.average_performance || 0}
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
              <Heading size="md" mb={4}>Stake Distribution</Heading>
              <Box height="300px">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      fill="#8884d8"
                      label
                    >
                      {pieData.map((_, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={borderColor} borderWidth={1}>
            <CardBody>
              <Heading size="md" mb={4}>Top Validators</Heading>
              <Box overflowX="auto">
                <Table variant="simple" size="sm">
                  <Thead>
                    <Tr>
                      <Th>Address</Th>
                      <Th isNumeric>Stake</Th>
                      <Th isNumeric>Delegators</Th>
                      <Th>Status</Th>
                      <Th></Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {paginatedValidators.map((validator) => (
                      <Tr key={validator.address}>
                        <Td>
                          <Text isTruncated maxW="150px">
                            {validator.address}
                          </Text>
                        </Td>
                        <Td isNumeric>
                          {parseFloat(validator.total_stake).toFixed(2)}
                          <Text as="span" fontSize="sm" color="gray.500" ml={1}>
                            ({((parseFloat(validator.total_stake) / totalStake) * 100).toFixed(1)}%)
                          </Text>
                        </Td>
                        <Td isNumeric>{validator.delegators}</Td>
                        <Td>
                          <Badge colorScheme={getStatusColor(validator.status)}>
                            {validator.status}
                          </Badge>
                        </Td>
                        <Td>
                          <Link href={`/validator/${validator.address}`} isExternal>
                            <IconButton
                              aria-label="View validator"
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
            </CardBody>
          </Card>
        </SimpleGrid>

        <Card bg={cardBg} borderColor={borderColor} borderWidth={1} mt={4}>
          <CardBody>
            <Flex justify="space-between" align="center" mb={4}>
              <Heading size="md">All Validators</Heading>
              <Text color="gray.500" fontSize="sm">
                Total Stake: {totalStake.toFixed(2)}
              </Text>
            </Flex>
            <Box overflowX="auto">
              <Table variant="simple" size="sm">
                <Thead>
                  <Tr>
                    <Th>Address</Th>
                    <Th isNumeric>Total Stake</Th>
                    <Th isNumeric>Self Stake</Th>
                    <Th isNumeric>Delegators</Th>
                    <Th isNumeric>Uptime</Th>
                    <Th isNumeric>Commission</Th>
                    <Th>Status</Th>
                    <Th></Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {validators?.validators.map((validator) => (
                    <Tr key={validator.address}>
                      <Td>
                        <Text isTruncated maxW="150px">
                          {validator.address}
                        </Text>
                      </Td>
                      <Td isNumeric>
                        {parseFloat(validator.total_stake).toFixed(2)}
                      </Td>
                      <Td isNumeric>
                        {parseFloat(validator.self_stake).toFixed(2)}
                      </Td>
                      <Td isNumeric>{validator.delegators}</Td>
                      <Td isNumeric>
                        {validator.uptime.toFixed(2)}%
                      </Td>
                      <Td isNumeric>
                        {(validator.commission_rate * 100).toFixed(1)}%
                      </Td>
                      <Td>
                        <Badge colorScheme={getStatusColor(validator.status)}>
                          {validator.status}
                        </Badge>
                      </Td>
                      <Td>
                        <Link href={`/validator/${validator.address}`} isExternal>
                          <IconButton
                            aria-label="View validator"
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
          </CardBody>
        </Card>

        <Card bg={cardBg} borderColor={borderColor} borderWidth={1}>
          <CardBody>
            <Heading size="md" mb={4}>Validators List</Heading>
            <Box overflowX="auto">
              <Table variant="simple" size="sm">
                <Thead>
                  <Tr>
                    <Th>Address</Th>
                    <Th isNumeric>Stake</Th>
                    <Th isNumeric>Delegators</Th>
                    <Th>Status</Th>
                    <Th></Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {paginatedValidators.map((validator) => (
                    <Tr key={validator.address}>
                      <Td>
                        <Text isTruncated maxW="150px">
                          {validator.address}
                        </Text>
                      </Td>
                      <Td isNumeric>
                        {parseFloat(validator.total_stake).toFixed(2)}
                      </Td>
                      <Td isNumeric>{validator.delegators}</Td>
                      <Td>
                        <Badge colorScheme={getStatusColor(validator.status)}>
                          {validator.status}
                        </Badge>
                      </Td>
                      <Td>
                        <Link href={`/validator/${validator.address}`} isExternal>
                          <IconButton
                            aria-label="View validator"
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
              
              <Flex justify="space-between" mt={4} align="center">
                <Select
                  w="100px"
                  value={pageSize}
                  onChange={(e) => handlePageSizeChange(Number(e.target.value))}
                >
                  <option value={5}>5</option>
                  <option value={10}>10</option>
                  <option value={20}>20</option>
                  <option value={50}>50</option>
                </Select>
                
                <ButtonGroup>
                  <Button
                    onClick={() => handlePageChange(page - 1)}
                    isDisabled={page === 1}
                  >
                    Previous
                  </Button>
                  <Button
                    onClick={() => handlePageChange(page + 1)}
                    isDisabled={paginatedValidators.length < pageSize}
                  >
                    Next
                  </Button>
                </ButtonGroup>
              </Flex>
            </Box>
          </CardBody>
        </Card>
      </Box>
    </ErrorBoundary>
  );
};

export default ValidatorDashboard; 