#!/usr/bin/env python
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()
# Configuration
CLIENT_ID = os.getenv("CLIENT_ID", "")  # Default to empty string instead of None
CLIENT_SECRET = os.getenv(
    "CLIENT_SECRET", ""
)  # Default to empty string instead of None
API_KEY = os.getenv("API_KEY", "")  # Default to empty string instead of None
if os.getenv("USE_SANDBOX") == "true":
    BASE_URL = "https://openapisandbox.investec.com"
else:
    BASE_URL = "https://openapi.investec.com"

# Debug print credentials
print("DEBUG - Loaded credentials:", file=sys.stderr)
print(f"DEBUG - CLIENT_ID: {CLIENT_ID}", file=sys.stderr)
print(
    f"DEBUG - CLIENT_SECRET: {CLIENT_SECRET[:3]}...{CLIENT_SECRET[-3:]}",
    file=sys.stderr,
)
print(f"DEBUG - API_KEY: {API_KEY[:10]}...{API_KEY[-10:]}", file=sys.stderr)
print(f"DEBUG - BASE_URL: {BASE_URL}", file=sys.stderr)

# Initialize FastMCP server
mcp = FastMCP("investec")

# Token storage
access_token = None
token_expiry = None


async def get_access_token() -> str:
    """Get a valid access token, requesting a new one if needed."""
    global access_token, token_expiry

    current_time = datetime.now()
    if access_token and token_expiry and token_expiry > current_time:
        print(
            f"DEBUG - Using cached token (expires at {token_expiry})", file=sys.stderr
        )
        return access_token

    # Request new token
    token_url = f"{BASE_URL}/identity/v2/oauth2/token"
    auth = httpx.BasicAuth(CLIENT_ID, CLIENT_SECRET)
    headers = {"x-api-key": API_KEY}  # API_KEY is now guaranteed to be a string
    data = {"grant_type": "client_credentials"}

    print(f"DEBUG - Requesting new token from: {token_url}", file=sys.stderr)
    print(f"DEBUG - Headers: {headers}", file=sys.stderr)
    print(f"DEBUG - Data: {data}", file=sys.stderr)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_url, auth=auth, headers=headers, data=data
            )
            print(f"DEBUG - Response status: {response.status_code}", file=sys.stderr)

            if response.status_code != 200:
                print(f"DEBUG - Error response body: {response.text}", file=sys.stderr)

            response.raise_for_status()
            result = response.json()
            print("DEBUG - Token received successfully", file=sys.stderr)

            access_token = result["access_token"]
            # Token is valid for result["expires_in"] seconds
            token_expiry = datetime.now() + timedelta(
                seconds=result["expires_in"] - 60
            )  # Buffer of 60 seconds
            print(f"DEBUG - Token will expire at: {token_expiry}", file=sys.stderr)

        return access_token
    except Exception as e:
        print(f"DEBUG - Exception during token request: {str(e)}", file=sys.stderr)
        raise


async def make_api_request(
    method: str,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Make an API request to the Investec API."""
    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    url = f"{BASE_URL}{endpoint}"

    async with httpx.AsyncClient() as client:
        if method.upper() == "GET":
            response = await client.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            headers["Content-Type"] = "application/json"
            response = await client.post(
                url, headers=headers, params=params, json=json_data
            )
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        return response.json()


# Account Information Tools


@mcp.tool()
async def get_accounts() -> str:
    """Get a list of accounts with metadata."""
    result = await make_api_request("GET", "/za/pb/v1/accounts")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_account_balance(accountId: str) -> str:
    """Get the balance of a specific account.

    Args:
        accountId: The unique identifier for the account
    """
    result = await make_api_request("GET", f"/za/pb/v1/accounts/{accountId}/balance")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_account_transactions(
    accountId: str,
    fromDate: str = "",
    toDate: str = "",
    transactionType: Optional[str] = None,
    includePending: Optional[bool] = False,
) -> str:
    """Get transactions for a specific account.

    Args:
        accountId: The unique identifier for the account
        fromDate: Optional. Start date in YYYY-MM-DD format
        toDate: Optional. End date in YYYY-MM-DD format
        transactionType: Optional. Filter by transaction type
        includePending: Optional. Whether to include pending transactions
    """
    params = {}
    if fromDate:
        params["fromDate"] = fromDate
    if toDate:
        params["toDate"] = toDate
    if transactionType:
        params["transactionType"] = transactionType
    if includePending:
        params["includePending"] = "true"

    result = await make_api_request(
        "GET", f"/za/pb/v1/accounts/{accountId}/transactions", params=params
    )
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_pending_transactions(accountId: str) -> str:
    """Get pending transactions for a specific account.

    Args:
        accountId: The unique identifier for the account
    """
    result = await make_api_request(
        "GET", f"/za/pb/v1/accounts/{accountId}/pending-transactions"
    )
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_profiles() -> str:
    """Get a list of profiles."""
    result = await make_api_request("GET", "/za/pb/v1/profiles")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_profile_accounts(profileId: str) -> str:
    """Get accounts for a specific profile.

    Args:
        profileId: The unique identifier for the profile
    """
    result = await make_api_request("GET", f"/za/pb/v1/profiles/{profileId}/accounts")
    return json.dumps(result, indent=2)


# Beneficiary Tools


@mcp.tool()
async def get_beneficiaries() -> str:
    """Get a list of beneficiaries."""
    result = await make_api_request("GET", "/za/pb/v1/accounts/beneficiaries")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_beneficiary_categories() -> str:
    """Get a list of beneficiary categories."""
    result = await make_api_request("GET", "/za/pb/v1/accounts/beneficiarycategories")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_profile_beneficiaries(profileId: str, accountId: str) -> str:
    """Get beneficiaries for a specific profile and account.

    Args:
        profileId: The unique identifier for the profile
        accountId: The unique identifier for the account
    """
    result = await make_api_request(
        "GET", f"/za/pb/v1/profiles/{profileId}/accounts/{accountId}/beneficiaries"
    )
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_authorisation_setup_details(profileId: str, accountId: str) -> str:
    """Get authorisation setup details for a specific profile and account.

    Args:
        profileId: The unique identifier for the profile
        accountId: The unique identifier for the account
    """
    result = await make_api_request(
        "GET",
        f"/za/pb/v1/profiles/{profileId}/accounts/{accountId}/authorisationsetupdetails",
    )
    return json.dumps(result, indent=2)


# Transfer Tools


@mcp.tool()
async def transfer_multiple(
    accountId: str, transferList: list[dict[str, str]], profileId: str | None = None
) -> str:
    """
    Transfer funds to one or multiple accounts.

    Args:
        accountId: The account ID to transfer from.
        transferList: REQUIRED. List of transfers, each transfer must be a dict with the following keys:
            - beneficiaryAccountId: str - The account ID of the beneficiary
            - amount: str - Amount to transfer in ZAR format (e.g., '100.00')
            - myReference: str - Reference shown on sender's account
            - theirReference: str - Reference shown on recipient's account
        profileId: Optional profile ID for the transfer. Set to None if not needed.
            Do not include this parameter in your request if you don't need it.
            When included in the request, it must be sent as null or a valid profile ID string.

    Returns:
        str: JSON string of the API response.
    """
    data: dict[str, Any] = {"transferList": transferList}
    if profileId is not None:
        # Only include profileId if it is not None
        data["profileId"] = profileId
        print(
            f"DEBUG - Including profileId in transfer_multiple: {profileId}",
            file=sys.stderr,
        )
    else:
        print(
            "DEBUG - profileId not included in transfer_multiple payload",
            file=sys.stderr,
        )

    result = await make_api_request(
        "POST", f"/za/pb/v1/accounts/{accountId}/transfermultiple", json_data=data
    )
    return json.dumps(result, indent=2)


@mcp.tool()
async def pay_multiple(accountId: str, paymentList: List[Dict[str, Any]]) -> str:
    """Pay funds to one or multiple beneficiaries.

    Args:
        accountId: The account ID to pay from
        paymentList: List of payments with beneficiaryId, amount, myReference, theirReference
    """
    data = {"paymentList": paymentList}

    result = await make_api_request(
        "POST", f"/za/pb/v1/accounts/{accountId}/paymultiple", json_data=data
    )
    return json.dumps(result, indent=2)


# Document Tools


@mcp.tool()
async def get_documents(accountId: str, fromDate: str, toDate: str) -> str:
    """Get a list of documents for a specific account.

    Args:
        accountId: The unique identifier for the account
        fromDate: Start date in YYYY-MM-DD format
        toDate: End date in YYYY-MM-DD format
    """
    params = {"fromDate": fromDate, "toDate": toDate}

    result = await make_api_request(
        "GET", f"/za/pb/v1/accounts/{accountId}/documents", params=params
    )
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_document(accountId: str, documentType: str, documentDate: str) -> str:
    """Get a specific document.

    Args:
        accountId: The unique identifier for the account
        documentType: The type of document (e.g., 'Statement')
        documentDate: The date of the document in YYYY-MM-DD format
    """
    result = await make_api_request(
        "GET", f"/za/pb/v1/accounts/{accountId}/document/{documentType}/{documentDate}"
    )
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    # Run the server with standard I/O transport
    mcp.run(transport="stdio")
