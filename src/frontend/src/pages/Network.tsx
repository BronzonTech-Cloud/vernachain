import React from 'react';
import { VStack } from '@chakra-ui/react';
import NetworkStatus from '../components/network/NetworkStatus';

const Network: React.FC = () => {
  return (
    <VStack spacing={6} align="stretch">
      <NetworkStatus />
    </VStack>
  );
};

export default Network;