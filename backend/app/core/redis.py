import hashlib
from fastapi import Request, Response


def search_cache_key_builder(
    func,
    namespace: str = "",
    *,
    request: Request = None,
    response: Response = None,
    **kwargs,
):
    q = kwargs.get("q")
    page = kwargs.get("page")
    size = kwargs.get("size")
    document_id = kwargs.get("document_id")
    my_docs = kwargs.get("my_docs")

    if my_docs:
        current_user = kwargs.get("current_user")
        user_segment = f"user:{current_user.id}" if current_user else "user:anonymous"
    else:
        user_segment = "global"

    cache_str = f"{namespace}:{func.__name__}:{user_segment}:q:{q}:p:{page}:s:{size}:doc:{document_id}"

    return hashlib.md5(cache_str.encode()).hexdigest()
