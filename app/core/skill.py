from typing import Any, Dict, Optional

from abstracts.skill import SkillStoreABC
from app.config.config import config
from models.agent import Agent, AgentData, AgentQuota
from models.skill import AgentSkillData, ThreadSkillData


class SkillStore(SkillStoreABC):
    """Implementation of skill data storage operations.

    This class provides concrete implementations for storing and retrieving
    skill-related data for both agents and threads.
    """

    @staticmethod
    def get_system_config(key: str) -> Any:
        # TODO: maybe need a whitelist here
        if hasattr(config, key):
            return getattr(config, key)
        return None

    @staticmethod
    async def get_agent_config(agent_id: str) -> Optional[Agent]:
        return await Agent.get(agent_id)

    @staticmethod
    async def get_agent_data(agent_id: str) -> Optional[AgentData]:
        return await AgentData.get(agent_id)

    @staticmethod
    async def set_agent_data(agent_id: str, data: Dict) -> None:
        return await AgentData.patch(agent_id, data)

    @staticmethod
    async def get_agent_quota(agent_id: str) -> Optional[AgentQuota]:
        return await AgentQuota.get(agent_id)

    @staticmethod
    async def get_agent_skill_data(
        agent_id: str, skill: str, key: str
    ) -> Optional[Dict[str, Any]]:
        """Get skill data for an agent.

        Args:
            agent_id: ID of the agent
            skill: Name of the skill
            key: Data key

        Returns:
            Dictionary containing the skill data if found, None otherwise
        """
        return await AgentSkillData.get(agent_id, skill, key)

    @staticmethod
    async def save_agent_skill_data(
        agent_id: str, skill: str, key: str, data: Dict[str, Any]
    ) -> None:
        """Save or update skill data for an agent.

        Args:
            agent_id: ID of the agent
            skill: Name of the skill
            key: Data key
            data: JSON data to store
        """
        skill_data = AgentSkillData(
            agent_id=agent_id,
            skill=skill,
            key=key,
            data=data,
        )
        await skill_data.save()

    @staticmethod
    async def get_thread_skill_data(
        thread_id: str, skill: str, key: str
    ) -> Optional[Dict[str, Any]]:
        """Get skill data for a thread.

        Args:
            thread_id: ID of the thread
            skill: Name of the skill
            key: Data key

        Returns:
            Dictionary containing the skill data if found, None otherwise
        """
        return await ThreadSkillData.get(thread_id, skill, key)

    @staticmethod
    async def save_thread_skill_data(
        thread_id: str,
        agent_id: str,
        skill: str,
        key: str,
        data: Dict[str, Any],
    ) -> None:
        """Save or update skill data for a thread.

        Args:
            thread_id: ID of the thread
            agent_id: ID of the agent that owns this thread
            skill: Name of the skill
            key: Data key
            data: JSON data to store
        """
        skill_data = ThreadSkillData(
            thread_id=thread_id,
            agent_id=agent_id,
            skill=skill,
            key=key,
            data=data,
        )
        await skill_data.save()


skill_store = SkillStore()
