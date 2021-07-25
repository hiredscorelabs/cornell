# pylint: ignore-errors
from pathlib import Path
from setuptools import setup, find_packages

readme = Path("README.md").read_text(encoding="utf-8")
exec(Path("cornell/_version.py").read_text(encoding="utf-8"))
VERSION = '.'.join(str(i) for i in __version__)

requirements = [
    'flask>=2.0.0',
    'yarl',
    'requests',
    'structlog',
    'toolz',
    'vcrpy~=4.0',
    'xmltodict',
    'click',
    'blinker'
]

dev_requirements = {"dev" : [
    'pylint>=2.6.0',
    'requests-mock>=1.8.0',
    'pytest>=6.2.2',
    'pytest-cov~=2.12',
]}

setup(
    name='cornell',
    packages=find_packages(),
    version=VERSION,
    description="Cornell: record & replay mock server",
    long_description=readme,
    long_description_content_type='text/markdown',
    url="https://hiredscorelabs.github.io/cornell/",
    author="Yael Mintz",
    author_email="yaelmi3@gmail.com",
    license="MIT",
    entry_points={'console_scripts': ['cornell = cornell.cornell_server:start_mock_service']},
    install_requires=requirements,
    extras_require=dev_requirements,
    project_urls={
        'Documentation': 'https://hiredscorelabs.github.io/cornell/',
        'Source': 'https://github.com/hiredscorelabs/cornell',
    },
)
