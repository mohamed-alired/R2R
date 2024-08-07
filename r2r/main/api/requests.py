import uuid
from typing import Optional, Union

from pydantic import BaseModel

from r2r.base import AnalysisTypes, FilterCriteria


class R2RUpdatePromptRequest(BaseModel):
    name: str
    template: Optional[str] = None
    input_types: Optional[dict[str, str]] = {}


class R2RIngestFilesRequest(BaseModel):
    document_ids: Optional[list[uuid.UUID]] = None
    metadatas: Optional[list[dict]] = None
    versions: Optional[list[str]] = None


class R2RUpdateFilesRequest(BaseModel):
    metadatas: Optional[list[dict]] = None
    document_ids: Optional[list[uuid.UUID]] = None


class R2RSearchRequest(BaseModel):
    query: str
    vector_search_settings: Optional[dict] = None
    kg_search_settings: Optional[dict] = None


class R2RRAGRequest(BaseModel):
    query: str
    vector_search_settings: Optional[dict] = None
    kg_search_settings: Optional[dict] = None
    rag_generation_config: Optional[dict] = None
    task_prompt_override: Optional[str] = None
    include_title_if_available: Optional[bool] = True


class R2REvalRequest(BaseModel):
    query: str
    context: str
    completion: str


class R2RDeleteRequest(BaseModel):
    keys: list[str]
    values: list[Union[bool, int, str]]


class R2RAnalyticsRequest(BaseModel):
    filter_criteria: FilterCriteria
    analysis_types: AnalysisTypes


class R2RUsersOverviewRequest(BaseModel):
    user_ids: Optional[list[uuid.UUID]]


class R2RDocumentsOverviewRequest(BaseModel):
    document_ids: Optional[list[uuid.UUID]]
    user_ids: Optional[list[uuid.UUID]]


class R2RDocumentChunksRequest(BaseModel):
    document_id: uuid.UUID


class R2RLogsRequest(BaseModel):
    log_type_filter: Optional[str] = (None,)
    max_runs_requested: int = 100


class R2RPrintRelationshipsRequest(BaseModel):
    limit: int = 100


class R2RExtractionRequest(BaseModel):
    entity_types: list[str]
    relations: list[str]
