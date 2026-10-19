from typing import Any

from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    case: str = "data/case1.json"
    algorithm: str = "ga"
    mode: str = "fee"
    seed: int = 0
    parameters: dict[str, Any] = Field(default_factory=dict)
