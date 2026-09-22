from pydantic import BaseModel
from jobs.models import JobType

class JobCreateSchema(BaseModel):
    type: JobType
    payload: str