from setuptools import find_packages, setup

with open("README.md") as f:
    details = f.read()


setup(
    name="chronox-python",
    version="1.0.0",
    description="An innovated and extended periodic cron time utility, it provides more expressive power by using expression similar to cron and optimized algorithm implementation for large number of steps search.",
    long_description=details,
    long_description_content_type="text/markdown",
    author="RobbieL-nlp",
    license_files="LICENSE",
    url="https://github.com/RobbieL-nlp/ChronoX-python",
    python_requires=">=3.8",
    keywords="cron, chronos, period, time, date, datetime, chronox",
    package_dir={"chronox": "xchronos"},
)
