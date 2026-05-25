from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from semeai_runtime.session_memory import (
    format_memory_summary,
    load_session_memory,
)
from semeai_runtime.tools import read_allowed_file


@dataclass(frozen=True)
class CommandResult:
    handled: bool
    command_name: str
    output: str
    tool_name: str
    tool_input: str


@dataclass(frozen=True)
class CommandSpec:
    name: str
    description: str
    tool_name: str
    handler: Callable[[str], CommandResult]


def memory_command(_: str) -> CommandResult:
    """Inspect persistent memory."""
    memory = load_session_memory()
    result = format_memory_summary(memory)

    return CommandResult(
        handled=True,
        command_name="/memory",
        output=result,
        tool_name="memory_inspection",
        tool_input="persistent_runtime_memory",
    )


def read_command(prompt: str) -> CommandResult:
    """Read an allowed local file."""
    if not prompt.startswith("/read "):
        return CommandResult(
            handled=False,
            command_name="",
            output="",
            tool_name="",
            tool_input="",
        )

    path = prompt[len("/read ") :].strip()
    result = read_allowed_file(path)

    return CommandResult(
        handled=True,
        command_name="/read",
        output=result,
        tool_name="read_allowed_file",
        tool_input=path,
    )


def unavailable_direct_command(prompt: str) -> CommandResult:
    """Placeholder for commands handled directly by metadata commands."""
    return CommandResult(
        handled=False,
        command_name="",
        output=f"Command not directly available: {prompt}",
        tool_name="",
        tool_input="",
    )


COMMAND_SPECS: dict[str, CommandSpec] = {
    "/help": CommandSpec(
        name="/help",
        description="Show runtime help and available commands.",
        tool_name="runtime_help",
        handler=unavailable_direct_command,
    ),
    "/tools": CommandSpec(
        name="/tools",
        description="List controlled runtime tools exposed through the command registry.",
        tool_name="runtime_tools",
        handler=unavailable_direct_command,
    ),
    "/memory": CommandSpec(
        name="/memory",
        description="Inspect persistent runtime memory.",
        tool_name="memory_inspection",
        handler=memory_command,
    ),
    "/read": CommandSpec(
        name="/read <path>",
        description="Read an approved local file through controlled file inspection.",
        tool_name="read_allowed_file",
        handler=read_command,
    ),
}


def format_help() -> str:
    """Build help text from command metadata."""
    lines = ["Available commands:"]

    for spec in COMMAND_SPECS.values():
        lines.append(f"{spec.name} - {spec.description}")

    lines.append("exit / quit - stop the runtime")

    return "\n".join(lines)


def format_tools() -> str:
    """Build controlled tool list from command metadata."""
    lines = ["Controlled tools:"]

    seen: set[str] = set()

    for spec in COMMAND_SPECS.values():
        if spec.tool_name in seen:
            continue

        seen.add(spec.tool_name)
        lines.append(f"- {spec.tool_name}: {spec.description}")

    return "\n".join(lines)


def help_command(_: str) -> CommandResult:
    """Return runtime help."""
    return CommandResult(
        handled=True,
        command_name="/help",
        output=format_help(),
        tool_name="runtime_help",
        tool_input="",
    )


def tools_command(_: str) -> CommandResult:
    """Return controlled tool list."""
    return CommandResult(
        handled=True,
        command_name="/tools",
        output=format_tools(),
        tool_name="runtime_tools",
        tool_input="",
    )


def unknown_slash_command(prompt: str) -> CommandResult:
    """Handle unknown slash commands."""
    if not prompt.startswith("/"):
        return CommandResult(
            handled=False,
            command_name="",
            output="",
            tool_name="",
            tool_input="",
        )

    return CommandResult(
        handled=True,
        command_name="unknown",
        output=f"Unknown command: {prompt}\nUse /help to see available commands.",
        tool_name="unknown_command",
        tool_input=prompt,
    )


def handle_command(prompt: str) -> CommandResult:
    """Dispatch runtime slash commands."""
    if prompt == "/help":
        return help_command(prompt)

    if prompt == "/tools":
        return tools_command(prompt)

    if prompt == "/memory":
        return COMMAND_SPECS["/memory"].handler(prompt)

    if prompt.startswith("/read "):
        return COMMAND_SPECS["/read"].handler(prompt)

    return unknown_slash_command(prompt)