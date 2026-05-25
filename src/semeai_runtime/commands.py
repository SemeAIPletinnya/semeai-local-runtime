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


CommandHandler = Callable[[str], CommandResult]


def help_command(_: str) -> CommandResult:
    """Return runtime help."""
    return CommandResult(
        handled=True,
        command_name="/help",
        output=(
            "Available commands:\n"
            "/help - show runtime help\n"
            "/tools - list controlled runtime tools\n"
            "/memory - inspect persistent runtime memory\n"
            "/read <path> - read an allowed local file\n"
            "exit / quit - stop the runtime"
        ),
        tool_name="runtime_help",
        tool_input="",
    )


def tools_command(_: str) -> CommandResult:
    """Return controlled tool list."""
    return CommandResult(
        handled=True,
        command_name="/tools",
        output=(
            "Controlled tools:\n"
            "- read_allowed_file: reads approved local files only\n"
            "- memory_inspection: summarizes persistent runtime memory\n"
            "- runtime_help: shows available runtime commands"
        ),
        tool_name="runtime_tools",
        tool_input="",
    )


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
    exact_handlers: dict[str, CommandHandler] = {
        "/help": help_command,
        "/tools": tools_command,
        "/memory": memory_command,
    }

    if prompt in exact_handlers:
        return exact_handlers[prompt](prompt)

    read_result = read_command(prompt)
    if read_result.handled:
        return read_result

    return unknown_slash_command(prompt)