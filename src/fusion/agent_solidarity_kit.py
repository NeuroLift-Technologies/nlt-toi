"""Agent Solidarity Kit primitives for the TOI agent.

This module provides a lightweight integration layer for running a
TOI-governed assistant with GitHub Models.
"""
from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from typing import Dict, List

from .toi_parser import TOIPreferences


@dataclass(frozen=True)
class SolidarityModelConfig:
    """Configuration for the GitHub Models endpoint used by the TOI agent."""

    model: str = "azureml/Phi-4-mini-instruct"
    endpoint: str = "https://models.inference.ai.azure.com/chat/completions"
    temperature: float = 0.3
    max_tokens: int = 600


@dataclass(frozen=True)
class TOIAgentSolidarityKit:
    """TOI-first agent runtime built with Agent Solidarity Kit conventions."""

    model_config: SolidarityModelConfig = SolidarityModelConfig()

    def build_system_prompt(self, toi: TOIPreferences) -> str:
        """Create a stable system prompt from TOI preferences."""
        toi_data = toi.to_dict()
        return (
            "You are the NeuroLift TOI Agent built with the Agent Solidarity Kit. "
            "Follow the provided Terms of Interaction exactly. "
            "Default to privacy-first, user agency, and neurodivergent-friendly communication. "
            "If a request conflicts with TOI, refuse and explain why briefly.\n\n"
            f"TOI Preferences:\n{json.dumps(toi_data, indent=2)}"
        )

    def build_messages(self, toi: TOIPreferences, user_message: str) -> List[Dict[str, str]]:
        """Build chat messages for GitHub Models."""
        return [
            {"role": "system", "content": self.build_system_prompt(toi)},
            {"role": "user", "content": user_message},
        ]

    def invoke(self, *, token: str, toi: TOIPreferences, user_message: str) -> str:
        """Invoke the configured GitHub Models endpoint.

        Args:
            token: GitHub token with GitHub Models access.
            toi: Parsed user TOI preferences.
            user_message: User input for the assistant.

        Returns:
            Assistant text response.

        Raises:
            RuntimeError: If response is malformed or request fails.
        """
        payload = {
            "model": self.model_config.model,
            "messages": self.build_messages(toi, user_message),
            "temperature": self.model_config.temperature,
            "max_tokens": self.model_config.max_tokens,
        }
        request = urllib.request.Request(
            self.model_config.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - preserves context from transport failures
            raise RuntimeError("Failed to invoke GitHub Models endpoint") from exc

        try:
            return body["choices"][0]["message"]["content"].strip()
        except Exception as exc:  # noqa: BLE001 - malformed response handling
            raise RuntimeError("GitHub Models response did not include assistant content") from exc


__all__ = ["TOIAgentSolidarityKit", "SolidarityModelConfig"]
