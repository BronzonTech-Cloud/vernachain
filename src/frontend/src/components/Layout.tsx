import { ReactNode } from 'react';
import {
  Box,
  Flex,
  HStack,
  IconButton,
  Link,
  Stack,
  Text,
  useColorMode,
  useColorModeValue,
  useDisclosure,
} from '@chakra-ui/react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import { FiMenu, FiX, FiSun, FiMoon } from 'react-icons/fi';

const NavItem = ({ to, children }: { to: string; children: ReactNode }) => {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link
      as={RouterLink}
      to={to}
      px={4}
      py={2}
      rounded="md"
      bg={isActive ? 'brand.500' : 'transparent'}
      color={isActive ? 'white' : undefined}
      _hover={{
        textDecoration: 'none',
        bg: isActive ? 'brand.600' : useColorModeValue('gray.100', 'gray.700'),
      }}
    >
      {children}
    </Link>
  );
};

const Layout = ({ children }: { children: ReactNode }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { colorMode, toggleColorMode } = useColorMode();

  return (
    <Box minH="100vh">
      <Box
        as="nav"
        bg={useColorModeValue('white', 'gray.800')}
        borderBottom="1px"
        borderBottomColor={useColorModeValue('gray.200', 'gray.700')}
        position="fixed"
        w="100%"
        zIndex={10}
      >
        <Flex
          h={16}
          alignItems="center"
          justifyContent="space-between"
          maxW="7xl"
          mx="auto"
          px={4}
        >
          <IconButton
            size="md"
            icon={isOpen ? <FiX /> : <FiMenu />}
            aria-label="Open Menu"
            display={{ md: 'none' }}
            onClick={isOpen ? onClose : onOpen}
          />

          <HStack spacing={8} alignItems="center">
            <Text
              fontSize="xl"
              fontWeight="bold"
              bgGradient="linear(to-r, brand.400, brand.600)"
              bgClip="text"
            >
              Vernachain Explorer
            </Text>
            <HStack as="nav" spacing={4} display={{ base: 'none', md: 'flex' }}>
              <NavItem to="/">Dashboard</NavItem>
              <NavItem to="/blocks">Blocks</NavItem>
              <NavItem to="/transactions">Transactions</NavItem>
              <NavItem to="/validators">Validators</NavItem>
              <NavItem to="/contracts">Contracts</NavItem>
              <NavItem to="/bridge">Bridge</NavItem>
              <NavItem to="/api-docs">API Docs</NavItem>
            </HStack>
          </HStack>

          <IconButton
            size="md"
            icon={colorMode === 'light' ? <FiMoon /> : <FiSun />}
            aria-label="Toggle color mode"
            onClick={toggleColorMode}
          />
        </Flex>

        {isOpen && (
          <Box
            pb={4}
            display={{ md: 'none' }}
            bg={useColorModeValue('white', 'gray.800')}
          >
            <Stack as="nav" spacing={4}>
              <NavItem to="/">Dashboard</NavItem>
              <NavItem to="/blocks">Blocks</NavItem>
              <NavItem to="/transactions">Transactions</NavItem>
              <NavItem to="/validators">Validators</NavItem>
              <NavItem to="/contracts">Contracts</NavItem>
              <NavItem to="/bridge">Bridge</NavItem>
              <NavItem to="/api-docs">API Docs</NavItem>
            </Stack>
          </Box>
        )}
      </Box>

      <Box as="main" pt={20} px={4} maxW="7xl" mx="auto">
        {children}
      </Box>
    </Box>
  );
};

export default Layout; 