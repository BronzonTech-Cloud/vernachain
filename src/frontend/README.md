# Vernachain Frontend

## Overview

The Vernachain frontend is a modern, React-based web application that provides a user interface for interacting with the Vernachain blockchain platform.

## Technology Stack

- React 18
- TypeScript
- Vite
- Chakra UI
- React Query
- React Router
- Axios

## Project Structure

```
src/
├── api/                 # API client and service modules
│   ├── auth.ts         # Authentication API
│   ├── client.ts       # Base API client configuration
│   ├── stats.ts        # Explorer and statistics API
│   └── tokens.ts       # Token management API
├── components/         # Reusable React components
├── pages/             # Page components and routes
├── hooks/             # Custom React hooks
├── theme.ts           # Chakra UI theme configuration
├── env.d.ts           # Environment variables type definitions
├── main.tsx          # Application entry point
└── App.tsx           # Root component

```

## API Integration

### Base Client (`client.ts`)

The API client is configured to work with three backend services:

1. **API Service** (`apiClient`)
   - Base URL: `VITE_API_URL` (default: http://localhost:8000)
   - Handles authentication and token management

2. **Explorer Service** (`explorerClient`)
   - Base URL: `VITE_EXPLORER_URL` (default: http://localhost:8001)
   - Provides blockchain explorer functionality

3. **Node Service** (`nodeClient`)
   - Base URL: `VITE_NODE_URL` (default: http://localhost:5001)
   - Direct blockchain node interaction

Features:
- Automatic error handling
- Authentication token management
- Request/response logging
- Service health checking

### Authentication (`auth.ts`)

Handles user authentication and management:
- Login/Logout
- Registration
- Password reset
- Two-factor authentication

### Token Management (`tokens.ts`)

Provides token-related functionality:
- Token creation
- Transfer operations
- Permission management
- Token analytics

### Statistics and Explorer (`stats.ts`)

Blockchain explorer features:
- Network statistics
- Block information
- Transaction history
- Validator data

## Development

### Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
```env
VITE_API_URL=http://localhost:8000
VITE_EXPLORER_URL=http://localhost:8001
VITE_NODE_URL=http://localhost:5001
VITE_API_KEY=your_api_key
```

3. Start development server:
```bash
npm run dev
```

### Available Scripts

- `npm run dev`: Start development server
- `npm run build`: Build for production
- `npm run preview`: Preview production build
- `npm run lint`: Run ESLint
- `npm run type-check`: Run TypeScript type checking

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| VITE_API_URL | API service URL | http://localhost:8000 |
| VITE_EXPLORER_URL | Explorer backend URL | http://localhost:8001 |
| VITE_NODE_URL | Blockchain node URL | http://localhost:5001 |
| VITE_API_KEY | API authentication key | development_key |

### Adding New Features

1. **New API Endpoint**
   - Add types to relevant API module
   - Create API function
   - Add error handling
   - Update documentation

2. **New Component**
   - Create component in `components/`
   - Add TypeScript interfaces
   - Include Chakra UI theming
   - Add to relevant page

3. **New Page**
   - Create page component in `pages/`
   - Add route to App.tsx
   - Include in navigation
   - Add data fetching logic

## Testing

1. **Unit Tests**
   - Component testing with React Testing Library
   - API module testing with Jest
   - Utility function testing

2. **Integration Tests**
   - Page component testing
   - API integration testing
   - Route testing

3. **E2E Tests**
   - User flow testing
   - API interaction testing
   - UI component testing

## Deployment

1. Build the application:
```bash
npm run build
```

2. Preview the build:
```bash
npm run preview
```

3. Deploy the `dist` directory to your hosting service

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Check service URLs in `.env`
   - Verify backend services are running
   - Check browser console for errors

2. **Build Errors**
   - Clear `node_modules` and reinstall
   - Verify TypeScript types
   - Check for lint errors

3. **Runtime Errors**
   - Check browser console
   - Verify API responses
   - Check React Query cache

## Best Practices

1. **Code Style**
   - Follow TypeScript best practices
   - Use functional components
   - Implement proper error handling
   - Add comprehensive documentation

2. **Performance**
   - Use React Query for caching
   - Implement lazy loading
   - Optimize bundle size
   - Monitor render performance

3. **Security**
   - Sanitize user input
   - Implement proper authentication
   - Handle sensitive data securely
   - Use HTTPS in production 