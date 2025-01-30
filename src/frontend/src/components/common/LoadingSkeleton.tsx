import React from 'react';
import { Box, Skeleton, SkeletonText, SimpleGrid } from '@chakra-ui/react';

interface LoadingSkeletonProps {
  type?: 'card' | 'list' | 'detail';
  count?: number;
  columns?: number;
}

const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  type = 'card',
  count = 1,
  columns = 1
}) => {
  const renderSkeleton = () => {
    switch (type) {
      case 'card':
        return (
          <Box
            padding="6"
            boxShadow="lg"
            bg="white"
            borderRadius="md"
            width="100%"
          >
            <Skeleton height="40px" width="40%" mb={4} />
            <SkeletonText mt="4" noOfLines={4} spacing="4" skeletonHeight="2" />
            <Skeleton height="100px" mt={6} />
          </Box>
        );
      
      case 'list':
        return (
          <Box padding="4" bg="white" borderRadius="md" width="100%">
            <Skeleton height="20px" mb={2} />
            <SkeletonText mt="2" noOfLines={2} spacing="2" />
          </Box>
        );
      
      case 'detail':
        return (
          <Box padding="6" bg="white" borderRadius="md" width="100%">
            <Skeleton height="60px" mb={6} />
            <SimpleGrid columns={2} spacing={4} mb={6}>
              <Skeleton height="100px" />
              <Skeleton height="100px" />
            </SimpleGrid>
            <SkeletonText mt="4" noOfLines={6} spacing="4" />
            <Skeleton height="200px" mt={6} />
          </Box>
        );
      
      default:
        return null;
    }
  };

  return (
    <SimpleGrid columns={columns} spacing={4}>
      {Array(count)
        .fill(0)
        .map((_, index) => (
          <Box key={index}>{renderSkeleton()}</Box>
        ))}
    </SimpleGrid>
  );
};

export default LoadingSkeleton; 