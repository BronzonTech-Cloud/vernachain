import React from 'react';
import {
  Box,
  Heading,
  Text,
  Button,
  VStack,
  useColorModeValue,
} from '@chakra-ui/react';
import { FiHome } from 'react-icons/fi';
import { Link } from 'react-router-dom';

const NotFound: React.FC = () => {
  const bg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <Box
      p={8}
      bg={bg}
      borderRadius="lg"
      borderWidth={1}
      borderColor={borderColor}
      textAlign="center"
    >
      <VStack spacing={6}>
        <Heading size="2xl">404</Heading>
        <Heading size="md">Page Not Found</Heading>
        <Text color="gray.500">
          The page you're looking for doesn't exist or has been moved.
        </Text>
        <Button
          as={Link}
          to="/"
          leftIcon={<FiHome />}
          colorScheme="blue"
        >
          Return Home
        </Button>
      </VStack>
    </Box>
  );
};

export default NotFound; 