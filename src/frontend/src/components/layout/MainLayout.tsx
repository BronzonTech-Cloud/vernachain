import React from 'react';
import {
  Box,
  Container,
  Flex,
  useColorMode,
  useColorModeValue,
  IconButton,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  useDisclosure,
  VStack,
  HStack,
  Text,
  Link as ChakraLink,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  Heading,
} from '@chakra-ui/react';
import {
  FiMenu,
  FiSun,
  FiMoon,
  FiHome,
  FiActivity,
  FiUsers,
  FiLayers,
  FiBox,
  FiSettings,
} from 'react-icons/fi';
import { Link, useLocation, Link as RouterLink } from 'react-router-dom';
import SearchBar from '../common/SearchBar';
import ErrorBoundary from '../common/ErrorBoundary';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const { colorMode, toggleColorMode } = useColorMode();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const location = useLocation();
  
  const bg = useColorModeValue('gray.50', 'gray.900');
  const navBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const navigationItems = [
    { name: 'Dashboard', icon: FiHome, path: '/' },
    { name: 'Network', icon: FiActivity, path: '/network' },
    { name: 'Validators', icon: FiUsers, path: '/validators' },
    { name: 'Shards', icon: FiLayers, path: '/shards' },
    { name: 'Transactions', icon: FiBox, path: '/transactions' },
    { name: 'Settings', icon: FiSettings, path: '/settings' },
  ];

  const getBreadcrumbs = () => {
    const paths = location.pathname.split('/').filter(Boolean);
    return [
      { name: 'Home', path: '/' },
      ...paths.map((path, index) => ({
        name: path.charAt(0).toUpperCase() + path.slice(1),
        path: '/' + paths.slice(0, index + 1).join('/')
      }))
    ];
  };

  const NavigationItem = ({ item }: { item: typeof navigationItems[0] }) => (
    <ChakraLink
      as={RouterLink}
      to={item.path}
      _hover={{ textDecoration: 'none' }}
      width="100%"
    >
      <HStack
        spacing={4}
        px={4}
        py={3}
        rounded="md"
        bg={location.pathname === item.path ? 'blue.500' : 'transparent'}
        color={location.pathname === item.path ? 'white' : undefined}
        _hover={{
          bg: location.pathname === item.path ? 'blue.600' : 'gray.100',
        }}
      >
        <item.icon />
        <Text>{item.name}</Text>
      </HStack>
    </ChakraLink>
  );

  return (
    <ErrorBoundary>
      <Box minH="100vh" bg={bg}>
        {/* Header */}
        <Flex
          as="header"
          position="fixed"
          w="100%"
          bg={navBg}
          borderBottomWidth={1}
          borderColor={borderColor}
          py={4}
          px={8}
          alignItems="center"
          justifyContent="space-between"
          zIndex={1000}
        >
          <HStack spacing={4}>
            <IconButton
              aria-label="Menu"
              icon={<FiMenu />}
              onClick={onOpen}
              variant="ghost"
            />
            <Heading size="md">Vernachain Explorer</Heading>
          </HStack>

          <Box flex={1} mx={8}>
            <SearchBar />
          </Box>

          <IconButton
            aria-label="Toggle color mode"
            icon={colorMode === 'light' ? <FiMoon /> : <FiSun />}
            onClick={toggleColorMode}
            variant="ghost"
          />
        </Flex>

        {/* Sidebar */}
        <Drawer isOpen={isOpen} placement="left" onClose={onClose}>
          <DrawerOverlay />
          <DrawerContent>
            <DrawerCloseButton />
            <DrawerHeader borderBottomWidth={1}>Navigation</DrawerHeader>
            <DrawerBody>
              <VStack spacing={2} align="stretch">
                {navigationItems.map((item) => (
                  <NavigationItem key={item.path} item={item} />
                ))}
              </VStack>
            </DrawerBody>
          </DrawerContent>
        </Drawer>

        {/* Main Content */}
        <Container
          maxW="container.xl"
          pt="100px"
          pb={8}
          px={4}
        >
          <Breadcrumb mb={6}>
            {getBreadcrumbs().map((crumb, index) => (
              <BreadcrumbItem key={crumb.path}>
                <BreadcrumbLink
                  as={Link}
                  to={crumb.path}
                  isCurrentPage={index === getBreadcrumbs().length - 1}
                >
                  {crumb.name}
                </BreadcrumbLink>
              </BreadcrumbItem>
            ))}
          </Breadcrumb>

          {children}
        </Container>
      </Box>
    </ErrorBoundary>
  );
};

export default MainLayout; 