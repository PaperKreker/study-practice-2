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
    """Строит ключ кеша для эндпоинта поиска на основе параметров запроса.

    Совместим с fastapi-cache: параметры эндпоинта могут приходить как именованные
    аргументы напрямую, либо вложенными в kwargs["kwargs"] (в зависимости от версии
    библиотеки), поэтому оба варианта обрабатываются одинаково. Если поиск ограничен
    документами пользователя (my_docs=True), ID пользователя включается в ключ,
    чтобы разные пользователи не получали чужой кеш.

    Args:
        func: Функция-обработчик эндпоинта, для которого строится ключ.
        namespace (str): Пространство имен кеша.
        request (Request, optional): Объект HTTP-запроса (не используется напрямую).
        response (Response, optional): Объект HTTP-ответа (не используется напрямую).
        **kwargs: Параметры вызова эндпоинта (q, page, size, document_id, my_docs,
            current_user), переданные напрямую или вложенно в ключе "kwargs".

    Returns:
        str: MD5-хэш, используемый как уникальный ключ кеша.
    """

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
