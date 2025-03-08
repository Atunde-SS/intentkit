"""Common utility skills."""

from typing import TypedDict

from abstracts.skill import SkillStoreABC
from skills.base import SkillConfig, SkillState
from skills.common.base import CommonBaseTool
from skills.common.current_time import CurrentTime

# Cache skills at the system level, because they are stateless
_cache: dict[str, CommonBaseTool] = {}


class SkillStates(TypedDict):
    current_time: SkillState


class Config(SkillConfig):
    """Configuration for common utility skills."""

    states: SkillStates


def get_skills(
    config: "Config",
    is_private: bool,
    store: SkillStoreABC,
    **_,
) -> list[CommonBaseTool]:
    """Get all common utility skills.

    Args:
        config: The configuration for common utility skills.
        is_private: Whether to include private skills.
        store: The skill store for persisting data.

    Returns:
        A list of common utility skills.
    """
    available_skills = []

    # Include skills based on their state
    for skill_name, state in config["states"].items():
        if state == "disabled":
            continue
        elif state == "public" or (state == "private" and is_private):
            available_skills.append(skill_name)

    # Get each skill using the cached getter
    return [get_common_skill(name, store) for name in available_skills]


def get_common_skill(
    name: str,
    store: SkillStoreABC,
) -> CommonBaseTool:
    """Get a common utility skill by name.

    Args:
        name: The name of the skill to get
        store: The skill store for persisting data

    Returns:
        The requested common utility skill

    Raises:
        ValueError: If the requested skill name is unknown
    """
    if name == "current_time":
        if name not in _cache:
            _cache[name] = CurrentTime(
                skill_store=store,
            )
        return _cache[name]
    else:
        raise ValueError(f"Unknown common skill: {name}")
