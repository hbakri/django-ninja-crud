from typing import List, Optional, Union

from ninja_crud.testing.core.components import utils


class Headers:
    """
    This class is used to manage headers used in HTTP requests.

    This class allows you to define sets of headers for different test scenarios. Specifically,
    it enables you to set up headers that should result in successful requests ('ok'), headers
    that should result in 'forbidden' responses, and headers that should result in 'unauthorized'
    responses.

    Example:
        >>> from ninja_crud.testing.core.components import Headers
        >>> headers = Headers(
        ...     ok=[{"HTTP_AUTHORIZATION": "Bearer ok"}],
        ...     forbidden=[{"HTTP_AUTHORIZATION": "Bearer forbidden"}],
        ...     unauthorized=[{}]
        ... )
        >>> headers.ok
        [{"HTTP_AUTHORIZATION": "Bearer ok"}]
        >>> headers.forbidden
        [{"HTTP_AUTHORIZATION": "Bearer forbidden"}]
        >>> headers.unauthorized
        [{}]
    """

    def __init__(
        self,
        ok: Union[dict, List[dict]],
        forbidden: Union[dict, List[dict], None] = None,
        unauthorized: Union[dict, List[dict], None] = None,
    ) -> None:
        self.ok: List[dict] = utils.ensure_list_of_dicts(ok)
        self.forbidden: Optional[List[dict]] = (
            utils.ensure_list_of_dicts(forbidden) if forbidden is not None else None
        )
        self.unauthorized: Optional[List[dict]] = (
            utils.ensure_list_of_dicts(unauthorized)
            if unauthorized is not None
            else None
        )
