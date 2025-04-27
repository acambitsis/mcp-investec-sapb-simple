# Investec API MCP Server

This is a Model Context Protocol (MCP) server that provides tools for interacting with the Investec API.

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy the `.env.example` file to `.env` and add your Investec API credentials:
   ```
   cp .env.example .env
   ```
4. Edit the `.env` file and add your Investec API credentials:
   ```
   CLIENT_ID=your-client-id
   CLIENT_SECRET=your-client-secret
   API_KEY=your-api-key
   BASE_URL=https://openapisandbox.investec.com  # or https://openapi.investec.com for production
   ```

## Running the Server

Run the server using:

```
python investec_mcp_server.py
```

## Connecting to Claude for Desktop

To connect this MCP server to Claude for Desktop:

1. Make sure you have Claude for Desktop installed (download from the Anthropic website)
2. Open your Claude for Desktop App configuration at:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%AppData%\Claude\claude_desktop_config.json`
3. Add the server configuration:

```json
{
    "mcpServers": {
        "investec": {
            "command": "python",
            "args": [
                "/ABSOLUTE/PATH/TO/investec_mcp_server.py"
            ]
        }
    }
}
```

4. Save the file and restart Claude for Desktop
5. You should now see the Investec tools available in Claude

## Available Tools

The server provides the following tools:

### Account Information
- `get_accounts`: Get a list of accounts
- `get_account_balance`: Get the balance of a specific account
- `get_account_transactions`: Get transactions for a specific account
- `get_pending_transactions`: Get pending transactions for a specific account
- `get_profiles`: Get a list of profiles
- `get_profile_accounts`: Get accounts for a specific profile

### Beneficiaries
- `get_beneficiaries`: Get a list of beneficiaries
- `get_beneficiary_categories`: Get a list of beneficiary categories
- `get_profile_beneficiaries`: Get beneficiaries for a specific profile and account
- `get_authorisation_setup_details`: Get authorisation setup details

### Transfers
- `transfer_multiple`: Transfer funds to one or multiple accounts
- `pay_multiple`: Pay funds to one or multiple beneficiaries

### Documents
- `get_documents`: Get a list of documents for a specific account
- `get_document`: Get a specific document 