from setuptools import setup, find_packages
from pathlib import Path

# Read the README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="weighit",
    version="1.0.0",
    author="wyojustin",
    description="Food pantry scale system with temperature tracking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wyojustin/weighit",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Other Audience",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    install_requires=[
        "streamlit>=1.31.0",
        "pillow>=10.0.0",
        "hidapi>=0.14.0",
        "click>=8.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "weigh=weigh.cli_weigh:main",
        ],
    },
    package_data={
        "weigh": [
            "schema.sql",
            "assets/*.png",
            "assets/*.css",
        ],
    },
    include_package_data=True,
)
