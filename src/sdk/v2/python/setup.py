from setuptools import setup, find_packages

setup(
    name="vernachain-sdk",
    version="2.0.0",
    description="Official Python SDK for Vernachain blockchain platform",
    author="BronzonTech-Cloud",
    author_email="bronzontech@pm.me",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "websockets>=10.4",
        "pydantic>=2.0.0",
        "python-dateutil>=2.8.2",
        "typing-extensions>=4.5.0",
        "cryptography>=40.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "black>=22.0.0",
            "mypy>=1.0.0",
            "isort>=5.0.0",
        ]
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
    ],
) 