from __future__ import annotations

from datetime import datetime
from typing import Optional, Literal, List

from pydantic import BaseModel, Field


class ObjectState(BaseModel):
    object_id: str = Field(..., description="Unique object identifier (e.g. NORAD ID or internal ID)")
    position_m: List[float] = Field(..., min_length=3, max_length=3, description="Position vector [m] (x,y,z)")
    velocity_mps: List[float] = Field(..., min_length=3, max_length=3, description="Velocity vector [m/s] (vx,vy,vz)")
    frame: Literal["EME2000", "ITRF", "TEME"] = "TEME"


class ConjunctionMessage(BaseModel):
    message_id: str
    creation_time_utc: datetime
    tca_utc: datetime = Field(..., description="Time of closest approach (UTC)")

    primary: ObjectState
    secondary: ObjectState

    miss_distance_m: Optional[float] = Field(None, ge=0.0)
    relative_speed_mps: Optional[float] = Field(None, ge=0.0)

    # Optional covariance (flattened 3x3 for simplicity in MVP)
    rel_pos_cov_m2: Optional[List[float]] = Field(
        None, min_length=9, max_length=9, description="Flattened 3x3 covariance of relative position [m^2]"
    )

    class Config:
        extra = "forbid"
