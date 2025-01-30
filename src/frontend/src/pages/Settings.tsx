import React from 'react';
import {
  Box,
  VStack,
  Heading,
  FormControl,
  FormLabel,
  Switch,
  Select,
  useColorMode,
  useColorModeValue,
  Text,
  Divider,
  SimpleGrid,
  Card,
  CardBody,
  Button,
  HStack,
} from '@chakra-ui/react';
import { FiSave, FiRefreshCw } from 'react-icons/fi';

const Settings: React.FC = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  const bg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <VStack spacing={6} align="stretch">
      <Box>
        <Heading size="lg" mb={2}>Settings</Heading>
        <Text color="gray.500">
          Manage your application preferences and display settings
        </Text>
      </Box>

      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
        {/* Appearance Settings */}
        <Card bg={bg} borderColor={borderColor} borderWidth={1}>
          <CardBody>
            <VStack spacing={6} align="stretch">
              <Heading size="md">Appearance</Heading>
              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="dark-mode" mb="0">
                  Dark Mode
                </FormLabel>
                <Switch
                  id="dark-mode"
                  isChecked={colorMode === 'dark'}
                  onChange={toggleColorMode}
                />
              </FormControl>

              <FormControl>
                <FormLabel>Theme Color</FormLabel>
                <Select defaultValue="blue">
                  <option value="blue">Blue</option>
                  <option value="purple">Purple</option>
                  <option value="green">Green</option>
                  <option value="red">Red</option>
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel>Font Size</FormLabel>
                <Select defaultValue="medium">
                  <option value="small">Small</option>
                  <option value="medium">Medium</option>
                  <option value="large">Large</option>
                </Select>
              </FormControl>
            </VStack>
          </CardBody>
        </Card>

        {/* Data Display Settings */}
        <Card bg={bg} borderColor={borderColor} borderWidth={1}>
          <CardBody>
            <VStack spacing={6} align="stretch">
              <Heading size="md">Data Display</Heading>
              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="auto-refresh" mb="0">
                  Auto-refresh Data
                </FormLabel>
                <Switch id="auto-refresh" defaultChecked />
              </FormControl>

              <FormControl>
                <FormLabel>Refresh Interval</FormLabel>
                <Select defaultValue="30">
                  <option value="15">15 seconds</option>
                  <option value="30">30 seconds</option>
                  <option value="60">1 minute</option>
                  <option value="300">5 minutes</option>
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel>Transaction Display Count</FormLabel>
                <Select defaultValue="50">
                  <option value="25">25 transactions</option>
                  <option value="50">50 transactions</option>
                  <option value="100">100 transactions</option>
                </Select>
              </FormControl>
            </VStack>
          </CardBody>
        </Card>

        {/* Notification Settings */}
        <Card bg={bg} borderColor={borderColor} borderWidth={1}>
          <CardBody>
            <VStack spacing={6} align="stretch">
              <Heading size="md">Notifications</Heading>
              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="desktop-notifications" mb="0">
                  Desktop Notifications
                </FormLabel>
                <Switch id="desktop-notifications" defaultChecked />
              </FormControl>

              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="sound-alerts" mb="0">
                  Sound Alerts
                </FormLabel>
                <Switch id="sound-alerts" />
              </FormControl>

              <FormControl>
                <FormLabel>Notification Events</FormLabel>
                <Select defaultValue="all">
                  <option value="all">All Events</option>
                  <option value="important">Important Only</option>
                  <option value="none">None</option>
                </Select>
              </FormControl>
            </VStack>
          </CardBody>
        </Card>

        {/* Advanced Settings */}
        <Card bg={bg} borderColor={borderColor} borderWidth={1}>
          <CardBody>
            <VStack spacing={6} align="stretch">
              <Heading size="md">Advanced</Heading>
              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="developer-mode" mb="0">
                  Developer Mode
                </FormLabel>
                <Switch id="developer-mode" />
              </FormControl>

              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="analytics" mb="0">
                  Usage Analytics
                </FormLabel>
                <Switch id="analytics" defaultChecked />
              </FormControl>

              <Divider />

              <Text fontSize="sm" color="gray.500">
                Cache Size: 24.5 MB
              </Text>
              <Button
                leftIcon={<FiRefreshCw />}
                variant="outline"
                size="sm"
              >
                Clear Cache
              </Button>
            </VStack>
          </CardBody>
        </Card>
      </SimpleGrid>

      <Divider />

      <HStack spacing={4} justify="flex-end">
        <Button variant="outline">
          Reset to Defaults
        </Button>
        <Button
          colorScheme="blue"
          leftIcon={<FiSave />}
        >
          Save Changes
        </Button>
      </HStack>
    </VStack>
  );
};

export default Settings; 