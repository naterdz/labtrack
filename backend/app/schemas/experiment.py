from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, FiniteFloat, StringConstraints, model_validator

from backend.app.schemas.project import Name

Dataset = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
MetricName = Annotated[str, StringConstraints(strip_whitespace=True, max_length=80)]
Notes = Annotated[str, StringConstraints(max_length=4000)]


class ExperimentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Name
    dataset_name: Dataset
    model_name: Name
    metric_name: MetricName | None = None
    metric_value: FiniteFloat | None = None
    notes: Notes | None = None


class ExperimentPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Name | None = None
    dataset_name: Dataset | None = None
    model_name: Name | None = None
    metric_name: MetricName | None = None
    metric_value: FiniteFloat | None = None
    notes: Notes | None = None

    @model_validator(mode="after")
    def valid_patch(self):
        if not self.model_fields_set:
            raise ValueError("Indica al menos un campo.")
        for field in ("name", "dataset_name", "model_name"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} no admite null.")
        return self


class ExperimentResponse(ExperimentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime
