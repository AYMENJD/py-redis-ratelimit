from redis.asyncio import Redis
from asyncio import Lock


class FloodWait(Exception):
    """FloodWait exception class.

    Args:
        message (``str``):
            The message to display.

        rate (``int``):
            The rate of the action.

        period (``int``):
            The period of the action.

        retry_after (``int``):
            The remaining time before the action can be performed again.
    """

    def __init__(self, message: str, rate: int, period: int, retry_after: int) -> None:
        self.message = message
        self.rate = rate
        self.period = period
        self.retry_after = retry_after
        super().__init__(message)

    def to_dict(self) -> dict:
        """Convert the exception to a dictionary."""
        return {
            "message": self.message,
            "rate": str(self.rate) + "/" + str(self.period),
            "retry_after": self.retry_after,
        }


class RateLimit:
    """Main class for rate limiting.

    Args:
        redis_client (``redis.Redis``):
            Instance of `~redis.Redis`.

        prefix (``str``):
            Prefix for redis keys. For example if you pass ``api_rate_limit``, redis keys will be like ``api_rate_limit:IDENTIFIER:usage``, ``api_rate_limit:IDENTIFIER:restrict``.

        rate (``int``):
            Number of requests allowed per period.

        period (``int``):
            Period in seconds.

        retry_after (``int``, optional):
            Number of seconds to wait after being rate-limited. If not specified, period is used.

    """

    def __init__(
        self, redis_client, prefix: str, rate: int, period: int, retry_after: int = None
    ):
        self.redis_client: Redis = redis_client
        self.prefix = prefix + ":"
        self.rate = rate
        self.period = period
        self.retry_after = period if retry_after is None else retry_after
        self.lock = Lock()

        if not isinstance(redis_client, Redis):
            raise TypeError("redis_client must be an instance of redis.asyncio.Redis")

    async def getUsage(self, identifier: str) -> int:
        """Get the usage of identifier.

        Args:
            identifier (``str``):
                Identifier of the service or resource that is being rate-limited.

        Returns:
            ``int``: Usage of the identifier. If the identifier is not found, 0 is returned.
        """
        return int(await self.redis_client.get(self._get_key(identifier, "usage")) or 0)

    async def getRemaining(self, identifier: str) -> int:
        """Get the remaining time for rate-limited identifier.

        Args:
            identifier (``str``):
                Identifier of the service or resource that is being rate-limited.

        Returns:
            ``int``: Remaining time in seconds. If the identifier is not found, 0 is returned.
        """
        ttl = int(
            await self.redis_client.ttl(self._get_key(identifier, "restrict")) or 0
        )
        if ttl > 0:
            return ttl
        return 0

    async def restrict(self, identifier: str):
        """Rate-limit an identifier.

        Args:
            identifier (``str``):
                Identifier of the service or resource that is being rate-limited.

        """
        return await self.redis_client.setex(
            self._get_key(identifier, "restrict"), self.retry_after, 1
        )

    async def acquire(self, identifier: str, restrict: bool = True) -> None:
        """Acquire a lock for an identifier.

        Args:
            identifier (``str``):
                Identifier of the service or resource that is being rate-limited.

            restrict (``bool``, optional):
                If True, the identifier will be rate-limited. If False, the identifier will not be rate-limited. But `~ratelimit.FloodWait` will be raised as notice once it hits the rate limit threshold. Default to ``True``.

        Raises:
            `~ratelimit.FloodWait`: If the identifier hits the rate limit threshold.
        """
        remaining = await self.getRemaining(identifier)

        if remaining:
            raise FloodWait("Rate limit exceeded", self.rate, self.period, remaining)

        async with self.lock:
            usage = await self.getUsage(identifier)
            u_key = self._get_key(identifier, "usage")

            if usage > self.rate:
                await self.redis_client.delete(u_key)

                if restrict:
                    await self.restrict(identifier)

                raise FloodWait(
                    "Rate limit exceeded",
                    self.rate,
                    self.period,
                    self.retry_after,
                )
            else:
                await self.redis_client.incr(u_key)
                if int(await self.redis_client.ttl(u_key)) < 0:
                    await self.redis_client.expire(u_key, self.period)

    def _get_key(self, identifier: str, key: str) -> str:
        return self.prefix + identifier + ":" + key


__all__ = ("RateLimit", "FloodWait")

__version__ = "0.1.2"
__copyright__ = "Copyright (c) 2022 AYMEN Mohammed ~ https://github.com/AYMENJD"
