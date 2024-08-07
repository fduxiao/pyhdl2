from setuptools import setup, find_packages


with open("README.md") as file:
    long_desc = file.read()

setup(
    name="pyhdl2",
    desc="try to make a hardware design language",
    long_desc=long_desc,
    version="0.0.1",
    packages=find_packages(exclude=["tests"])
)
