import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardBody,
  FormControl,
  FormLabel,
  Textarea,
  VStack,
  Heading,
  Text,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
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
  useColorModeValue
} from '@chakra-ui/react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

interface TokenGovernanceProps {
  tokenId: string;
}

interface Proposal {
  id: number;
  creator: string;
  description: string;
  for_votes: string;
  against_votes: string;
  status: string;
  start_time: string;
  end_time: string;
  executed: boolean;
}

const TokenGovernance: React.FC<TokenGovernanceProps> = ({ tokenId }) => {
  const cardBg = useColorModeValue('white', 'gray.800');
  const toast = useToast();
  const queryClient = useQueryClient();
  const { isOpen, onOpen, onClose } = useDisclosure();
  
  const [description, setDescription] = useState('');
  const [actions, setActions] = useState('');
  
  // Fetch proposals
  const { data: proposals, isLoading } = useQuery<Proposal[]>({
    queryKey: ['proposals', tokenId],
    queryFn: async () => {
      const response = await fetch(`http://localhost:8001/api/v1/tokens/${tokenId}/proposals`);
      if (!response.ok) throw new Error('Failed to fetch proposals');
      return response.json();
    }
  });
  
  // Create proposal mutation
  const createProposalMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(`http://localhost:8001/api/v1/tokens/${tokenId}/proposals`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description,
          actions: JSON.parse(actions)
        })
      });
      if (!response.ok) throw new Error('Failed to create proposal');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['proposals'] });
      toast({
        title: 'Proposal created',
        status: 'success',
        duration: 3000
      });
      onClose();
      setDescription('');
      setActions('');
    },
    onError: (error: Error) => {
      toast({
        title: 'Failed to create proposal',
        description: error.message,
        status: 'error',
        duration: 5000
      });
    }
  });
  
  // Vote mutation
  const voteMutation = useMutation({
    mutationFn: async ({ proposalId, support }: { proposalId: number, support: boolean }) => {
      const response = await fetch(
        `http://localhost:8001/api/v1/tokens/${tokenId}/proposals/${proposalId}/vote`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ support })
        }
      );
      if (!response.ok) throw new Error('Failed to cast vote');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['proposals'] });
      toast({
        title: 'Vote cast successfully',
        status: 'success',
        duration: 3000
      });
    }
  });
  
  if (isLoading) {
    return <Box>Loading proposals...</Box>;
  }
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'blue';
      case 'succeeded': return 'green';
      case 'defeated': return 'red';
      case 'executed': return 'purple';
      default: return 'gray';
    }
  };
  
  const calculateProgress = (forVotes: string, againstVotes: string) => {
    const total = Number(forVotes) + Number(againstVotes);
    return total > 0 ? (Number(forVotes) / total) * 100 : 0;
  };
  
  return (
    <Box>
      <Card bg={cardBg} mb={4}>
        <CardBody>
          <Heading size="md" mb={4}>Governance</Heading>
          <Button colorScheme="blue" onClick={onOpen}>Create Proposal</Button>
        </CardBody>
      </Card>

      <Card bg={cardBg}>
        <CardBody>
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>ID</Th>
                <Th>Description</Th>
                <Th>Status</Th>
                <Th>Votes</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {proposals?.map((proposal) => (
                <Tr key={proposal.id}>
                  <Td>{proposal.id}</Td>
                  <Td>
                    <Text noOfLines={2}>{proposal.description}</Text>
                  </Td>
                  <Td>
                    <Badge colorScheme={getStatusColor(proposal.status)}>
                      {proposal.status}
                    </Badge>
                  </Td>
                  <Td>
                    <VStack align="stretch" spacing={2}>
                      <Progress
                        value={calculateProgress(proposal.for_votes, proposal.against_votes)}
                        colorScheme="green"
                        size="sm"
                      />
                      <Text fontSize="sm">
                        For: {proposal.for_votes} | Against: {proposal.against_votes}
                      </Text>
                    </VStack>
                  </Td>
                  <Td>
                    {proposal.status === 'active' && (
                      <VStack>
                        <Button
                          size="sm"
                          colorScheme="green"
                          onClick={() => voteMutation.mutate({
                            proposalId: proposal.id,
                            support: true
                          })}
                        >
                          Vote For
                        </Button>
                        <Button
                          size="sm"
                          colorScheme="red"
                          onClick={() => voteMutation.mutate({
                            proposalId: proposal.id,
                            support: false
                          })}
                        >
                          Vote Against
                        </Button>
                      </VStack>
                    )}
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
          <ModalHeader>Create Proposal</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              <FormControl isRequired>
                <FormLabel>Description</FormLabel>
                <Textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe your proposal"
                />
              </FormControl>
              <FormControl isRequired>
                <FormLabel>Actions (JSON)</FormLabel>
                <Textarea
                  value={actions}
                  onChange={(e) => setActions(e.target.value)}
                  placeholder='[{"target": "contract_address", "function": "transfer", "args": ["address", 1000]}]'
                />
              </FormControl>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button
              colorScheme="blue"
              onClick={() => createProposalMutation.mutate()}
              isLoading={createProposalMutation.isPending}
            >
              Create Proposal
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
}

export default TokenGovernance; 