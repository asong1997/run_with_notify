from setuptools import setup, find_packages

setup(
    name="run_with_notify",
    version="0.1",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'run-with-notify=notifier.cli:main'
        ]
    },
)