from re import findall
from setuptools import setup, find_packages


with open("ratelimit/__init__.py", "r") as f:
    version = findall(r"__version__ = \"(.+)\"", f.read())[0]

with open("README.md", "r") as f:
    readme = f.read()

with open("requirements.txt", "r") as f:
    requirements = [x.strip() for x in f.readlines()]


setup(
    name="Py-redis-ratelimit",
    version=version,
    description="A simple asyncio-based rate limiter for Python3 using Redis.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="AYMEN Mohammed",
    author_email="let.me.code.safe@gmail.com",
    url="https://github.com/AYMENJD/py-redis-ratelimit",
    license="MIT",
    python_requires=">=3.7",
    install_requires=requirements,
    project_urls={
        "Source": "https://github.com/AYMENJD/py-redis-ratelimit",
        "Tracker": "https://github.com/AYMENJD/py-redis-ratelimit/issues",
    },
    packages=find_packages(),
    keywords=["ratelimit", "redis", "flood", "spam", "asyncio"],
)
