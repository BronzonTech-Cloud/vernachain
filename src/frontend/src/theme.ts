import { extendTheme } from '@chakra-ui/react';

export const theme = extendTheme({
  config: {
    initialColorMode: 'dark',
    useSystemColorMode: true,
  },
  colors: {
    brand: {
      50: '#E5F4FF',
      100: '#B8E1FF',
      200: '#8ACDFF',
      300: '#5CB9FF',
      400: '#2EA5FF',
      500: '#0091FF',
      600: '#0074CC',
      700: '#005799',
      800: '#003A66',
      900: '#001D33',
    },
    accent: {
      50: '#FFE5F4',
      100: '#FFB8E1',
      200: '#FF8ACD',
      300: '#FF5CB9',
      400: '#FF2EA5',
      500: '#FF0091',
      600: '#CC0074',
      700: '#990057',
      800: '#66003A',
      900: '#33001D',
    },
  },
  fonts: {
    heading: 'Space Grotesk, system-ui, sans-serif',
    body: 'Inter, system-ui, sans-serif',
    mono: 'JetBrains Mono, monospace',
  },
  components: {
    Button: {
      defaultProps: {
        colorScheme: 'brand',
      },
      variants: {
        solid: (props: any) => ({
          bg: props.colorScheme === 'brand' ? 'brand.500' : `${props.colorScheme}.500`,
          color: 'white',
          _hover: {
            bg: props.colorScheme === 'brand' ? 'brand.600' : `${props.colorScheme}.600`,
            transform: 'translateY(-1px)',
            boxShadow: 'lg',
          },
          _active: {
            transform: 'translateY(0)',
            boxShadow: 'md',
          },
        }),
      },
    },
    Card: {
      baseStyle: {
        container: {
          borderRadius: 'xl',
          boxShadow: 'xl',
          backdropFilter: 'blur(8px)',
          border: '1px solid',
          borderColor: 'whiteAlpha.200',
        },
      },
    },
    Stat: {
      baseStyle: {
        container: {
          padding: 4,
        },
        label: {
          fontSize: 'sm',
          fontWeight: 'medium',
          textTransform: 'uppercase',
          color: 'gray.500',
        },
        number: {
          fontSize: '2xl',
          fontWeight: 'bold',
          fontFamily: 'mono',
        },
        helpText: {
          fontSize: 'xs',
          color: 'gray.500',
        },
      },
    },
  },
  styles: {
    global: (props: any) => ({
      body: {
        bg: props.colorMode === 'dark' ? 'gray.900' : 'gray.50',
        backgroundImage: props.colorMode === 'dark' 
          ? 'radial-gradient(circle at 50% 0%, rgba(0, 145, 255, 0.15), transparent 50%)'
          : 'radial-gradient(circle at 50% 0%, rgba(0, 145, 255, 0.1), transparent 50%)',
      },
      '::-webkit-scrollbar': {
        width: '10px',
        height: '10px',
      },
      '::-webkit-scrollbar-track': {
        bg: props.colorMode === 'dark' ? 'gray.800' : 'gray.200',
      },
      '::-webkit-scrollbar-thumb': {
        bg: props.colorMode === 'dark' ? 'gray.600' : 'gray.400',
        borderRadius: 'full',
      },
    }),
  },
}); 