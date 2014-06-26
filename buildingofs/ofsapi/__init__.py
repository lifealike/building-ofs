from nameko.legacy.proxy import RPCProxy
from nameko.exceptions import RemoteError
from nameko.legacy.context import Context

from django.conf import settings


def context_factory():
    ctx = Context(
        user_id=None,
        language="en"
    )
    return ctx

rpc = RPCProxy(uri=settings.NAMEKO_URL, timeout=settings.NAMEKO_TIMEOUT,
               context_factory=context_factory)


def rpc_factory(user=None):
    def context_factory():
        user_id = None
        if user and not user.is_anonymous():
            user_id = user.id

        ctx = Context(
            user_id=user_id,
            language="en"
        )

        return ctx
    return RPCProxy(uri=settings.NAMEKO_URL, timeout=settings.NAMEKO_TIMEOUT,
               context_factory=context_factory)
