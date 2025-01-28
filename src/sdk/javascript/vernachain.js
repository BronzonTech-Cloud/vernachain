/**
 * Vernachain JavaScript SDK.
 * 
 * This module provides a JavaScript interface for interacting with the Vernachain blockchain.
 */

class Transaction {
    constructor(data) {
        this.hash = data.hash;
        this.fromAddress = data.from_address;
        this.toAddress = data.to_address;
        this.value = data.value;
        this.timestamp = new Date(data.timestamp);
        this.status = data.status;
        this.blockNumber = data.block_number;
        this.gasUsed = data.gas_used;
    }
}

class Block {
    constructor(data) {
        this.number = data.number;
        this.hash = data.hash;
        this.timestamp = new Date(data.timestamp);
        this.transactions = data.transactions;
        this.validator = data.validator;
        this.size = data.size;
    }
}

class Contract {
    constructor(data) {
        this.address = data.address;
        this.creator = data.creator;
        this.creationTx = data.creation_tx;
        this.bytecode = data.bytecode;
        this.abi = data.abi;
    }
}

class VernachainSDK {
    /**
     * Initialize the SDK.
     * @param {string} apiUrl - Base URL for the API
     * @param {string} apiKey - API key for authentication
     */
    constructor(apiUrl, apiKey) {
        this.apiUrl = apiUrl.replace(/\/$/, '');
        this.headers = {
            'X-API-Key': apiKey,
            'Content-Type': 'application/json'
        };
    }

    /**
     * Make an API request.
     * @private
     */
    async _request(method, endpoint, data = null) {
        const options = {
            method,
            headers: this.headers
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(`${this.apiUrl}${endpoint}`, options);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API request failed');
        }

        return response.json();
    }

    /**
     * Get block details by ID.
     * @param {number} blockId - Block number
     * @returns {Promise<Block>}
     */
    async getBlock(blockId) {
        const data = await this._request('GET', `/api/v1/block/${blockId}`);
        return new Block(data);
    }

    /**
     * Get transaction details by hash.
     * @param {string} txHash - Transaction hash
     * @returns {Promise<Transaction>}
     */
    async getTransaction(txHash) {
        const data = await this._request('GET', `/api/v1/transaction/${txHash}`);
        return new Transaction(data);
    }

    /**
     * Get address balance.
     * @param {string} address - Wallet address
     * @returns {Promise<number>}
     */
    async getBalance(address) {
        const data = await this._request('GET', `/api/v1/address/${address}`);
        return parseFloat(data.balance);
    }

    /**
     * Send a transaction.
     * @param {Object} params - Transaction parameters
     * @returns {Promise<string>} Transaction hash
     */
    async sendTransaction({
        toAddress,
        value,
        privateKey,
        gasLimit = null,
        data = null
    }) {
        const payload = {
            to_address: toAddress,
            value,
            private_key: privateKey,
            gas_limit: gasLimit,
            data
        };

        const response = await this._request('POST', '/api/v1/transaction', payload);
        return response.transaction_hash;
    }

    /**
     * Deploy a smart contract.
     * @param {Object} params - Deployment parameters
     * @returns {Promise<string>} Contract address
     */
    async deployContract({
        bytecode,
        abi,
        constructorArgs = null,
        privateKey,
        gasLimit = null
    }) {
        const payload = {
            bytecode,
            abi,
            constructor_args: constructorArgs,
            private_key: privateKey,
            gas_limit: gasLimit
        };

        const response = await this._request('POST', '/api/v1/contract/deploy', payload);
        return response.contract_address;
    }

    /**
     * Call a contract function.
     * @param {Object} params - Call parameters
     * @returns {Promise<any>} Function result
     */
    async callContract({
        contractAddress,
        functionName,
        args,
        abi
    }) {
        const payload = {
            contract_address: contractAddress,
            function_name: functionName,
            args,
            abi
        };

        const response = await this._request(
            'POST',
            `/api/v1/contract/${contractAddress}/call`,
            payload
        );
        return response.result;
    }

    /**
     * Initiate a cross-chain transfer.
     * @param {Object} params - Transfer parameters
     * @returns {Promise<string>} Bridge transaction hash
     */
    async bridgeTransfer({
        fromChain,
        toChain,
        token,
        amount,
        toAddress,
        privateKey
    }) {
        const payload = {
            from_chain: fromChain,
            to_chain: toChain,
            token,
            amount,
            to_address: toAddress,
            private_key: privateKey
        };

        const response = await this._request('POST', '/api/v1/bridge/transfer', payload);
        return response.bridge_tx_hash;
    }

    /**
     * Get bridge transaction status.
     * @param {string} txHash - Bridge transaction hash
     * @returns {Promise<Object>}
     */
    async getBridgeTransaction(txHash) {
        return this._request('GET', `/api/v1/bridge/transaction/${txHash}`);
    }

    /**
     * Get network statistics.
     * @returns {Promise<Object>}
     */
    async getNetworkStats() {
        return this._request('GET', '/api/v1/stats');
    }

    /**
     * Get list of validators and their stats.
     * @returns {Promise<Array>}
     */
    async getValidators() {
        return this._request('GET', '/api/v1/validators');
    }
} 