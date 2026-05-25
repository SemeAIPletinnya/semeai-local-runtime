from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeCapability:
    tool_name: str
    description: str
    requires_policy: bool
    requires_mode: bool
    replay_logged: bool
    governed: bool


CAPABILITY_MANIFEST: dict[str, RuntimeCapability] = {
    "runtime_help": RuntimeCapability(
        tool_name="runtime_help",
        description="Displays runtime command help and available capabilities.",
        requires_policy=False,
        requires_mode=False,
        replay_logged=True,
        governed=False,
    ),
    "runtime_tools": RuntimeCapability(
        tool_name="runtime_tools",
        description="Displays registered runtime tools and governance surface.",
        requires_policy=False,
        requires_mode=False,
        replay_logged=True,
        governed=False,
    ),
    "runtime_config": RuntimeCapability(
        tool_name="runtime_config",
        description="Displays active runtime configuration.",
        requires_policy=False,
        requires_mode=True,
        replay_logged=True,
        governed=True,
    ),
    "runtime_mode": RuntimeCapability(
        tool_name="runtime_mode",
        description="Displays active runtime execution mode.",
        requires_policy=False,
        requires_mode=True,
        replay_logged=True,
        governed=True,
    ),
    "policy_registry": RuntimeCapability(
        tool_name="policy_registry",
        description="Displays active runtime governance policies.",
        requires_policy=True,
        requires_mode=True,
        replay_logged=True,
        governed=True,
    ),
    "memory_inspection": RuntimeCapability(
        tool_name="memory_inspection",
        description="Displays persistent runtime memory state.",
        requires_policy=True,
        requires_mode=True,
        replay_logged=True,
        governed=True,
    ),
    "read_allowed_file": RuntimeCapability(
        tool_name="read_allowed_file",
        description="Reads an approved local file through runtime policy evaluation.",
        requires_policy=True,
        requires_mode=True,
        replay_logged=True,
        governed=True,
    ),
    "unknown_command": RuntimeCapability(
        tool_name="unknown_command",
        description="Handles unsupported runtime slash commands.",
        requires_policy=False,
        requires_mode=False,
        replay_logged=True,
        governed=False,
    ),
}


def format_capability_manifest() -> str:
    """Format runtime capability manifest for inspection."""
    lines = ["Runtime capability manifest:"]

    for capability in CAPABILITY_MANIFEST.values():
        lines.append("")
        lines.append(f"tool_name: {capability.tool_name}")
        lines.append(f"description: {capability.description}")
        lines.append(f"requires_policy: {capability.requires_policy}")
        lines.append(f"requires_mode: {capability.requires_mode}")
        lines.append(f"replay_logged: {capability.replay_logged}")
        lines.append(f"governed: {capability.governed}")

    return "\n".join(lines)