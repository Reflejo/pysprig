from setuptools import setup

name = "sprig"
version = "0.0.1"

readme = open("README.md").read()

setup(
    name=name,
    version=version,
    description="Unofficial python implementation of Sprig's API",
    long_description=readme,
    author="Martin Conte Mac Donell",
    author_email="Reflejo@gmail.com",
    url="https://github.com/Reflejo/sprig-api",
    license="MIT",
    packages=["sprig", "sprig.mock"],
    package_data={
        "sprig.mock": ['*.json'],
    },
    zip_safe=False,
    include_package_data=True,
    test_suite="tests.suite",
)
