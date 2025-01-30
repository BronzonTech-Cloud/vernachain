import React, { useState, useCallback } from 'react';
import {
  IconButton,
  IconButtonProps,
  Tooltip,
  useClipboard,
  useToast,
} from '@chakra-ui/react';
import { FiCopy, FiCheck } from 'react-icons/fi';

interface CopyButtonProps extends Omit<IconButtonProps, 'aria-label'> {
  text: string;
  tooltipText?: string;
  successMessage?: string;
  errorMessage?: string;
}

const CopyButton: React.FC<CopyButtonProps> = ({
  text,
  tooltipText = 'Copy to clipboard',
  successMessage = 'Copied to clipboard!',
  errorMessage = 'Failed to copy',
  ...props
}) => {
  const [showCheck, setShowCheck] = useState(false);
  const { onCopy } = useClipboard(text);
  const toast = useToast();

  const handleCopy = useCallback(() => {
    try {
      onCopy();
      setShowCheck(true);
      toast({
        title: successMessage,
        status: 'success',
        duration: 2000,
        isClosable: true,
        position: 'bottom-right',
      });
      setTimeout(() => setShowCheck(false), 2000);
    } catch (error) {
      toast({
        title: errorMessage,
        status: 'error',
        duration: 2000,
        isClosable: true,
        position: 'bottom-right',
      });
    }
  }, [onCopy, successMessage, errorMessage, toast]);

  return (
    <Tooltip label={tooltipText} hasArrow>
      <IconButton
        icon={showCheck ? <FiCheck /> : <FiCopy />}
        aria-label="Copy to clipboard"
        size="sm"
        variant="ghost"
        onClick={handleCopy}
        color={showCheck ? 'green.500' : undefined}
        {...props}
      />
    </Tooltip>
  );
};

export default CopyButton;