import React, { useState, useCallback, useRef } from 'react';
import {
  Box,
  Input,
  InputGroup,
  InputLeftElement,
  InputRightElement,
  IconButton,
  Popover,
  PopoverTrigger,
  PopoverContent,
  PopoverBody,
  VStack,
  HStack,
  Text,
  Badge,
  Spinner,
  useColorModeValue,
  Flex,
  Select,
  Button,
} from '@chakra-ui/react';
import {
  FiSearch,
  FiFilter,
  FiX,
  FiClock,
  FiHash,
  FiUser,
  FiCheckCircle,
} from 'react-icons/fi';
import { useQuery } from '@tanstack/react-query';
import { statsAPI } from '../../api/stats';
import { useNavigate } from 'react-router-dom';
import { debounce } from 'lodash';

interface SearchResult {
  type: 'block' | 'transaction' | 'address' | 'validator';
  data: any;
}

const SearchBar: React.FC = () => {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [filter, setFilter] = useState<'all' | 'block' | 'transaction' | 'address' | 'validator'>('all');
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const bg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const { data: results, isLoading } = useQuery({
    queryKey: ['search', query, filter],
    queryFn: async () => {
      if (!query) return [];
      const response = await statsAPI.search(query);
      let searchResults: SearchResult[] = [];

      if (filter === 'all' || filter === 'block') {
        searchResults.push(...response.blocks.map(block => ({
          type: 'block' as const,
          data: block
        })));
      }

      if (filter === 'all' || filter === 'transaction') {
        searchResults.push(...response.transactions.map(tx => ({
          type: 'transaction' as const,
          data: tx
        })));
      }

      if (filter === 'all' || filter === 'address') {
        searchResults.push(...response.addresses.map(address => ({
          type: 'address' as const,
          data: address
        })));
      }

      if (filter === 'all' || filter === 'validator') {
        searchResults.push(...response.validators.map(validator => ({
          type: 'validator' as const,
          data: validator
        })));
      }

      return searchResults;
    },
    enabled: query.length >= 3,
  });

  const debouncedSearch = useCallback(
    debounce((value: string) => {
      setQuery(value);
      if (value.length >= 3) {
        setIsOpen(true);
      }
    }, 300),
    []
  );

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    debouncedSearch(value);
    if (!value) {
      setIsOpen(false);
    }
  };

  const handleResultClick = (result: SearchResult) => {
    setIsOpen(false);
    switch (result.type) {
      case 'block':
        navigate(`/block/${result.data.index}`);
        break;
      case 'transaction':
        navigate(`/transaction/${result.data.hash}`);
        break;
      case 'address':
        navigate(`/address/${result.data.address}`);
        break;
      case 'validator':
        navigate(`/validator/${result.data.address}`);
        break;
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'block':
        return FiHash;
      case 'transaction':
        return FiClock;
      case 'address':
        return FiUser;
      case 'validator':
        return FiCheckCircle;
      default:
        return FiHash;
    }
  };

  const getResultPreview = (result: SearchResult) => {
    switch (result.type) {
      case 'block':
        return `Block #${result.data.index}`;
      case 'transaction':
        return `${result.data.hash.slice(0, 16)}...`;
      case 'address':
        return `${result.data.address.slice(0, 16)}...`;
      case 'validator':
        return result.data.name || `${result.data.address.slice(0, 16)}...`;
      default:
        return '';
    }
  };

  return (
    <Box position="relative" width="100%" maxW="600px">
      <Popover
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        initialFocusRef={inputRef}
        placement="bottom"
        matchWidth
      >
        <PopoverTrigger>
          <InputGroup>
            <InputLeftElement>
              <FiSearch />
            </InputLeftElement>
            <Input
              ref={inputRef}
              placeholder="Search blocks, transactions, addresses, or validators..."
              onChange={handleInputChange}
              onFocus={() => query.length >= 3 && setIsOpen(true)}
              borderColor={borderColor}
              _focus={{
                borderColor: 'blue.500',
                boxShadow: 'none',
              }}
            />
            <InputRightElement width="auto">
              <HStack spacing={2} pr={2}>
                <Select
                  size="sm"
                  value={filter}
                  onChange={(e) => setFilter(e.target.value as any)}
                  width="auto"
                  variant="ghost"
                >
                  <option value="all">All</option>
                  <option value="block">Blocks</option>
                  <option value="transaction">Transactions</option>
                  <option value="address">Addresses</option>
                  <option value="validator">Validators</option>
                </Select>
                {query && (
                  <IconButton
                    aria-label="Clear search"
                    icon={<FiX />}
                    size="sm"
                    variant="ghost"
                    onClick={() => {
                      if (inputRef.current) {
                        inputRef.current.value = '';
                      }
                      setQuery('');
                      setIsOpen(false);
                    }}
                  />
                )}
              </HStack>
            </InputRightElement>
          </InputGroup>
        </PopoverTrigger>

        <PopoverContent bg={bg} borderColor={borderColor}>
          <PopoverBody p={0}>
            {isLoading ? (
              <Flex justify="center" align="center" py={4}>
                <Spinner />
              </Flex>
            ) : results?.length ? (
              <VStack spacing={0} align="stretch">
                {results.map((result, index) => {
                  const Icon = getIcon(result.type);
                  return (
                    <Box
                      key={index}
                      p={3}
                      cursor="pointer"
                      _hover={{ bg: useColorModeValue('gray.50', 'gray.700') }}
                      onClick={() => handleResultClick(result)}
                      borderBottomWidth={index < results.length - 1 ? 1 : 0}
                      borderColor={borderColor}
                    >
                      <HStack spacing={3}>
                        <Icon />
                        <VStack spacing={1} align="start">
                          <Text>{getResultPreview(result)}</Text>
                          <Badge
                            colorScheme={
                              result.type === 'block'
                                ? 'blue'
                                : result.type === 'transaction'
                                ? 'green'
                                : result.type === 'validator'
                                ? 'purple'
                                : 'gray'
                            }
                          >
                            {result.type}
                          </Badge>
                        </VStack>
                      </HStack>
                    </Box>
                  );
                })}
              </VStack>
            ) : query.length >= 3 ? (
              <Box p={4} textAlign="center">
                <Text color="gray.500">No results found</Text>
              </Box>
            ) : (
              <Box p={4} textAlign="center">
                <Text color="gray.500">
                  Enter at least 3 characters to search
                </Text>
              </Box>
            )}
          </PopoverBody>
        </PopoverContent>
      </Popover>
    </Box>
  );
};

export default SearchBar; 