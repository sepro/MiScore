import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="miscore",
    version="0.0.2",
    author="Sebastian Proost",
    author_email="sebastian.proost@gmail.com",
    description="Package to manage high scores in JSON format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sepro/MiScore",
    project_urls={
        "Bug Tracker": "https://github.com/sepro/MiScore/issues",
    },
    install_requires=["click>=8.1.3", "pydantic>=1.9.2,<2.0.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["miscore"],
    python_requires=">=3.6",
)
