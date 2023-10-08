from typing import List, Optional, Union


class PathParameters:
    def __init__(
        self,
        ok: Union[dict, List[dict]],
        not_found: Union[dict, List[dict], None] = None,
    ) -> None:
        if isinstance(ok, dict):
            ok = [ok]
        if not_found is not None and isinstance(not_found, dict):
            not_found = [not_found]

        assert isinstance(ok, list) and len(ok) > 0
        if not_found is not None:
            assert isinstance(not_found, list) and len(not_found) > 0

        self.ok: List[dict] = ok
        self.not_found: Optional[List[dict]] = not_found


class QueryParameters:
    def __init__(
        self,
        ok: Union[dict, List[dict]],
        bad_request: Union[dict, List[dict], None] = None,
    ) -> None:
        if isinstance(ok, dict):
            ok = [ok]
        if bad_request is not None and isinstance(bad_request, dict):
            bad_request = [bad_request]

        assert isinstance(ok, list) and len(ok) > 0
        if bad_request is not None:
            assert isinstance(bad_request, list) and len(bad_request) > 0

        self.ok: List[dict] = ok
        self.bad_request: Optional[List[dict]] = bad_request


class AuthHeaders:
    def __init__(
        self,
        ok: Union[dict, List[dict]],
        forbidden: Union[dict, List[dict], None] = None,
        unauthorized: Union[dict, List[dict], None] = None,
    ) -> None:
        if isinstance(ok, dict):
            ok = [ok]
        if forbidden is not None and isinstance(forbidden, dict):
            forbidden = [forbidden]
        if unauthorized is not None and isinstance(unauthorized, dict):
            unauthorized = [unauthorized]

        assert isinstance(ok, list) and len(ok) > 0
        if forbidden is not None:
            assert isinstance(forbidden, list) and len(forbidden) > 0
        if unauthorized is not None:
            assert isinstance(unauthorized, list) and len(unauthorized) > 0

        self.ok: List[dict] = ok
        self.forbidden: Optional[List[dict]] = forbidden
        self.unauthorized: Optional[List[dict]] = unauthorized


class Payloads:
    def __init__(
        self,
        ok: Union[dict, List[dict]],
        bad_request: Union[dict, List[dict], None] = None,
        conflict: Union[dict, List[dict], None] = None,
    ) -> None:
        if isinstance(ok, dict):
            ok = [ok]
        if bad_request is not None and isinstance(bad_request, dict):
            bad_request = [bad_request]
        if conflict is not None and isinstance(conflict, dict):
            conflict = [conflict]

        assert isinstance(ok, list) and len(ok) > 0
        if bad_request is not None:
            assert isinstance(bad_request, list) and len(bad_request) > 0
        if conflict is not None:
            assert isinstance(conflict, list) and len(conflict) > 0

        self.ok: List[dict] = ok
        self.bad_request: Optional[List[dict]] = bad_request
        self.conflict: Optional[List[dict]] = conflict
