from pydantic import BaseModel
from app.jobs.models import JobType

class JobCreateSchema(BaseModel):
    type: JobType
    payload: str