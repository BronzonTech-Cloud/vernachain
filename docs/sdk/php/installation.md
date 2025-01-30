# PHP SDK Installation

## Prerequisites
- PHP 8.1+
- Composer
- ext-json
- ext-gmp (for big number calculations)
- ext-curl (for HTTP requests)

## Installation

### Using Composer
```bash
composer require vernachain/sdk
```

### Manual Installation
```bash
git clone https://github.com/BronzonTech-Cloud/vernachain
cd vernachain/src/sdk/v2/php
composer install
```

## Basic Setup

### Autoloading
```php
require_once 'vendor/autoload.php';

use Vernachain\SDK\VernachainClient;
```

### Client Initialization
```php
$client = new VernachainClient([
    'node_url' => 'http://localhost:8545',
    'api_key' => 'your-api-key'
]);
```

## Configuration Options

### Client Configuration
```php
$config = [
    // Required
    'node_url' => 'http://localhost:8545',
    
    // Optional
    'api_key' => 'your-api-key',
    'timeout' => 30,              // Request timeout in seconds
    'retries' => 3,               // Number of retry attempts
    'logger' => $logger,          // PSR-3 logger implementation
    'network' => 'mainnet',       // Network identifier
    'verify_ssl' => true,         // SSL verification
];

$client = new VernachainClient($config);
```

### Environment Variables
The SDK can be configured using environment variables in your `.env` file:
```env
VERNACHAIN_NODE_URL=http://localhost:8545
VERNACHAIN_API_KEY=your-api-key
VERNACHAIN_TIMEOUT=30
VERNACHAIN_RETRIES=3
```

Loading environment variables:
```php
$dotenv = Dotenv\Dotenv::createImmutable(__DIR__);
$dotenv->load();

$client = new VernachainClient([
    'node_url' => $_ENV['VERNACHAIN_NODE_URL'],
    'api_key' => $_ENV['VERNACHAIN_API_KEY']
]);
```

## Verification

### Connection Test
```php
try {
    $status = $client->getNodeStatus();
    echo "Connected successfully: " . json_encode($status) . "\n";
} catch (Exception $e) {
    echo "Connection failed: " . $e->getMessage() . "\n";
}
```

### Version Check
```php
// Check SDK version
echo "SDK Version: " . VernachainClient::VERSION . "\n";

// Check node version compatibility
$nodeInfo = $client->getNodeInfo();
echo "Node Version: " . $nodeInfo['version'] . "\n";
```

## PHP Extensions

### Required Extensions
```bash
# Install required PHP extensions
sudo apt-get install php8.1-gmp php8.1-curl php8.1-mbstring

# Verify installations
php -m | grep -E 'gmp|curl|json|mbstring'
```

### Optional Extensions
```bash
# For better performance
sudo apt-get install php8.1-opcache

# For development
sudo apt-get install php8.1-xdebug
```

## Next Steps

After installation, you can:
1. Follow the [Basic Usage Guide](basic-usage.md)
2. Explore [Advanced Features](advanced-features.md)
3. Check the [API Reference](api-reference.md)

## Troubleshooting

### Common Installation Issues

1. **Composer Issues**
```bash
# Clear composer cache
composer clear-cache

# Update composer
composer self-update

# Install with verbose output
composer install -vvv
```

2. **Extension Issues**
```bash
# Check PHP configuration
php -i | grep "extension_dir"

# Verify extension loading
php -m

# Check error log
tail -f /var/log/php/error.log
```

3. **Permission Issues**
```bash
# Fix directory permissions
chmod -R 755 vendor/
chmod -R 644 composer.json composer.lock

# Fix ownership
chown -R www-data:www-data vendor/
```

### SSL Issues
```php
// Disable SSL verification (not recommended for production)
$client = new VernachainClient([
    'node_url' => 'http://localhost:8545',
    'verify_ssl' => false
]);

// Specify custom SSL certificate
$client = new VernachainClient([
    'node_url' => 'http://localhost:8545',
    'ssl_cert' => '/path/to/certificate.pem'
]);
```

### Getting Help
- Check [GitHub Issues](https://github.com/BronzonTech-Cloud/vernachain-php/issues)