import React from 'react';
import { VStack } from '@chakra-ui/react';
import ShardMonitor from '../components/shards/ShardMonitor';

const Shards: React.FC = () => {
  return (
    <VStack spacing={6} align="stretch">
      <ShardMonitor />
    </VStack>
  );
};

export default Shards;