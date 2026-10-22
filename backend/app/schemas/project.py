from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Description = Annotated[str, StringConstraints(max_length=2000)]


class ProjectCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Name
    description: Description | None = None


class ProjectPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Name | None = None
    description: Description | None = None

    @model_validator(mode="after")
    def valid_patch(self):
        if not self.model_fields_set or ("name" in self.model_fields_set and self.name is None):
            raise ValueError("Indica al menos un campo válido; el nombre no admite null.")
        return self


class ProjectResponse(ProjectCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
