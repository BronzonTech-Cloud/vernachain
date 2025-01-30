import React from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Container,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Heading,
  Text,
  VStack,
  useColorModeValue
} from '@chakra-ui/react';
import { useQuery } from '@tanstack/react-query';
import TokenAnalytics from '../components/TokenAnalytics';
import TokenGovernance from '../components/TokenGovernance';
import TokenSwap from '../components/TokenSwap';
import TokenVesting from '../components/TokenVesting';

interface TokenDetails {
  id: string;
  name: string;
  symbol: string;
  description: string;
  total_supply: string;
  circulating_supply: string;
  owner_address: string;
}

const TokenDetails: React.FC = () => {
  const { tokenId } = useParams<{ tokenId: string }>();
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  
  const { data: token, isLoading } = useQuery<TokenDetails>({
    queryKey: ['token', tokenId],
    queryFn: async () => {
      const response = await fetch(`http://localhost:8001/api/v1/tokens/${tokenId}`);
      if (!response.ok) throw new Error('Failed to fetch token details');
      return response.json();
    },
    enabled: Boolean(tokenId)
  });
  
  if (isLoading || !token) {
    return <Box>Loading token details...</Box>;
  }
  
  return (
    <Box bg={bgColor} minH="100vh" py={8}>
      <Container maxW="container.xl">
        <VStack align="stretch" spacing={6}>
          <Box>
            <Heading size="lg">{token.name} ({token.symbol})</Heading>
            <Text mt={2} color="gray.500">{token.description}</Text>
          </Box>
          
          <TokenAnalytics tokenId={token.id} />
          
          <Tabs variant="enclosed" colorScheme="blue">
            <TabList>
              <Tab>Swap</Tab>
              <Tab>Governance</Tab>
              <Tab>Vesting</Tab>
            </TabList>
            
            <TabPanels>
              <TabPanel>
                <TokenSwap tokenId={token.id} />
              </TabPanel>
              
              <TabPanel>
                <TokenGovernance tokenId={token.id} />
              </TabPanel>
              
              <TabPanel>
                <TokenVesting tokenId={token.id} />
              </TabPanel>
            </TabPanels>
          </Tabs>
        </VStack>
      </Container>
    </Box>
  );
}

export default TokenDetails; 