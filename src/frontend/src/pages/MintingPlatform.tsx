import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardBody,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  VStack,
  HStack,
  Text,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Image,
  Switch,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Stack,
  SimpleGrid,
  Divider,
  Heading,
  useToast,
  useColorModeValue,
  IconButton,
  Badge,
  Tooltip,
  Progress,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  useDisclosure,
  InputGroup,
  InputRightElement,
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
  FormHelperText,
  Checkbox
} from '@chakra-ui/react';
import { 
  FiEye, 
  FiEyeOff, 
  FiPlus,  
  FiCopy,  
  FiExternalLink,
  FiTrash2
} from 'react-icons/fi';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

interface TokenData {
  id: string;
  name: string;
  symbol: string;
  image: string;
  totalSupply: number;
  currentSupply: number;
  description: string;
  website?: string;
  socials?: {
    twitter?: string;
    telegram?: string;
    discord?: string;
  };
  decimals: number;
  burnable: boolean;
  mintable: boolean;
  createdAt: string;
  updatedAt: string;
  holders: number;
  transferCount: number;
  image_url?: string;
  circulating_supply: string;
  holders_count: number;
  is_mintable: boolean;
  is_burnable: boolean;
  is_pausable: boolean;
  governance_enabled: boolean;
  vesting_enabled: boolean;
}

interface TokenAction {
  tokenId: string;
  amount: number;
  recipient?: string;
}

interface APIKey {
  id: string;
  name: string;
  key: string;
  permissions: string[];
  rateLimit: number;
  ipRestrictions?: string[];
  createdAt: string;
  lastUsed?: string;
  expiresAt?: string;
}

interface AuthState {
  isAuthenticated: boolean;
  email: string;
  twoFactorEnabled: boolean;
}

const MintingPlatform: React.FC = () => {
  const [authState, setAuthState] = useState<AuthState>({ isAuthenticated: false, email: '', twoFactorEnabled: false });
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);
  
  // Token minting state
  const [tokenName, setTokenName] = useState('');
  const [tokenSymbol, setTokenSymbol] = useState('');
  const [tokenImage, setTokenImage] = useState<File | null>(null);
  const [tokenSupply, setTokenSupply] = useState('');
  const [imagePreview, setImagePreview] = useState('');
  const [description, setDescription] = useState('');
  const [website, setWebsite] = useState('');
  const [socials, setSocials] = useState({ twitter: '', telegram: '', discord: '' });
  const [decimals, setDecimals] = useState('18');
  const [burnable, setBurnable] = useState(false);
  const [mintable, setMintable] = useState(true);
  const [isPausable, setIsPausable] = useState(false);
  const [governance_enabled, setGovernanceEnabled] = useState(false);
  const [vesting_enabled, setEnableVesting] = useState(false);
  
  // API key state
  const [newKeyName, setNewKeyName] = useState('');
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([]);
  const [rateLimit, setRateLimit] = useState('1000');
  const [ipRestrictions, setIpRestrictions] = useState('');
  const [keyExpiration, setKeyExpiration] = useState('');
  const [deleteKeyId, setDeleteKeyId] = useState<string>('');
  const { isOpen: isDeleteOpen, onOpen: onDeleteOpen, onClose: onDeleteClose } = useDisclosure();
  const toast = useToast();
  const cardBg = useColorModeValue('white', 'gray.800');
  const queryClient = useQueryClient();

  // Password strength checker
  const [passwordStrength, setPasswordStrength] = useState(0);
  const [twoFactorCode, setTwoFactorCode] = useState('');

  const navigate = useNavigate();

  // Auth mutations
  const authMutation = useMutation({
    mutationFn: async (data: { email: string; password: string; isSignUp: boolean; twoFactorCode?: string }) => {
      const endpoint = data.isSignUp ? '/auth/signup' : '/auth/login';
      const response = await fetch(`http://localhost:8001${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: data.email,
          password: data.password,
          twoFactorCode: data.twoFactorCode,
        }),
        credentials: 'include', // Enable cookies for session management
      });
      if (!response.ok) throw new Error('Authentication failed');
      return response.json();
    },
    onSuccess: (data) => {
      setAuthState({
        isAuthenticated: true,
        email: data.email,
        twoFactorEnabled: data.twoFactorEnabled,
      });
      toast({
        title: isSignUp ? 'Account created' : 'Login successful',
        status: 'success',
        duration: 3000,
      });
    },
  });

  // Token queries and mutations
  const { data: tokens, isLoading } = useQuery<TokenData[]>({
    queryKey: ['tokens'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8001/api/v1/tokens');
      if (!response.ok) throw new Error('Failed to fetch tokens');
      return response.json();
    },
    enabled: authState.isAuthenticated,
  });

  const mintTokenMutation = useMutation({
    mutationFn: async (formData: FormData) => {
      const response = await fetch('http://localhost:8001/api/v1/tokens', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('Failed to mint token');
      return response.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['tokens'] });
      toast({
        title: 'Token created successfully',
        status: 'success',
        duration: 3000,
      });
      // Reset form
      setTokenName('');
      setTokenSymbol('');
      setTokenImage(null);
      setTokenSupply('');
      setImagePreview('');
      setDescription('');
      setWebsite('');
      setSocials({ twitter: '', telegram: '', discord: '' });
      setDecimals('18');
      setBurnable(false);
      setMintable(true);
      
      // Navigate to token details
      navigate(`/tokens/${data.id}`);
    },
    onError: (error: Error) => {
      toast({
        title: 'Failed to create token',
        description: error.message,
        status: 'error',
        duration: 5000,
      });
    },
  });

  // API key queries and mutations
  const { data: apiKeys } = useQuery<APIKey[]>({
    queryKey: ['apiKeys'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8001/api-keys');
      if (!response.ok) throw new Error('Failed to fetch API keys');
      return response.json();
    },
    enabled: authState.isAuthenticated,
  });

  const generateApiKeyMutation = useMutation({
    mutationFn: async (name: string) => {
      const response = await fetch('http://localhost:8001/api-keys/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      });
      if (!response.ok) throw new Error('Failed to generate API key');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apiKeys'] });
      toast({
        title: 'API key generated successfully',
        status: 'success',
        duration: 3000,
      });
      setNewKeyName('');
    },
    onError: (error: Error) => {
      toast({
        title: 'Failed to generate API key',
        description: error.message,
        status: 'error',
        duration: 5000,
      });
    },
  });

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = () => {
          const img: HTMLImageElement = new (window.Image as any)(0, 0);
          img.onload = () => {
            if (img.width === img.height) {
              setTokenImage(file);
              setImagePreview(reader.result as string);
            } else {
              toast({
                title: 'Invalid image dimensions',
                description: 'Image must be square (1:1 aspect ratio)',
                status: 'error',
                duration: 5000,
              });
            }
          };
          img.src = reader.result as string;
        };
        reader.readAsDataURL(file);
      } else {
        toast({
          title: 'Invalid file type',
          description: 'Please upload an image file',
          status: 'error',
          duration: 5000,
        });
      }
    }
  };

  const handleMintToken = () => {
    if (!tokenImage) {
      toast({
        title: 'Image required',
        description: 'Please upload a token image',
        status: 'error',
        duration: 3000,
      });
      return;
    }

    const formData = new FormData();
    formData.append('name', tokenName);
    formData.append('symbol', tokenSymbol);
    formData.append('image', tokenImage);
    formData.append('totalSupply', tokenSupply);
    formData.append('description', description);
    formData.append('website', website);
    formData.append('socials', JSON.stringify(socials));
    formData.append('decimals', decimals);
    formData.append('burnable', String(burnable));
    formData.append('mintable', String(mintable));

    mintTokenMutation.mutate(formData);
  };

  const handleAuth = () => {
    authMutation.mutate({ email, password, isSignUp, twoFactorCode });
  };

  // Enhanced API key management
  const deleteApiKeyMutation = useMutation({
    mutationFn: async (keyId: string) => {
      const response = await fetch(`http://localhost:8001/api-keys/${keyId}`, {
        method: 'DELETE',
        credentials: 'include',
      });
      if (!response.ok) throw new Error('Failed to delete API key');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apiKeys'] });
      toast({
        title: 'API key deleted',
        status: 'success',
        duration: 3000,
      });
    },
  });

  const handleDeleteKey = (keyId: string) => {
    setDeleteKeyId(keyId);
    onDeleteOpen();
  };

  const confirmDeleteKey = () => {
    deleteApiKeyMutation.mutate(deleteKeyId);
    onDeleteClose();
  };

  // Password strength checker
  useEffect(() => {
    if (password) {
      let strength = 0;
      if (password.length >= 8) strength += 25;
      if (/[A-Z]/.test(password)) strength += 25;
      if (/[0-9]/.test(password)) strength += 25;
      if (/[^A-Za-z0-9]/.test(password)) strength += 25;
      setPasswordStrength(strength);
    } else {
      setPasswordStrength(0);
    }
  }, [password]);

  const [selectedToken, setSelectedToken] = useState<TokenData | null>(null);
  const [transferAmount, setTransferAmount] = useState('');
  const [transferRecipient, setTransferRecipient] = useState('');
  const [burnAmount, setBurnAmount] = useState('');
  const { 
    isOpen: isTokenActionOpen, 
    onOpen: onTokenActionOpen, 
    onClose: onTokenActionClose 
  } = useDisclosure();

  // Token transfer mutation
  const transferTokenMutation = useMutation({
    mutationFn: async (data: TokenAction) => {
      const response = await fetch(`http://localhost:8001/tokens/${data.tokenId}/transfer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: data.amount,
          recipient: data.recipient,
        }),
        credentials: 'include',
      });
      if (!response.ok) throw new Error('Failed to transfer tokens');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tokens'] });
      toast({
        title: 'Tokens transferred successfully',
        status: 'success',
        duration: 3000,
      });
      setTransferAmount('');
      setTransferRecipient('');
      onTokenActionClose();
    },
    onError: (error: Error) => {
      toast({
        title: 'Failed to transfer tokens',
        description: error.message,
        status: 'error',
        duration: 5000,
      });
    },
  });

  // Token burn mutation
  const burnTokenMutation = useMutation({
    mutationFn: async (data: TokenAction) => {
      const response = await fetch(`http://localhost:8001/tokens/${data.tokenId}/burn`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount: data.amount }),
        credentials: 'include',
      });
      if (!response.ok) throw new Error('Failed to burn tokens');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tokens'] });
      toast({
        title: 'Tokens burned successfully',
        status: 'success',
        duration: 3000,
      });
      setBurnAmount('');
      onTokenActionClose();
    },
    onError: (error: Error) => {
      toast({
        title: 'Failed to burn tokens',
        description: error.message,
        status: 'error',
        duration: 5000,
      });
    },
  });

  const handleTransfer = () => {
    if (!selectedToken || !transferAmount || !transferRecipient) return;
    
    transferTokenMutation.mutate({
      tokenId: selectedToken.id,
      amount: parseFloat(transferAmount),
      recipient: transferRecipient,
    });
  };

  const handleBurn = () => {
    if (!selectedToken || !burnAmount) return;
    
    burnTokenMutation.mutate({
      tokenId: selectedToken.id,
      amount: parseFloat(burnAmount),
    });
  };

  const openTokenActions = (token: TokenData) => {
    setSelectedToken(token);
    onTokenActionOpen();
  };

  const cancelRef = useRef(null);

  if (!authState.isAuthenticated) {
    return (
      <Box maxW="md" mx="auto" mt="10">
        <Card bg={cardBg}>
          <CardBody>
            <VStack spacing="4">
              <Heading size="lg">{isSignUp ? 'Create Account' : 'Login'}</Heading>
              <FormControl>
                <FormLabel>Email</FormLabel>
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </FormControl>
              <FormControl>
                <FormLabel>Password</FormLabel>
                <InputGroup>
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <InputRightElement>
                    <IconButton
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                      icon={showPassword ? <FiEyeOff /> : <FiEye />}
                      variant="ghost"
                      onClick={() => setShowPassword(!showPassword)}
                    />
                  </InputRightElement>
                </InputGroup>
                {isSignUp && (
                  <Box mt="2">
                    <Progress value={passwordStrength} colorScheme={passwordStrength > 75 ? 'green' : 'orange'} />
                    <Text fontSize="sm" color="gray.500">
                      Password strength: {passwordStrength}%
                    </Text>
                  </Box>
                )}
              </FormControl>
              {authState.twoFactorEnabled && (
                <FormControl>
                  <FormLabel>2FA Code</FormLabel>
                  <Input
                    type="text"
                    value={twoFactorCode}
                    onChange={(e) => setTwoFactorCode(e.target.value)}
                    placeholder="Enter 2FA code"
                  />
                </FormControl>
              )}
              <Button
                colorScheme="brand"
                width="full"
                onClick={handleAuth}
                isLoading={authMutation.isPending}
              >
                {isSignUp ? 'Sign Up' : 'Login'}
              </Button>
              <Button
                variant="link"
                onClick={() => setIsSignUp(!isSignUp)}
              >
                {isSignUp ? 'Already have an account? Login' : "Don't have an account? Sign Up"}
              </Button>
            </VStack>
          </CardBody>
        </Card>
      </Box>
    );
  }

  return (
    <Box p={8}>
      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8}>
        {/* Token Creation Form */}
        <Card bg={cardBg}>
          <CardBody>
            <VStack spacing={6}>
              <Heading size="lg">Create New Token</Heading>
              
              <SimpleGrid columns={2} spacing={4} width="full">
                <FormControl isRequired>
                  <FormLabel>Token Name</FormLabel>
                  <Input
                    value={tokenName}
                    onChange={(e) => setTokenName(e.target.value)}
                    placeholder="e.g., My Token"
                  />
                </FormControl>
                
                <FormControl isRequired>
                  <FormLabel>Token Symbol</FormLabel>
                  <Input
                    value={tokenSymbol}
                    onChange={(e) => setTokenSymbol(e.target.value.toUpperCase())}
                    placeholder="e.g., MTK"
                  />
                </FormControl>
              </SimpleGrid>
              
              <FormControl isRequired>
                <FormLabel>Description</FormLabel>
                <Textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe your token's purpose and features"
                />
              </FormControl>
              
              <SimpleGrid columns={2} spacing={4} width="full">
                <FormControl isRequired>
                  <FormLabel>Initial Supply</FormLabel>
                  <NumberInput
                    value={tokenSupply}
                    onChange={(value) => setTokenSupply(value)}
                    min={0}
                  >
                    <NumberInputField placeholder="Enter initial supply" />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>
                
                <FormControl>
                  <FormLabel>Decimals</FormLabel>
                  <NumberInput
                    value={decimals}
                    onChange={(value) => setDecimals(value)}
                    min={0}
                    max={18}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>
              </SimpleGrid>
              
              <FormControl>
                <FormLabel>Token Image</FormLabel>
                <Input
                  type="file"
                  accept="image/*"
                  onChange={handleImageChange}
                />
                <Text fontSize="sm" color="gray.500" mt={1}>
                  Recommended: Square image (1:1 aspect ratio)
                </Text>
                {imagePreview && (
                  <Image
                    src={imagePreview}
                    alt="Token preview"
                    boxSize="100px"
                    objectFit="cover"
                    mt={2}
                    borderRadius="md"
                  />
                )}
              </FormControl>
              
              <Divider />
              
              <Heading size="md">Token Features</Heading>
              <SimpleGrid columns={2} spacing={4} width="full">
                <FormControl display="flex" alignItems="center">
                  <FormLabel mb="0">Mintable</FormLabel>
                  <Switch
                    isChecked={mintable}
                    onChange={(e) => setMintable(e.target.checked)}
                  />
                </FormControl>
                
                <FormControl display="flex" alignItems="center">
                  <FormLabel mb="0">Burnable</FormLabel>
                  <Switch
                    isChecked={burnable}
                    onChange={(e) => setBurnable(e.target.checked)}
                  />
                </FormControl>
                
                <FormControl display="flex" alignItems="center">
                  <FormLabel mb="0">Pausable</FormLabel>
                  <Switch
                    isChecked={isPausable}
                    onChange={(e) => setIsPausable(e.target.checked)}
                  />
                </FormControl>
                
                <FormControl display="flex" alignItems="center">
                  <FormLabel mb="0">Governance</FormLabel>
                  <Switch
                    isChecked={governance_enabled}
                    onChange={(e) => setGovernanceEnabled(e.target.checked)}
                  />
                </FormControl>
                
                <FormControl display="flex" alignItems="center">
                  <FormLabel mb="0">Vesting</FormLabel>
                  <Switch
                    isChecked={vesting_enabled}
                    onChange={(e) => setEnableVesting(e.target.checked)}
                  />
                </FormControl>
              </SimpleGrid>
              
              <Divider />
              
              <Heading size="md">Social Links</Heading>
              <SimpleGrid columns={1} spacing={4} width="full">
                <FormControl>
                  <FormLabel>Website</FormLabel>
                  <Input
                    value={website}
                    onChange={(e) => setWebsite(e.target.value)}
                    placeholder="https://"
                  />
                </FormControl>
                
                <FormControl>
                  <FormLabel>Twitter</FormLabel>
                  <Input
                    value={socials.twitter}
                    onChange={(e) => setSocials({ ...socials, twitter: e.target.value })}
                    placeholder="@username"
                  />
                </FormControl>
                
                <FormControl>
                  <FormLabel>Telegram</FormLabel>
                  <Input
                    value={socials.telegram}
                    onChange={(e) => setSocials({ ...socials, telegram: e.target.value })}
                    placeholder="t.me/group"
                  />
                </FormControl>
                
                <FormControl>
                  <FormLabel>Discord</FormLabel>
                  <Input
                    value={socials.discord}
                    onChange={(e) => setSocials({ ...socials, discord: e.target.value })}
                    placeholder="discord.gg/invite"
                  />
                </FormControl>
              </SimpleGrid>
              
              <Button
                colorScheme="blue"
                size="lg"
                width="full"
                onClick={handleMintToken}
                isLoading={mintTokenMutation.isPending}
              >
                Create Token
              </Button>
            </VStack>
          </CardBody>
        </Card>
        
        {/* Token List */}
        <Card bg={cardBg}>
          <CardBody>
            <Heading size="lg" mb={6}>Your Tokens</Heading>
            
            {isLoading ? (
              <Text>Loading tokens...</Text>
            ) : (
              <Table variant="simple">
                <Thead>
                  <Tr>
                    <Th>Token</Th>
                    <Th>Supply</Th>
                    <Th>Features</Th>
                    <Th>Actions</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {tokens?.map((token) => (
                    <Tr key={token.id}>
                      <Td>
                        <HStack>
                          {token.image_url && (
                            <Image
                              src={token.image_url}
                              alt={token.name}
                              boxSize="40px"
                              borderRadius="full"
                            />
                          )}
                          <VStack align="start" spacing={0}>
                            <Text fontWeight="bold">{token.name}</Text>
                            <Text fontSize="sm" color="gray.500">
                              {token.symbol}
                            </Text>
                          </VStack>
                        </HStack>
                      </Td>
                      <Td>
                        <VStack align="start" spacing={0}>
                          <Text>{token.circulating_supply}</Text>
                          <Text fontSize="sm" color="gray.500">
                            {token.holders_count} holders
                          </Text>
                        </VStack>
                      </Td>
                      <Td>
                        <HStack spacing={2}>
                          {token.is_mintable && (
                            <Badge colorScheme="green">Mintable</Badge>
                          )}
                          {token.is_burnable && (
                            <Badge colorScheme="red">Burnable</Badge>
                          )}
                          {token.governance_enabled && (
                            <Badge colorScheme="purple">Governance</Badge>
                          )}
                          {token.vesting_enabled && (
                            <Badge colorScheme="blue">Vesting</Badge>
                          )}
                        </HStack>
                      </Td>
                      <Td>
                        <HStack spacing={2}>
                          <Tooltip label="View Details">
                            <IconButton
                              aria-label="View token details"
                              icon={<FiExternalLink />}
                              variant="ghost"
                              onClick={() => navigate(`/tokens/${token.id}`)}
                            />
                          </Tooltip>
                          <Tooltip label="Token Actions">
                            <IconButton
                              aria-label="Token actions"
                              icon={<FiPlus />}
                              variant="ghost"
                              onClick={() => openTokenActions(token)}
                            />
                          </Tooltip>
                        </HStack>
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            )}
          </CardBody>
        </Card>
      </SimpleGrid>
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Create New API Key</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <FormControl>
              <FormLabel>Key Name</FormLabel>
              <Input 
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
                placeholder="Enter key name"
              />
            </FormControl>
            <FormControl mt={4}>
              <FormLabel>Rate Limit (requests/day)</FormLabel>
              <Input 
                value={rateLimit}
                onChange={(e) => setRateLimit(e.target.value)}
                type="number"
              />
            </FormControl>
            <FormControl mt={4}>
              <FormLabel>IP Restrictions</FormLabel>
              <Input 
                value={ipRestrictions}
                onChange={(e) => setIpRestrictions(e.target.value)}
                placeholder="Enter IP addresses (comma-separated)"
              />
              <FormHelperText>Optional: Restrict API key access to specific IPs</FormHelperText>
            </FormControl>
            <FormControl mt={4}>
              <FormLabel>Key Expiration</FormLabel>
              <Input 
                type="datetime-local"
                value={keyExpiration}
                onChange={(e) => setKeyExpiration(e.target.value)}
                placeholder="Set expiration date/time"
              />
              <FormHelperText>Optional: Set when this API key should expire</FormHelperText>
            </FormControl>
            <FormControl mt={4}>
              <FormLabel>Permissions</FormLabel>
              <Stack spacing={2}>
                {['read', 'write', 'admin'].map((permission) => (
                  <Checkbox
                    key={permission}
                    isChecked={selectedPermissions.includes(permission)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedPermissions([...selectedPermissions, permission]);
                      } else {
                        setSelectedPermissions(selectedPermissions.filter(p => p !== permission));
                      }
                    }}
                  >
                    {permission.charAt(0).toUpperCase() + permission.slice(1)}
                  </Checkbox>
                ))}
              </Stack>
            </FormControl>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>Cancel</Button>
            <Button 
              colorScheme="blue" 
              onClick={() => {
                generateApiKeyMutation.mutate(newKeyName);
                onClose();
              }}
            >
              Create
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
      <Button leftIcon={<FiPlus />} onClick={onOpen}>
        Create API Key
      </Button>
      <AlertDialog
        isOpen={isDeleteOpen}
        leastDestructiveRef={cancelRef}
        onClose={onDeleteClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader>Delete API Key</AlertDialogHeader>
            <AlertDialogBody>
              Are you sure? This action cannot be undone.
            </AlertDialogBody>
            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onDeleteClose}>Cancel</Button>
              <Button colorScheme="red" ml={3} onClick={confirmDeleteKey}>
                Delete
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>Name</Th>
            <Th>Key</Th>
            <Th>Permissions</Th>
            <Th>Actions</Th>
          </Tr>
        </Thead>
        <Tbody>
          {apiKeys?.map((key) => (
            <Tr key={key.id}>
              <Td>{key.name}</Td>
              <Td>
                <HStack>
                  <Text>{key.key}</Text>
                  <IconButton
                    aria-label="Copy API key"
                    icon={<FiCopy />}
                    size="sm"
                    onClick={() => {
                      navigator.clipboard.writeText(key.key);
                      toast({ title: 'API key copied', status: 'success' });
                    }}
                  />
                </HStack>
              </Td>
              <Td>{key.permissions.join(', ')}</Td>
              <Td>
                <IconButton
                  aria-label="Delete API key"
                  icon={<FiTrash2 />}
                  colorScheme="red"
                  size="sm"
                  onClick={() => handleDeleteKey(key.id)}
                />
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
      <Modal isOpen={isTokenActionOpen} onClose={onTokenActionClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Token Actions - {selectedToken?.name}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              {selectedToken?.is_mintable && (
                <FormControl>
                  <FormLabel>Transfer Amount</FormLabel>
                  <Input
                    type="number"
                    value={transferAmount}
                    onChange={(e) => setTransferAmount(e.target.value)}
                  />
                  <Input
                    mt={2}
                    placeholder="Recipient Address"
                    value={transferRecipient}
                    onChange={(e) => setTransferRecipient(e.target.value)}
                  />
                  <Button mt={2} onClick={handleTransfer}>Transfer</Button>
                </FormControl>
              )}
              {selectedToken?.is_burnable && (
                <FormControl>
                  <FormLabel>Burn Amount</FormLabel>
                  <Input
                    type="number"
                    value={burnAmount}
                    onChange={(e) => setBurnAmount(e.target.value)}
                  />
                  <Button mt={2} onClick={handleBurn}>Burn</Button>
                </FormControl>
              )}
            </VStack>
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default MintingPlatform; 