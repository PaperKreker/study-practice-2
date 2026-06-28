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
    endpoint_kwargs = kwargs.get("kwargs") if "kwargs" in kwargs else kwargs

    q = endpoint_kwargs.get("q")
    page = endpoint_kwargs.get("page")
    size = endpoint_kwargs.get("size")
    document_id = endpoint_kwargs.get("document_id")
    my_docs = endpoint_kwargs.get("my_docs")

    if my_docs:
        current_user = endpoint_kwargs.get("current_user")
        user_segment = f"user:{current_user.id}" if current_user else "user:anonymous"
    else:
        user_segment = "global"

    cache_str = f"{namespace}:{func.__name__}:{user_segment}:q:{q}:p:{page}:s:{size}:doc:{document_id}"

    return hashlib.md5(cache_str.encode()).hexdigest()
