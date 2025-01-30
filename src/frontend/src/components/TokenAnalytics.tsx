import React from 'react';
import {
  Box,
  Card,
  CardBody,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  SimpleGrid,
  Heading,
  useColorModeValue,
} from '@chakra-ui/react';
import { useQuery } from '@tanstack/react-query';
import {
  LineChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts';

interface TokenAnalyticsProps {
  tokenId: string;
}

interface PriceData {
  price_usd: number;
  market_cap: number;
  volume_24h: number;
  price_change_24h: number;
  holders_count: number;
  transactions_count: number;
}

const TokenAnalytics: React.FC<TokenAnalyticsProps> = ({ tokenId }) => {
  const cardBg = useColorModeValue('white', 'gray.800');
  
  const { data: analytics, isLoading } = useQuery<PriceData>({
    queryKey: ['token-analytics', tokenId],
    queryFn: async () => {
      const response = await fetch(`http://localhost:8001/api/v1/tokens/${tokenId}/analytics`);
      if (!response.ok) throw new Error('Failed to fetch token analytics');
      return response.json();
    },
    refetchInterval: 30000 // Refresh every 30 seconds
  });
  
  if (isLoading || !analytics) {
    return <Box>Loading analytics...</Box>;
  }
  
  return (
    <Box>
      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
        <Card bg={cardBg}>
          <CardBody>
            <Heading size="md" mb={4}>Price Information</Heading>
            <SimpleGrid columns={2} spacing={4}>
              <Stat>
                <StatLabel>Price (USD)</StatLabel>
                <StatNumber>${analytics.price_usd.toFixed(4)}</StatNumber>
                <StatHelpText>
                  <StatArrow 
                    type={analytics.price_change_24h >= 0 ? 'increase' : 'decrease'} 
                  />
                  {Math.abs(analytics.price_change_24h).toFixed(2)}%
                </StatHelpText>
              </Stat>
              <Stat>
                <StatLabel>Market Cap</StatLabel>
                <StatNumber>
                  ${(analytics.market_cap / 1e6).toFixed(2)}M
                </StatNumber>
                <StatHelpText>Total Value Locked</StatHelpText>
              </Stat>
            </SimpleGrid>
          </CardBody>
        </Card>

        <Card bg={cardBg}>
          <CardBody>
            <Heading size="md" mb={4}>Trading Activity</Heading>
            <SimpleGrid columns={2} spacing={4}>
              <Stat>
                <StatLabel>24h Volume</StatLabel>
                <StatNumber>
                  ${(analytics.volume_24h / 1e6).toFixed(2)}M
                </StatNumber>
                <StatHelpText>Trading Volume</StatHelpText>
              </Stat>
              <Stat>
                <StatLabel>Transactions</StatLabel>
                <StatNumber>{analytics.transactions_count}</StatNumber>
                <StatHelpText>{analytics.holders_count} holders</StatHelpText>
              </Stat>
            </SimpleGrid>
          </CardBody>
        </Card>
      </SimpleGrid>

      <Card bg={cardBg} mt={4}>
        <CardBody>
          <Heading size="md" mb={4}>Price History</Heading>
          <Box h="300px">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={[/* Price history data */]}>
                <XAxis dataKey="timestamp" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="price" 
                  stroke="#4299E1" 
                  strokeWidth={2} 
                />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        </CardBody>
      </Card>
    </Box>
  );
}

export default TokenAnalytics; 