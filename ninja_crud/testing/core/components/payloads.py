from typing import List, Optional, Union

from ninja_crud.testing.core.components import utils


class Payloads:
    """
    This class is used to manage payloads used in HTTP requests.

    This class allows you to define sets of payloads for different test scenarios. Specifically,
    it enables you to set up payloads that should result in successful requests ('ok'), payloads
    that should result in 'bad request' responses, and payloads that should result in 'conflict'
    responses.

    Example:
    ```python
    from ninja_crud.testing.core.components import Payloads

    payloads = Payloads(
        ok=[{"name": "item 1"}, {"name": "item 2"}],
        bad_request=[{"name": ""}],
        conflict=[{"name": "existing item"}],
    )
    """

    def __init__(
        self,
        ok: Union[dict, List[dict]],
        bad_request: Union[dict, List[dict], None] = None,
        conflict: Union[dict, List[dict], None] = None,
    ) -> None:
        self.ok: List[dict] = utils.ensure_list_of_dicts(ok)
        self.bad_request: Optional[List[dict]] = (
            utils.ensure_list_of_dicts(bad_request) if bad_request is not None else None
        )
        self.conflict: Optional[List[dict]] = (
            utils.ensure_list_of_dicts(conflict) if conflict is not None else None
        )
