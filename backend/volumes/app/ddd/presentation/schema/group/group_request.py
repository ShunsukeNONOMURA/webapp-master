

from typing import Any

# from sqlmodel import Field
from pydantic import Field, validator

from app.core.base import BaseRequest
from app.ddd.infrastructure.util.convert import recursive_to_snake


class CreateGroupRequest(BaseRequest):
    group_name: str

# class PatchGroupsRequest(BaseRequest):
#     updated_at: datetime # 楽観的ロック用途
#     user_password: str | None = Field(None)
#     user_name: str | None = Field(None)
#     user_role_code: str | None = Field(None)


_filters_example: dict[str, Any] = {
    "groupId": "abc",
}

class QueryGroupRequest(BaseRequest):
    offset: int = Field(default=0)
    limit: int = Field(default=10)
    query: dict[str,Any] = Field(
        default={},
        examples=[_filters_example]
    )

    @validator("query", pre=True, always=True)
    def validate_query(cls, query: dict[str, Any]) -> dict[str, Any]:
        """filtersのcaseをスネークに変換する."""
        # query = query or {}
        return recursive_to_snake(query)
