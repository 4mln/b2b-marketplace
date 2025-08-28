# Wallet Plugin

The Wallet Plugin provides functionality for managing user wallets, handling deposits, withdrawals, transfers, and cashback in the B2B Marketplace platform.

## Features

- **Multiple Wallets**: Users can have multiple wallets with different currencies
- **Fiat and Crypto Support**: Support for both fiat (USD, EUR, etc.) and cryptocurrency (BTC, ETH, etc.) wallets
- **Transaction Types**:
  - Deposits
  - Withdrawals
  - Transfers between users
  - Cashback rewards
  - Fee handling
- **Balance Management**: Real-time balance tracking and updates
- **Transaction History**: Complete history of all wallet transactions

## API Endpoints

### Wallet Management

- `POST /api/v1/wallet/` - Create a new wallet
- `GET /api/v1/wallet/user/{user_id}` - Get all wallets for a specific user
- `GET /api/v1/wallet/me` - Get all wallets for the current user
- `GET /api/v1/wallet/{wallet_id}` - Get a specific wallet
- `PATCH /api/v1/wallet/{wallet_id}` - Update a wallet (admin only)
- `GET /api/v1/wallet/{wallet_id}/transactions` - Get all transactions for a wallet

### Financial Operations

- `POST /api/v1/wallet/deposit` - Deposit funds into a wallet
- `POST /api/v1/wallet/withdraw` - Withdraw funds from a wallet
- `POST /api/v1/wallet/transfer` - Transfer funds between wallets

## Models

### Wallet

- `id`: Unique identifier
- `user_id`: User who owns the wallet
- `currency`: Currency code (USD, EUR, BTC, etc.)
- `currency_type`: Type of currency (fiat or crypto)
- `balance`: Current balance
- `is_active`: Whether the wallet is active
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Transaction

- `id`: Unique identifier
- `wallet_id`: Associated wallet
- `amount`: Transaction amount (positive for deposits, negative for withdrawals)
- `transaction_type`: Type of transaction (deposit, withdrawal, transfer, cashback, fee)
- `reference`: External reference (optional)
- `description`: Transaction description
- `status`: Transaction status (pending, completed, failed)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Configuration

The wallet plugin can be configured with the following settings:

- `default_currency`: Default currency for new wallets (default: USD)
- `cashback_percentage`: Default cashback percentage for transactions (default: 1.0%)
- `withdrawal_fee_percentage`: Fee percentage for withdrawals (default: 0.5%)
- `min_withdrawal`: Minimum withdrawal amount (default: 10.0)
- `supported_currencies`: List of supported currencies (default: ["USD", "EUR", "BTC", "ETH"])
- `crypto_currencies`: List of supported crypto currencies (default: ["BTC", "ETH"])

## Integration with Other Plugins

The Wallet plugin integrates with other plugins in the B2B Marketplace platform:

- **Auth Plugin**: Uses the User model for wallet ownership
- **Payments Plugin**: Can be used for processing deposits and withdrawals
- **Marketplace Plugin**: For handling payments for inquiries, tenders, and other marketplace features

## Future Enhancements

- Currency conversion between different wallet types
- Scheduled payments and recurring transfers
- Advanced reporting and analytics
- Integration with external payment gateways and cryptocurrency exchanges
- Multi-signature wallets for enhanced security