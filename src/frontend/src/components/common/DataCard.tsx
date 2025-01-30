import React from 'react';
import {
  Card,
  CardBody,
  CardHeader,
  CardProps,
  Heading,
  useColorModeValue,
  Skeleton,
  IconButton,
  Flex,
  Tooltip,
} from '@chakra-ui/react';
import { FiMaximize2, FiMinimize2, FiRefreshCw } from 'react-icons/fi';

interface DataCardProps extends Omit<CardProps, 'title'> {
  title: React.ReactNode;
  isLoading?: boolean;
  isExpandable?: boolean;
  onExpand?: () => void;
  isExpanded?: boolean;
  onRefresh?: () => void;
  showRefresh?: boolean;
  headerAction?: React.ReactNode;
}

const DataCard: React.FC<DataCardProps> = ({
  title,
  children,
  isLoading = false,
  isExpandable = false,
  onExpand,
  isExpanded = false,
  onRefresh,
  showRefresh = false,
  headerAction,
  ...props
}) => {
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const bg = useColorModeValue('white', 'gray.800');

  return (
    <Card
      bg={bg}
      borderColor={borderColor}
      borderWidth={1}
      {...props}
    >
      <CardHeader
        p={4}
        borderBottomWidth={1}
        borderColor={borderColor}
      >
        <Flex justify="space-between" align="center">
          <Heading size="md">
            {title}
          </Heading>
          <Flex gap={2}>
            {headerAction}
            {showRefresh && onRefresh && (
              <Tooltip label="Refresh data">
                <IconButton
                  aria-label="Refresh"
                  icon={<FiRefreshCw />}
                  size="sm"
                  variant="ghost"
                  onClick={onRefresh}
                />
              </Tooltip>
            )}
            {isExpandable && onExpand && (
              <Tooltip label={isExpanded ? 'Minimize' : 'Maximize'}>
                <IconButton
                  aria-label={isExpanded ? 'Minimize' : 'Maximize'}
                  icon={isExpanded ? <FiMinimize2 /> : <FiMaximize2 />}
                  size="sm"
                  variant="ghost"
                  onClick={onExpand}
                />
              </Tooltip>
            )}
          </Flex>
        </Flex>
      </CardHeader>
      <CardBody p={4}>
        <Skeleton isLoaded={!isLoading}>
          {children}
        </Skeleton>
      </CardBody>
    </Card>
  );
};

export default DataCard; 