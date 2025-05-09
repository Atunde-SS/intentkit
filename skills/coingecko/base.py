from typing import Optional, Type

from pydantic import BaseModel, Field

from abstracts.skill import SkillStoreABC
from skills.base import IntentKitSkill


class CoinGeckoBaseTool(IntentKitSkill):
    """Base class for CoinGecko market data tools."""

    name: str = Field(description="The name of the tool")
    description: str = Field(description="Tool description")
    args_schema: Type[BaseModel]
    skill_store: SkillStoreABC = Field(description="Skill store for persistence")
    api_base: str = "https://api.coingecko.com/api/v3"
    api_key: Optional[str] = Field(
        default="", description="Optional API key for premium endpoints"
    )

    @property
    def category(self) -> str:
        return "coingecko"
