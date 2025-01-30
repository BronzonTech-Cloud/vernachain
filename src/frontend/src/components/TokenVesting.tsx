import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardBody,
  FormControl,
  FormLabel,
  Input,
  VStack,
  HStack,
  Text,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Progress,
  useToast,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  useDisclosure,
  useColorModeValue,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Heading
} from '@chakra-ui/react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

interface TokenVestingProps {
  tokenId: string;
}

interface VestingSchedule {
  beneficiary: string;
  total_amount: string;
  released_amount: string;
  start_time: string;
  cliff_duration: number;
  vesting_duration: number;
  revoked: boolean;
  vested_amount: string;
  releasable_amount: string;
}

const TokenVesting: React.FC<TokenVestingProps> = ({ tokenId }) => {
  const cardBg = useColorModeValue('white', 'gray.800');
  const toast = useToast();
  const queryClient = useQueryClient();
  const { isOpen, onOpen, onClose } = useDisclosure();
  
  const [beneficiary, setBeneficiary] = useState('');
  const [amount, setAmount] = useState('');
  const [cliffDuration, setCliffDuration] = useState('0');
  const [vestingDuration, setVestingDuration] = useState('0');
  
  // Fetch vesting schedules
  const { data: schedules, isLoading } = useQuery<VestingSchedule[]>({
    queryKey: ['vesting-schedules', tokenId],
    queryFn: async () => {
      const response = await fetch(`http://localhost:8001/api/v1/tokens/${tokenId}/vesting`);
      if (!response.ok) throw new Error('Failed to fetch vesting schedules');
      return response.json();
    }
  });
  
  // Create vesting schedule mutation
  const createScheduleMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(`http://localhost:8001/api/v1/tokens/${tokenId}/vesting`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          beneficiary,
          total_amount: Number(amount),
          cliff_duration: Number(cliffDuration),
          vesting_duration: Number(vestingDuration)
        })
      });
      if (!response.ok) throw new Error('Failed to create vesting schedule');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vesting-schedules'] });
      toast({
        title: 'Vesting schedule created',
        status: 'success',
        duration: 3000
      });
      onClose();
      setBeneficiary('');
      setAmount('');
      setCliffDuration('0');
      setVestingDuration('0');
    },
    onError: (error: Error) => {
      toast({
        title: 'Failed to create vesting schedule',
        description: error.message,
        status: 'error',
        duration: 5000
      });
    }
  });
  
  // Release tokens mutation
  const releaseMutation = useMutation({
    mutationFn: async (beneficiary: string) => {
      const response = await fetch(
        `http://localhost:8001/api/v1/tokens/${tokenId}/vesting/${beneficiary}/release`,
        { method: 'POST' }
      );
      if (!response.ok) throw new Error('Failed to release tokens');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vesting-schedules'] });
      toast({
        title: 'Tokens released successfully',
        status: 'success',
        duration: 3000
      });
    }
  });
  
  // Revoke schedule mutation
  const revokeMutation = useMutation({
    mutationFn: async (beneficiary: string) => {
      const response = await fetch(
        `http://localhost:8001/api/v1/tokens/${tokenId}/vesting/${beneficiary}/revoke`,
        { method: 'POST' }
      );
      if (!response.ok) throw new Error('Failed to revoke schedule');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vesting-schedules'] });
      toast({
        title: 'Schedule revoked successfully',
        status: 'success',
        duration: 3000
      });
    }
  });
  
  if (isLoading) {
    return <Box>Loading vesting schedules...</Box>;
  }
  
  const calculateProgress = (vested: string, total: string) => {
    return (Number(vested) / Number(total)) * 100;
  };
  
  const formatDuration = (seconds: number) => {
    const days = Math.floor(seconds / (24 * 3600));
    const hours = Math.floor((seconds % (24 * 3600)) / 3600);
    return `${days}d ${hours}h`;
  };
  
  return (
    <Box>
      <Card bg={cardBg} mb={4}>
        <CardBody>
          <Heading size="md" mb={4}>Token Vesting</Heading>
          <Button colorScheme="blue" onClick={onOpen}>Create Vesting Schedule</Button>
        </CardBody>
      </Card>

      <Card bg={cardBg}>
        <CardBody>
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Beneficiary</Th>
                <Th>Progress</Th>
                <Th>Duration</Th>
                <Th>Releasable</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {schedules?.map((schedule) => (
                <Tr key={schedule.beneficiary}>
                  <Td>{schedule.beneficiary}</Td>
                  <Td>
                    <VStack align="stretch" spacing={2}>
                      <Progress
                        value={calculateProgress(schedule.vested_amount, schedule.total_amount)}
                        size="sm"
                        colorScheme="blue"
                      />
                      <Text fontSize="sm">
                        {schedule.released_amount} / {schedule.total_amount}
                      </Text>
                    </VStack>
                  </Td>
                  <Td>
                    <VStack align="start" spacing={0}>
                      <Text>Cliff: {formatDuration(schedule.cliff_duration)}</Text>
                      <Text>Total: {formatDuration(schedule.vesting_duration)}</Text>
                    </VStack>
                  </Td>
                  <Td>{schedule.releasable_amount}</Td>
                  <Td>
                    <VStack>
                      <Button
                        size="sm"
                        colorScheme="green"
                        onClick={() => releaseMutation.mutate(schedule.beneficiary)}
                        isDisabled={Number(schedule.releasable_amount) === 0 || schedule.revoked}
                      >
                        Release
                      </Button>
                      {!schedule.revoked && (
                        <Button
                          size="sm"
                          colorScheme="red"
                          onClick={() => revokeMutation.mutate(schedule.beneficiary)}
                        >
                          Revoke
                        </Button>
                      )}
                    </VStack>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </CardBody>
      </Card>

      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Create Vesting Schedule</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              <FormControl isRequired>
                <FormLabel>Beneficiary Address</FormLabel>
                <Input
                  value={beneficiary}
                  onChange={(e) => setBeneficiary(e.target.value)}
                  placeholder="0x..."
                />
              </FormControl>
              <FormControl isRequired>
                <FormLabel>Amount</FormLabel>
                <NumberInput
                  value={amount}
                  onChange={(value) => setAmount(value)}
                  min={0}
                >
                  <NumberInputField placeholder="Enter amount" />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
              </FormControl>
              <FormControl isRequired>
                <FormLabel>Cliff Duration (seconds)</FormLabel>
                <NumberInput
                  value={cliffDuration}
                  onChange={(value) => setCliffDuration(value)}
                  min={0}
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
              </FormControl>
              <FormControl isRequired>
                <FormLabel>Vesting Duration (seconds)</FormLabel>
                <NumberInput
                  value={vestingDuration}
                  onChange={(value) => setVestingDuration(value)}
                  min={0}
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
              </FormControl>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button
              colorScheme="blue"
              onClick={() => createScheduleMutation.mutate()}
              isLoading={createScheduleMutation.isPending}
            >
              Create Schedule
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
}

export default TokenVesting; 