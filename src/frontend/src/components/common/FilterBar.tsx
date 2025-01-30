import React from 'react';
import {
  Box,
  HStack,
  Input,
  Select,
  IconButton,
  useColorModeValue,
  Wrap,
  WrapItem,
  Tooltip,
  Badge,
} from '@chakra-ui/react';
import { FiX, FiSearch } from 'react-icons/fi';

export interface FilterOption {
  label: string;
  value: string;
  options?: { label: string; value: string }[];
}

interface FilterBarProps {
  filters: FilterOption[];
  activeFilters: Record<string, string>;
  onFilterChange: (filters: Record<string, string>) => void;
  searchPlaceholder?: string;
  onSearch?: (query: string) => void;
  searchValue?: string;
  showActiveFilters?: boolean;
}

const FilterBar: React.FC<FilterBarProps> = ({
  filters,
  activeFilters,
  onFilterChange,
  searchPlaceholder = 'Search...',
  onSearch,
  searchValue = '',
  showActiveFilters = true,
}) => {
  const bg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const handleFilterChange = (key: string, value: string) => {
    const newFilters = { ...activeFilters };
    if (value === '') {
      delete newFilters[key];
    } else {
      newFilters[key] = value;
    }
    onFilterChange(newFilters);
  };

  const clearFilter = (key: string) => {
    const newFilters = { ...activeFilters };
    delete newFilters[key];
    onFilterChange(newFilters);
  };

  const clearAllFilters = () => {
    onFilterChange({});
  };

  return (
    <Box>
      <Box
        p={4}
        bg={bg}
        borderRadius="md"
        borderWidth={1}
        borderColor={borderColor}
      >
        <Wrap spacing={4}>
          {onSearch && (
            <WrapItem>
              <HStack>
                <Input
                  placeholder={searchPlaceholder}
                  value={searchValue}
                  onChange={(e) => onSearch(e.target.value)}
                  width="auto"
                />
                <IconButton
                  aria-label="Search"
                  icon={<FiSearch />}
                  onClick={() => onSearch(searchValue)}
                />
              </HStack>
            </WrapItem>
          )}

          {filters.map((filter) => (
            <WrapItem key={filter.value}>
              {filter.options ? (
                <Select
                  placeholder={filter.label}
                  value={activeFilters[filter.value] || ''}
                  onChange={(e) => handleFilterChange(filter.value, e.target.value)}
                  width="auto"
                >
                  {filter.options.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </Select>
              ) : (
                <Input
                  placeholder={filter.label}
                  value={activeFilters[filter.value] || ''}
                  onChange={(e) => handleFilterChange(filter.value, e.target.value)}
                  width="auto"
                />
              )}
            </WrapItem>
          ))}

          {Object.keys(activeFilters).length > 0 && (
            <WrapItem>
              <Tooltip label="Clear all filters">
                <IconButton
                  aria-label="Clear filters"
                  icon={<FiX />}
                  onClick={clearAllFilters}
                  variant="ghost"
                />
              </Tooltip>
            </WrapItem>
          )}
        </Wrap>
      </Box>

      {showActiveFilters && Object.keys(activeFilters).length > 0 && (
        <Wrap spacing={2} mt={2}>
          {Object.entries(activeFilters).map(([key, value]) => {
            const filter = filters.find((f) => f.value === key);
            const option = filter?.options?.find((o) => o.value === value);
            return (
              <WrapItem key={key}>
                <Badge
                  display="flex"
                  alignItems="center"
                  px={2}
                  py={1}
                  borderRadius="full"
                  colorScheme="blue"
                >
                  {filter?.label}: {option?.label || value}
                  <IconButton
                    aria-label={`Clear ${filter?.label} filter`}
                    icon={<FiX />}
                    size="xs"
                    ml={1}
                    variant="ghost"
                    onClick={() => clearFilter(key)}
                  />
                </Badge>
              </WrapItem>
            );
          })}
        </Wrap>
      )}
    </Box>
  );
};

export default FilterBar; 