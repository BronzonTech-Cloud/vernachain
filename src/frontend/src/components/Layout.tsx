import React from 'react';
import { Box, Container } from '@chakra-ui/react';

// Add debugging
console.log('Rendering Layout component');

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <Box minH="100vh" bg="gray.50">
      <Container maxW="container.xl" py={8}>
        {children}
      </Container>
    </Box>
  );
};

export default Layout; 