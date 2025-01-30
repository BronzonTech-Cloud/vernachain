import React from 'react';
import { Badge, BadgeProps, Tooltip } from '@chakra-ui/react';

interface StatusBadgeProps extends Omit<BadgeProps, 'colorScheme'> {
  status: 'success' | 'error' | 'warning' | 'info' | 'pending' | 'active' | 'inactive';
  showTooltip?: boolean;
  tooltipText?: string;
}

const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  showTooltip = true,
  tooltipText,
  ...props
}) => {
  const getColorScheme = () => {
    switch (status) {
      case 'success':
      case 'active':
        return 'green';
      case 'error':
        return 'red';
      case 'warning':
        return 'yellow';
      case 'info':
        return 'blue';
      case 'pending':
        return 'orange';
      case 'inactive':
        return 'gray';
      default:
        return 'gray';
    }
  };

  const getDefaultTooltip = () => {
    switch (status) {
      case 'success':
        return 'Operation completed successfully';
      case 'error':
        return 'An error occurred';
      case 'warning':
        return 'Proceed with caution';
      case 'info':
        return 'Information';
      case 'pending':
        return 'Operation in progress';
      case 'active':
        return 'Currently active';
      case 'inactive':
        return 'Currently inactive';
      default:
        return '';
    }
  };

  const badge = (
    <Badge
      colorScheme={getColorScheme()}
      textTransform="capitalize"
      {...props}
    >
      {status}
    </Badge>
  );

  if (showTooltip) {
    return (
      <Tooltip
        label={tooltipText || getDefaultTooltip()}
        hasArrow
      >
        {badge}
      </Tooltip>
    );
  }

  return badge;
};

export default StatusBadge; 