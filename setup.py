from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lenslogic",
    version="1.0.1",
    author="LensLogic",
    description="Smart photo organization powered by metadata",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "pillow>=10.0.0",
        "exif>=1.6.0",
        "click>=8.0.0",
        "rich>=13.0.0",
        "pyyaml>=6.0",
        "geopy>=2.0.0",
        "python-dateutil>=2.8.0",
        "questionary>=2.0.0",
        "colorama>=0.4.0",
        "pathvalidate>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "lenslogic=main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)