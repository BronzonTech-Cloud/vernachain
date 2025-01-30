import { FC, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardBody,
  Flex,
  FormControl,
  FormLabel,
  Heading,
  Input,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  useToast,
  VStack,
  Badge,
  Text,
  useColorModeValue,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  HStack,
  Tooltip,
  Progress,
} from '@chakra-ui/react';
import { useQuery } from '@tanstack/react-query';
import { FiSend, FiClock, FiLock, FiUnlock } from 'react-icons/fi';
import { QRCodeSVG } from 'qrcode.react';
import { CopyIcon, ExternalLinkIcon } from '@chakra-ui/icons';

interface WalletData {
  address: string;
  balance: number;
  stake: number;
  transaction_count: number;
  is_validator: boolean;
  rewards_earned?: number;
  delegations?: Array<{
    validator: string;
    amount: number;
  }>;
}

interface Transaction {
  hash: string;
  type: 'send' | 'receive' | 'stake' | 'unstake' | 'claim_rewards';
  amount: number;
  status: 'pending' | 'confirmed' | 'failed';
  timestamp: number;
  from?: string;
  to?: string;
}

const Wallet: FC = () => {
  const [address, setAddress] = useState('');
  const [recipient, setRecipient] = useState('');
  const [amount, setAmount] = useState('');
  const [stakeAmount, setStakeAmount] = useState('');
  const [selectedValidator, setSelectedValidator] = useState('');
  const toast = useToast();
  const cardBg = useColorModeValue('white', 'gray.800');
  const { isOpen, onOpen, onClose } = useDisclosure();

  const { data: walletData, isLoading } = useQuery<WalletData>({
    queryKey: ['wallet', address],
    queryFn: async () => {
      if (!address) return null;
      const response = await fetch(`http://localhost:8001/address/${address}`);
      if (!response.ok) throw new Error('Failed to fetch wallet data');
      return response.json();
    },
    enabled: !!address,
  });

  const { data: transactions } = useQuery<Transaction[]>({
    queryKey: ['transactions', address],
    queryFn: async () => {
      if (!address) return [];
      const response = await fetch(`http://localhost:8001/transactions/${address}`);
      if (!response.ok) throw new Error('Failed to fetch transactions');
      return response.json();
    },
    enabled: !!address,
  });

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: 'Address copied',
      status: 'success',
      duration: 2000,
    });
  };

  const handleSend = async () => {
    try {
      const response = await fetch('http://localhost:8001/transactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          from_address: address,
          to_address: recipient,
          amount: parseFloat(amount),
          type: 'transfer',
        }),
      });

      if (!response.ok) throw new Error('Transaction failed');

      toast({
        title: 'Transaction sent',
        description: 'Your transaction has been submitted to the network',
        status: 'success',
        duration: 5000,
      });

      setRecipient('');
      setAmount('');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      toast({
        title: 'Transaction failed',
        description: errorMessage,
        status: 'error',
        duration: 5000,
      });
    }
  };

  const handleStake = async () => {
    try {
      const response = await fetch('http://localhost:8001/stake', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          address,
          amount: parseFloat(stakeAmount),
          validator: selectedValidator,
        }),
      });

      if (!response.ok) throw new Error('Staking failed');

      toast({
        title: 'Tokens staked',
        description: 'Your tokens have been staked successfully',
        status: 'success',
        duration: 5000,
      });

      setStakeAmount('');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      toast({
        title: 'Staking failed',
        description: errorMessage,
        status: 'error',
        duration: 5000,
      });
    }
  };

  const handleUnstake = async (validatorAddress: string, amount: number) => {
    try {
      const response = await fetch('http://localhost:8001/unstake', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          address,
          validator: validatorAddress,
          amount,
        }),
      });

      if (!response.ok) throw new Error('Unstaking failed');

      toast({
        title: 'Tokens unstaked',
        description: 'Your tokens have been unstaked successfully',
        status: 'success',
        duration: 5000,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      toast({
        title: 'Unstaking failed',
        description: errorMessage,
        status: 'error',
        duration: 5000,
      });
    }
  };

  return (
    <Box>
      <Heading mb="6">Wallet</Heading>

      <Card bg={cardBg} mb="6">
        <CardBody>
          <FormControl>
            <FormLabel>Your Address</FormLabel>
            <HStack spacing="4" mb="4">
              <Input
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="Enter your wallet address"
                isDisabled={isLoading}
              />
              <Button onClick={onOpen} colorScheme="brand" size="sm">
                Show QR
              </Button>
              <Tooltip label="Copy address">
                <Button
                  onClick={() => copyToClipboard(address)}
                  size="sm"
                  variant="ghost"
                >
                  <CopyIcon />
                </Button>
              </Tooltip>
            </HStack>
          </FormControl>

          {isLoading ? (
            <Progress size="xs" isIndeterminate />
          ) : walletData && (
            <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing="4">
              <Stat>
                <StatLabel>Balance</StatLabel>
                <StatNumber>{walletData.balance} VERNA</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Staked</StatLabel>
                <StatNumber>{walletData.stake} VERNA</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Rewards Earned</StatLabel>
                <StatNumber>{walletData.rewards_earned || 0} VERNA</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Status</StatLabel>
                <StatNumber>
                  <Badge colorScheme={walletData.is_validator ? 'green' : 'gray'}>
                    {walletData.is_validator ? 'Validator' : 'Regular'}
                  </Badge>
                </StatNumber>
              </Stat>
            </SimpleGrid>
          )}
        </CardBody>
      </Card>

      <Tabs variant="enclosed" colorScheme="brand">
        <TabList>
          <Tab>Send</Tab>
          <Tab>Stake</Tab>
          <Tab>History</Tab>
        </TabList>

        <TabPanels>
          <TabPanel>
            <Card bg={cardBg}>
              <CardBody>
                <VStack spacing="4">
                  <FormControl>
                    <FormLabel>Recipient Address</FormLabel>
                    <Input
                      value={recipient}
                      onChange={(e) => setRecipient(e.target.value)}
                      placeholder="Enter recipient address"
                    />
                  </FormControl>
                  <FormControl>
                    <FormLabel>Amount (VERNA)</FormLabel>
                    <Input
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                      placeholder="Enter amount"
                      type="number"
                    />
                  </FormControl>
                  <Button
                    leftIcon={<FiSend />}
                    colorScheme="brand"
                    onClick={handleSend}
                    isDisabled={!address || !recipient || !amount}
                    width="full"
                  >
                    Send
                  </Button>
                </VStack>
              </CardBody>
            </Card>
          </TabPanel>

          <TabPanel>
            <Card bg={cardBg}>
              <CardBody>
                <VStack spacing="4">
                  <FormControl>
                    <FormLabel>Amount to Stake (VERNA)</FormLabel>
                    <Input
                      value={stakeAmount}
                      onChange={(e) => setStakeAmount(e.target.value)}
                      placeholder="Enter amount to stake"
                      type="number"
                    />
                  </FormControl>
                  <FormControl>
                    <FormLabel>Validator</FormLabel>
                    <Input
                      value={selectedValidator}
                      onChange={(e) => setSelectedValidator(e.target.value)}
                      placeholder="Enter validator address"
                    />
                  </FormControl>
                  <Button
                    leftIcon={<FiLock />}
                    colorScheme="brand"
                    onClick={handleStake}
                    isDisabled={!address || !stakeAmount || !selectedValidator}
                    width="full"
                  >
                    Stake
                  </Button>
                </VStack>

                {walletData?.delegations && walletData.delegations.length > 0 && (
                  <Box mt="6">
                    <Heading size="sm" mb="4">Active Delegations</Heading>
                    <Table variant="simple">
                      <Thead>
                        <Tr>
                          <Th>Validator</Th>
                          <Th>Amount</Th>
                          <Th>Action</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        {walletData.delegations.map((delegation) => (
                          <Tr key={delegation.validator}>
                            <Td>{delegation.validator}</Td>
                            <Td>{delegation.amount} VERNA</Td>
                            <Td>
                              <Button
                                size="sm"
                                leftIcon={<FiUnlock />}
                                onClick={() => handleUnstake(delegation.validator, delegation.amount)}
                              >
                                Unstake
                              </Button>
                            </Td>
                          </Tr>
                        ))}
                      </Tbody>
                    </Table>
                  </Box>
                )}
              </CardBody>
            </Card>
          </TabPanel>

          <TabPanel>
            <Card bg={cardBg}>
              <CardBody>
                <Table variant="simple">
                  <Thead>
                    <Tr>
                      <Th>Type</Th>
                      <Th>Amount</Th>
                      <Th>Status</Th>
                      <Th>Time</Th>
                      <Th>Details</Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {transactions?.map((tx) => (
                      <Tr key={tx.hash}>
                        <Td>{tx.type}</Td>
                        <Td>{tx.amount} VERNA</Td>
                        <Td>
                          <Badge colorScheme={tx.status === 'confirmed' ? 'green' : 'yellow'}>
                            {tx.status}
                          </Badge>
                        </Td>
                        <Td>
                          <Flex align="center" gap="2">
                            <FiClock />
                            <Text>{new Date(tx.timestamp * 1000).toLocaleString()}</Text>
                          </Flex>
                        </Td>
                        <Td>
                          <Button
                            size="sm"
                            rightIcon={<ExternalLinkIcon />}
                            variant="ghost"
                            onClick={() => window.open(`/explorer/tx/${tx.hash}`, '_blank')}
                          >
                            View
                          </Button>
                        </Td>
                      </Tr>
                    ))}
                  </Tbody>
                </Table>
              </CardBody>
            </Card>
          </TabPanel>
        </TabPanels>
      </Tabs>

      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Wallet Address QR Code</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <VStack spacing={4} align="center">
              <QRCodeSVG value={address} size={200} />
              <Text fontSize="sm" color="gray.500">
                Scan this QR code to get the wallet address
              </Text>
            </VStack>
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default Wallet; 