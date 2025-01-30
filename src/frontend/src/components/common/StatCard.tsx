import React from 'react';
import {
  Box,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  useColorModeValue,
  Card,
  CardBody,
  Icon,
  Flex,
  Tooltip,
  Skeleton,
} from '@chakra-ui/react';
import { IconType } from 'react-icons';

interface StatCardProps {
  label: string;
  value: string | number;
  icon?: IconType;
  helpText?: string;
  change?: number;
  isLoading?: boolean;
  tooltipText?: string;
  iconColor?: string;
  bg?: string;
}

const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  icon,
  helpText,
  change,
  isLoading = false,
  tooltipText,
  iconColor,
  bg,
}) => {
  const bgCard = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const defaultIconColor = useColorModeValue('blue.500', 'blue.300');

  const content = (
    <Card
      bg={bg || bgCard}
      borderColor={borderColor}
      borderWidth={1}
      w="100%"
    >
      <CardBody>
        <Flex justify="space-between" align="flex-start">
          <Box flex="1">
            <Skeleton isLoaded={!isLoading}>
              <StatLabel color="gray.500">{label}</StatLabel>
              <StatNumber fontSize="2xl">{value}</StatNumber>
              {(helpText || typeof change !== 'undefined') && (
                <StatHelpText>
                  {typeof change !== 'undefined' && (
                    <StatArrow
                      type={change >= 0 ? 'increase' : 'decrease'}
                      color={change >= 0 ? 'green.500' : 'red.500'}
                    />
                  )}
                  {helpText}
                </StatHelpText>
              )}
            </Skeleton>
          </Box>
          {icon && (
            <Box
              p={2}
              borderRadius="md"
              bg={useColorModeValue('gray.50', 'gray.700')}
            >
              <Icon
                as={icon}
                boxSize={6}
                color={iconColor || defaultIconColor}
              />
            </Box>
          )}
        </Flex>
      </CardBody>
    </Card>
  );

  if (tooltipText) {
    return (
      <Tooltip label={tooltipText} hasArrow>
        {content}
      </Tooltip>
    );
  }

  return content;
};

export default StatCard;