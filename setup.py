import setuptools
import sys

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as reqs:
    requirements = reqs.read().split("\n")

versionName = sys.argv[1].replace("refs/tags/v", "")
del sys.argv[1]

setuptools.setup(
    name="pythonpp",
    version=versionName,
    author="Ronak Badhe, Kento Nishi",
    author_email="ronak.badhe@gmail.com, kento24gs@outlook.com",
    description=long_description.split("\n")[1],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/r2dev2bb8/PythonPP",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.0",
    install_requires=requirements,
)
