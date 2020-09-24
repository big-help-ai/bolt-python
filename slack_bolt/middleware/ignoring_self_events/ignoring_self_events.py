import logging
from typing import Callable, Dict, Any

from slack_bolt.authorization import AuthorizationResult
from slack_bolt.logger import get_bolt_logger
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse
from slack_bolt.middleware.middleware import Middleware


class IgnoringSelfEvents(Middleware):
    def __init__(self):
        """Ignores the events generated by this bot user itself."""
        self.logger = get_bolt_logger(IgnoringSelfEvents)

    def process(
        self, *, req: BoltRequest, resp: BoltResponse, next: Callable[[], BoltResponse],
    ) -> BoltResponse:
        auth_result = req.context.authorization_result
        if self._is_self_event(auth_result, req.context.user_id, req.body):
            self._debug_log(req.body)
            return req.context.ack()
        else:
            return next()

    # -----------------------------------------

    @staticmethod
    def _is_self_event(
        auth_result: AuthorizationResult, user_id: str, body: Dict[str, Any]
    ):
        return (
            auth_result is not None
            and user_id == auth_result.bot_user_id
            and body.get("event") is not None
        )

    def _debug_log(self, body: dict):
        if self.logger.level <= logging.DEBUG:
            event = body.get("event")
            self.logger.debug(f"Skipped self event: {event}")
