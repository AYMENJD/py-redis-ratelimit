# py-redis-ratelimit

 A simple asynchronous rate limiter based on redis.

### Requirements

- python >= 3.7
- redis >= 4.2.0

### Installation

```bash
pip install py-redis-ratelimit
```

### Examples
Basic example:
```python

from redis.asyncio import Redis
import ratelimit, asyncio

redis = Redis(decode_responses=True)
limiter = ratelimit.RateLimit(
    redis, prefix="api_rate_limit", rate=10, period=60, retry_after=20
)
print(ratelimit.RateLimit.__doc__)  # print RateLimit class docstring


async def do_something():
    await limiter.acquire(
        identifier="do_something_function"
    )  # a unique identifier for the function. This let's RateLimit know what service/resource you are trying to access.
    ...


async def main():
    for x in range(40):
        try:
            print("Calling do_something() for the {}th time".format(x + 1))
            await do_something()
        except ratelimit.FloodWait as e:
            print("Exception:", e.to_dict())
            break


if __name__ == "__main__":
    asyncio.run(main())

```

# Contributing
Pull requests are always welcome!!
# License

MIT [License](https://github.com/AYMENJD/py-redis-ratelimit/blob/main/LICENSE)
