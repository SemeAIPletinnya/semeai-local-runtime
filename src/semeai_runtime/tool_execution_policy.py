from __future__ import annotations

from dataclasses import dataclass


ALLOW = "ALLOW"
NEEDS_REVIEW = "NEEDS_REVIEW"
DENY = "DENY"

SAFE = "SAFE"
DEVELOPMENT = "DEVELOPMENT"
STRICT = "STRICT"

READ_ONLY_TERMS = (
    "read",
    "inspect",
    "list",
    "show",
    "summarize",
)

WRITE_CONFIG_TERMS = (
    "write",
    "modify",
    "edit",
    "save",
    "update config",
    "change config",
)

DESTRUCTIVE_BYPASS_TERMS = (
    "delete production data",
    "bypass approval",
    "remove safety",
    "disable review",
    "wipe",
)


@dataclass(frozen=True)
class ToolExecutionDecision:
    decision: str
    allowed: bool
    reason: str
    runtime_mode: str
    tool_name: str
    action: str


def evaluate_tool_execution(
    *,
    tool_name: str,
    action: str,
    runtime_mode: str = SAFE,
) -> ToolExecutionDecision:
    """Evaluate deterministic local mediation for a requested tool action."""
    normalized_mode = runtime_mode.upper()
    text = action.lower()

    if any(term in text for term in DESTRUCTIVE_BYPASS_TERMS):
        return ToolExecutionDecision(
            decision=DENY,
            allowed=False,
            reason="action contains destructive or approval-bypass language",
            runtime_mode=normalized_mode,
            tool_name=tool_name,
            action=action,
        )

    if normalized_mode not in {SAFE, DEVELOPMENT, STRICT}:
        return ToolExecutionDecision(
            decision=NEEDS_REVIEW,
            allowed=False,
            reason="unknown runtime mode requires conservative review",
            runtime_mode=normalized_mode,
            tool_name=tool_name,
            action=action,
        )

    is_read_only = any(term in text for term in READ_ONLY_TERMS)
    is_write_or_config = any(term in text for term in WRITE_CONFIG_TERMS)

    if normalized_mode == STRICT:
        if is_write_or_config:
            return ToolExecutionDecision(
                decision=DENY,
                allowed=False,
                reason="STRICT mode denies file write or config mutation actions",
                runtime_mode=normalized_mode,
                tool_name=tool_name,
                action=action,
            )

        if is_read_only:
            return ToolExecutionDecision(
                decision=NEEDS_REVIEW,
                allowed=False,
                reason="STRICT mode requires review for read-only inspection actions",
                runtime_mode=normalized_mode,
                tool_name=tool_name,
                action=action,
            )

        return ToolExecutionDecision(
            decision=NEEDS_REVIEW,
            allowed=False,
            reason="STRICT mode requires review for unclassified actions",
            runtime_mode=normalized_mode,
            tool_name=tool_name,
            action=action,
        )

    if is_write_or_config:
        return ToolExecutionDecision(
            decision=NEEDS_REVIEW,
            allowed=False,
            reason=f"{normalized_mode} mode requires review for file write or config mutation actions",
            runtime_mode=normalized_mode,
            tool_name=tool_name,
            action=action,
        )

    if is_read_only:
        return ToolExecutionDecision(
            decision=ALLOW,
            allowed=True,
            reason=f"{normalized_mode} mode allows read-only inspection actions",
            runtime_mode=normalized_mode,
            tool_name=tool_name,
            action=action,
        )

    return ToolExecutionDecision(
        decision=NEEDS_REVIEW,
        allowed=False,
        reason=f"{normalized_mode} mode requires review for unclassified actions",
        runtime_mode=normalized_mode,
        tool_name=tool_name,
        action=action,
    )
