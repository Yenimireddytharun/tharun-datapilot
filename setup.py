from setuptools import setup, find_packages

setup(
    name="datapilot",
    version="1.0.0",
    packages=find_packages(),
    py_modules=['cli_prototype'], # Tell it to include your CLI file
    install_requires=[
        "ply",
        "pandas",
        "matplotlib",
        "scikit-learn"
    ],
    entry_points={
        'console_scripts': [
            # CHANGE THIS LINE: command_name=filename:function_name
            'datapilot=cli_prototype:main', 
        ],
    },
)