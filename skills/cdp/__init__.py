"""CDP wallet interaction skills."""

from typing import TypedDict

from coinbase_agentkit import (
    AgentKit,
    AgentKitConfig,
    CdpWalletProvider,
    basename_action_provider,
    cdp_api_action_provider,
    cdp_wallet_action_provider,
    erc20_action_provider,
    morpho_action_provider,
    pyth_action_provider,
    superfluid_action_provider,
    wallet_action_provider,
    weth_action_provider,
    wow_action_provider,
)
from coinbase_agentkit.action_providers.erc721 import erc721_action_provider
from coinbase_agentkit_langchain import get_langchain_tools

from abstracts.skill import SkillStoreABC
from clients import CdpClient, get_cdp_client
from skills.base import SkillConfig, SkillState
from skills.cdp.base import CDPBaseTool
from skills.cdp.get_balance import GetBalance

# Cache skills at the system level, because they are stateless
_cache: dict[str, CDPBaseTool] = {}


class SkillStates(TypedDict):
    get_balance: SkillState
    WalletActionProvider_get_balance: SkillState
    WalletActionProvider_get_wallet_details: SkillState
    WalletActionProvider_native_transfer: SkillState
    CdpApiActionProvider_address_reputation: SkillState
    CdpApiActionProvider_request_faucet_funds: SkillState
    CdpWalletActionProvider_deploy_contract: SkillState
    CdpWalletActionProvider_deploy_nft: SkillState
    CdpWalletActionProvider_deploy_token: SkillState
    CdpWalletActionProvider_trade: SkillState
    PythActionProvider_fetch_price: SkillState
    PythActionProvider_fetch_price_feed_id: SkillState
    BasenameActionProvider_register_basename: SkillState
    ERC20ActionProvider_get_balance: SkillState
    ERC20ActionProvider_transfer: SkillState
    Erc721ActionProvider_get_balance: SkillState
    Erc721ActionProvider_mint: SkillState
    Erc721ActionProvider_transfer: SkillState
    WethActionProvider_wrap_eth: SkillState
    MorphoActionProvider_deposit: SkillState
    MorphoActionProvider_withdraw: SkillState
    SuperfluidActionProvider_create_flow: SkillState
    SuperfluidActionProvider_delete_flow: SkillState
    SuperfluidActionProvider_update_flow: SkillState
    WowActionProvider_buy_token: SkillState
    WowActionProvider_create_token: SkillState
    WowActionProvider_sell_token: SkillState


class Config(SkillConfig):
    """Configuration for CDP skills."""

    states: SkillStates


# CDP skills is not stateless for agents, so we need agent_id here
# If you are skill contributor, please do not follow this pattern
def get_skills(
    config: "Config",
    is_private: bool,
    store: SkillStoreABC,
    agent_id: str,
    **_,
) -> list[CDPBaseTool]:
    """Get all CDP skills.

    Args:
        config: The configuration for CDP skills.
        is_private: Whether to include private skills.
        store: The skill store for persisting data.
        agent_id: The ID of the agent using the skills.

    Returns:
        A list of CDP skills.
    """
    available_skills = []

    # Include skills based on their state
    for skill_name, state in config["states"].items():
        if state == "disabled":
            continue
        elif state == "public" or (state == "private" and is_private):
            available_skills.append(skill_name)

    # Initialize CDP client
    cdp_client: CdpClient = get_cdp_client(agent_id, store)
    cdp_wallet_provider: CdpWalletProvider = cdp_client.get_wallet_provider()
    cdp_provider_config = cdp_client.get_provider_config()
    agent_kit = AgentKit(
        AgentKitConfig(
            wallet_provider=cdp_wallet_provider,
            action_providers=[
                wallet_action_provider(),
                cdp_api_action_provider(cdp_provider_config),
                cdp_wallet_action_provider(cdp_provider_config),
                pyth_action_provider(),
                basename_action_provider(),
                erc20_action_provider(),
                erc721_action_provider(),
                weth_action_provider(),
                morpho_action_provider(),
                superfluid_action_provider(),
                wow_action_provider(),
            ],
        )
    )
    cdp_tools = get_langchain_tools(agent_kit)
    tools = []
    for skill in available_skills:
        if skill == "get_balance":
            tools.append(
                GetBalance(
                    wallet=cdp_wallet_provider._wallet,
                    agent_id=agent_id,
                    skill_store=store,
                )
            )
            continue
        for tool in cdp_tools:
            if tool.name.endswith(skill):
                tools.append(tool)
    return tools
