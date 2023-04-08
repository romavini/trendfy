from pathlib import Path

from setuptools import find_packages, setup  # type: ignore

here = Path(__file__).parent.resolve()
requirements = open(here / "requirements.txt", encoding="utf-8").read()

setup(
    name="trendfy",
    version=1.0,
    description="A Spotify data collector and analyser.",
    author="Vinícius Romano",
    author_email="mdcdxcvi@gmail.com",
    include_package_data=True,
    python_requires=">=3.6.0",
    packages=find_packages(exclude=("tests",)),
    install_requires=requirements,
)

