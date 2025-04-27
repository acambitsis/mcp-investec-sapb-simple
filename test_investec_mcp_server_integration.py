import json
import os
from datetime import datetime, timedelta

import pytest
import pytest_asyncio

from server import (
    get_access_token,
    get_account_balance,
    get_account_transactions,
    get_accounts,
    get_beneficiaries,
    get_beneficiary_categories,
    get_documents,
    get_pending_transactions,
    get_profile_accounts,
    get_profile_beneficiaries,
    get_profiles,
)

# Skip all tests if not using sandbox
pytestmark = pytest.mark.skipif(
    os.getenv("USE_SANDBOX") != "true",
    reason="Integration tests require sandbox environment",
)


@pytest_asyncio.fixture(scope="module")
async def test_account_id():
    """Get a test account ID from the sandbox environment."""
    accounts = await get_accounts()
    accounts_data = json.loads(accounts)
    if not accounts_data.get("data", {}).get("accounts"):
        pytest.skip("No accounts available in sandbox environment")
    return accounts_data["data"]["accounts"][0]["accountId"]


@pytest_asyncio.fixture(scope="module")
async def test_profile_id():
    """Get a test profile ID from the sandbox environment."""
    profiles = await get_profiles()
    profiles_data = json.loads(profiles)
    if not profiles_data.get("data"):
        pytest.skip("No profiles available in sandbox environment")
    return profiles_data["data"][0]["profileId"]


@pytest.mark.asyncio
async def test_get_access_token_integration():
    """Test getting access token from sandbox."""
    token = await get_access_token()
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.asyncio
async def test_get_accounts_integration():
    """Test getting accounts from sandbox."""
    result = await get_accounts()
    data = json.loads(result)
    assert "data" in data
    assert "accounts" in data["data"]
    assert isinstance(data["data"]["accounts"], list)
    if data["data"]["accounts"]:
        account = data["data"]["accounts"][0]
        assert "accountId" in account
        assert "accountName" in account
        assert "accountNumber" in account


@pytest.mark.asyncio
async def test_get_account_balance_integration(test_account_id):
    """Test getting account balance from sandbox."""
    result = await get_account_balance(test_account_id)
    data = json.loads(result)
    assert "data" in data
    assert "currentBalance" in data["data"]
    assert "availableBalance" in data["data"]
    assert "currency" in data["data"]


@pytest.mark.asyncio
async def test_get_account_transactions_integration(test_account_id):
    """Test getting account transactions from sandbox."""
    # Get transactions for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    result = await get_account_transactions(
        test_account_id,
        fromDate=start_date.strftime("%Y-%m-%d"),
        toDate=end_date.strftime("%Y-%m-%d"),
    )
    data = json.loads(result)
    assert "data" in data
    assert "transactions" in data["data"]
    assert isinstance(data["data"]["transactions"], list)


@pytest.mark.asyncio
async def test_get_pending_transactions_integration(test_account_id):
    """Test getting pending transactions from sandbox."""
    result = await get_pending_transactions(test_account_id)
    data = json.loads(result)
    assert "data" in data
    assert "transactions" in data["data"]
    assert isinstance(data["data"]["transactions"], list)


@pytest.mark.asyncio
async def test_get_profiles_integration():
    """Test getting profiles from sandbox."""
    result = await get_profiles()
    data = json.loads(result)
    assert "data" in data
    assert isinstance(data["data"], list)
    if data["data"]:
        profile = data["data"][0]
        assert "profileId" in profile
        assert "profileName" in profile


@pytest.mark.asyncio
async def test_get_profile_accounts_integration(test_profile_id):
    """Test getting profile accounts from sandbox."""
    result = await get_profile_accounts(test_profile_id)
    data = json.loads(result)
    assert "data" in data
    assert isinstance(data["data"], list)
    if data["data"]:
        account = data["data"][0]
        assert "accountId" in account
        assert "accountName" in account
        assert "accountNumber" in account


@pytest.mark.asyncio
async def test_get_beneficiaries_integration():
    """Test getting beneficiaries from sandbox."""
    result = await get_beneficiaries()
    data = json.loads(result)
    assert "data" in data
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_get_beneficiary_categories_integration():
    """Test getting beneficiary categories from sandbox."""
    result = await get_beneficiary_categories()
    data = json.loads(result)
    assert "data" in data
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_get_profile_beneficiaries_integration(test_profile_id, test_account_id):
    """Test getting profile beneficiaries from sandbox."""
    result = await get_profile_beneficiaries(test_profile_id, test_account_id)
    data = json.loads(result)
    assert "data" in data
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_get_documents_integration(test_account_id):
    """Test getting documents from sandbox."""
    # Get documents for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    result = await get_documents(
        test_account_id,
        fromDate=start_date.strftime("%Y-%m-%d"),
        toDate=end_date.strftime("%Y-%m-%d"),
    )
    data = json.loads(result)
    assert "data" in data

    # The response might be an empty list if no documents exist
    if isinstance(data["data"], list):
        assert data["data"] == []  # Empty list of documents is valid
    else:
        # If it's not an empty list, it should have the expected structure
        assert "documents" in data["data"]
        assert isinstance(data["data"]["documents"], list)
