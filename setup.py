from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="enhanced-typing-assistant",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="An AI-powered typing assistant with accessibility features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/typing_assistant",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Office/Business",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
        "Natural Language :: English",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "typing-assistant=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "typing_assistant": [
            "assets/*.png",
            "styles.qss",
            "config/*.json",
            "resources/*",
        ],
    },
)
