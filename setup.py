import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="faadelays",
    version="0.0.5",
    author="Nathan Tilley",
    author_email="nathan@tilley.xyz",
    description="A package to retrieve FAA airport status",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ntilley905/faadelays",
    packages=setuptools.find_packages(),
    install_requires=['aiohttp'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
