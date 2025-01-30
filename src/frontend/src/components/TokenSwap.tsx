import React, { useState, useEffect } from 'react';
import {
  Button,
  Card,
  CardBody,
  FormControl,
  FormLabel,
  Input,
  VStack,
  HStack,
  Text,
  Select,
  IconButton,
  useToast,
  Divider,
  useColorModeValue,
  Skeleton,
} from '@chakra-ui/react';
import { FiArrowDown } from 'react-icons/fi';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

interface TokenSwapProps {
  tokenId: string;
}

interface TokenInfo {
  id: string;
  symbol: string;
  name: string;
  price: number;
  balance: number;
}

interface SwapQuote {
  inputAmount: number;
  outputAmount: number;
  price: number;
  priceImpact: number;
  fee: number;
}

const TokenSwap: React.FC<TokenSwapProps> = ({ tokenId }) => {
  const [inputAmount, setInputAmount] = useState<string>('');
  const [outputAmount, setOutputAmount] = useState<string>('');
  const [slippage, setSlippage] = useState<string>('0.5');
  const [fromToken, setFromToken] = useState<string>('VERNA');
  const [toToken, setToToken] = useState<string>(tokenId);
  
  const toast = useToast();
  const queryClient = useQueryClient();
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  // Fetch available tokens
  const { data: tokens, isLoading: tokensLoading } = useQuery<TokenInfo[]>({
    queryKey: ['available-tokens'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8001/api/v1/tokens/list');
      if (!response.ok) throw new Error('Failed to fetch tokens');
      return response.json();
    }
  });

  // Get swap quote
  const { data: quote, isLoading: quoteLoading } = useQuery<SwapQuote>({
    queryKey: ['swap-quote', fromToken, toToken, inputAmount],
    queryFn: async () => {
      if (!inputAmount || parseFloat(inputAmount) === 0) return null;
      const response = await fetch(`http://localhost:8001/api/v1/swap/quote?from=${fromToken}&to=${toToken}&amount=${inputAmount}`);
      if (!response.ok) throw new Error('Failed to fetch quote');
      return response.json();
    },
    enabled: !!inputAmount && parseFloat(inputAmount) > 0
  });

  // Execute swap
  const swapMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('http://localhost:8001/api/v1/swap/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fromToken,
          toToken,
          inputAmount,
          slippage,
        }),
      });
      if (!response.ok) throw new Error('Swap failed');
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: 'Swap successful',
        status: 'success',
        duration: 5000,
      });
      queryClient.invalidateQueries({ queryKey: ['available-tokens'] });
      setInputAmount('');
      setOutputAmount('');
    },
    onError: (error: Error) => {
      toast({
        title: 'Swap failed',
        description: error.message,
        status: 'error',
        duration: 5000,
      });
    },
  });

  // Switch tokens
  const handleSwitchTokens = () => {
    const temp = fromToken;
    setFromToken(toToken);
    setToToken(temp);
    setInputAmount('');
    setOutputAmount('');
  };

  // Update output amount when quote changes
  useEffect(() => {
    if (quote) {
      setOutputAmount(quote.outputAmount.toString());
    }
  }, [quote]);

  return (
    <Card bg={cardBg} border="1px" borderColor={borderColor}>
      <CardBody>
        <VStack spacing={4}>
          <FormControl>
            <FormLabel>From</FormLabel>
            <VStack spacing={2}>
              <Select
                value={fromToken}
                onChange={(e) => setFromToken(e.target.value)}
                isDisabled={tokensLoading}
              >
                {tokens?.map((token) => (
                  <option key={token.id} value={token.symbol}>
                    {token.name} ({token.symbol})
                  </option>
                ))}
              </Select>
              <Input
                type="number"
                value={inputAmount}
                onChange={(e) => setInputAmount(e.target.value)}
                placeholder="0.0"
              />
              {tokens?.find(t => t.symbol === fromToken) && (
                <Text fontSize="sm" alignSelf="flex-end">
                  Balance: {tokens.find(t => t.symbol === fromToken)?.balance.toFixed(4)}
                </Text>
              )}
            </VStack>
          </FormControl>

          <IconButton
            aria-label="Switch tokens"
            icon={<FiArrowDown />}
            onClick={handleSwitchTokens}
            variant="ghost"
          />

          <FormControl>
            <FormLabel>To</FormLabel>
            <VStack spacing={2}>
              <Select
                value={toToken}
                onChange={(e) => setToToken(e.target.value)}
                isDisabled={tokensLoading}
              >
                {tokens?.map((token) => (
                  <option key={token.id} value={token.symbol}>
                    {token.name} ({token.symbol})
                  </option>
                ))}
              </Select>
              <Input
                type="number"
                value={outputAmount}
                isReadOnly
                placeholder="0.0"
              />
              {tokens?.find(t => t.symbol === toToken) && (
                <Text fontSize="sm" alignSelf="flex-end">
                  Balance: {tokens.find(t => t.symbol === toToken)?.balance.toFixed(4)}
                </Text>
              )}
            </VStack>
          </FormControl>

          <Divider />

          {quoteLoading ? (
            <Skeleton height="20px" />
          ) : quote && (
            <VStack w="full" spacing={2}>
              <HStack justify="space-between" w="full">
                <Text fontSize="sm">Price</Text>
                <Text fontSize="sm">
                  1 {fromToken} = {quote.price.toFixed(4)} {toToken}
                </Text>
              </HStack>
              <HStack justify="space-between" w="full">
                <Text fontSize="sm">Price Impact</Text>
                <Text fontSize="sm" color={quote.priceImpact > 5 ? 'red.500' : 'inherit'}>
                  {quote.priceImpact.toFixed(2)}%
                </Text>
              </HStack>
              <HStack justify="space-between" w="full">
                <Text fontSize="sm">Fee</Text>
                <Text fontSize="sm">{quote.fee.toFixed(4)} {fromToken}</Text>
              </HStack>
            </VStack>
          )}

          <FormControl>
            <FormLabel>Slippage Tolerance</FormLabel>
            <HStack>
              <Input
                type="number"
                value={slippage}
                onChange={(e) => setSlippage(e.target.value)}
                placeholder="0.5"
                w="100px"
              />
              <Text>%</Text>
            </HStack>
          </FormControl>

          <Button
            colorScheme="blue"
            w="full"
            isLoading={swapMutation.isPending}
            isDisabled={!quote || !inputAmount || parseFloat(inputAmount) === 0}
            onClick={() => swapMutation.mutate()}
          >
            Swap
          </Button>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default TokenSwap; 