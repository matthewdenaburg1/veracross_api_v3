from distutils.core import setup
from os import path


__version__ = "1.0.0"


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="veracross_api_v3",
    packages=["veracross_api"],
    version=__version__,
    description="Simple library for interacting with Veracross's V3 API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT License",
    author="Matthew Denaburg",
    author_email=["matthew.denaburg@ssfs.org"],
    url="https://bitbucket.org/ssfs_tech/veracross_api",
    download_url=f"https://bitbucket.org/ssfs_tech/veracross_api/get/v{__version__}.tar.gz",
    keywords=["Veracross", "API", "API v3"],
    install_requires=["requests"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8"
    ],
)
