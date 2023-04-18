from setuptools import find_packages
from setuptools import setup

version = "0.0.1"

setup(
    name="passerelle-imio-apims-casier-judiciaire",
    version=version,
    author="iMio",
    author_email="support-ts@imio.be",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
    ],
    url="https://github.com/IMIO/passerelle-imio-apims-casier-judiciare",
    install_requires=[
        "django>=2.2",
    ],
    zip_safe=False,
)
