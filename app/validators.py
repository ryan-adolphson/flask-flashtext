from typing import Annotated

from flask import abort, current_app
from pydantic import BaseModel, Field, ValidationError


class SearchRequest(BaseModel):
    text: Annotated[str, Field(min_length=1)]
    keywords: Annotated[list[Annotated[str, Field(min_length=1, max_length=500)]], Field(min_length=1)]
    case_sensitive: bool = False

    def model_post_init(self, __context) -> None:
        max_text = current_app.config.get("MAX_TEXT_LENGTH", 1_048_576)
        max_kw = current_app.config.get("MAX_KEYWORDS", 1000)
        errors = []
        if len(self.text) > max_text:
            errors.append({"field": "text", "msg": f"Text exceeds maximum length of {max_text} characters"})
        if len(self.keywords) > max_kw:
            errors.append({"field": "keywords", "msg": f"List must have at most {max_kw} items"})
        if errors:
            abort(422, description={"error": "Input validation failed", "code": "VALIDATION_ERROR", "detail": errors})


def validate_search_request(raw: dict) -> SearchRequest:
    try:
        return SearchRequest.model_validate(raw)
    except ValidationError as exc:
        detail = [{"field": e["loc"][-1] if e["loc"] else "body", "msg": e["msg"]} for e in exc.errors()]
        abort(422, description={"error": "Input validation failed", "code": "VALIDATION_ERROR", "detail": detail})
