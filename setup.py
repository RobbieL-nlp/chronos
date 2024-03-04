from setuptools import find_packages, setup

with open("README.md") as f:
    details = f.read()


setup(
    name="xchronos",
    version="0.1.1",
    description="An innovated periodic cron time utility using similar but extended expression with cron, and optimized algorithm implementation for large number of steps search.",
    long_description=details,
    long_description_content_type="text/markdown",
    author="RobbieL-nlp",
    license_files="LICENSE",
    url="https://github.com/RobbieL-nlp/xchronos",
    python_requires=">=3.8",
    keywords="cron, chronos, period, time, date, datetime, cronos",
    package_dir={"xchronos": "xchronos"},
    packages=find_packages("xchronos")
)

