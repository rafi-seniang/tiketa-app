"""What the service says about itself."""

from pydantic import BaseModel


class ServiceMeta(BaseModel):
    id: str
    name: str
    summary: str
    version: str
    docs_path: str
