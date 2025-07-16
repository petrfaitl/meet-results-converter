from setuptools import setup, find_packages

setup(
    name="swim_results_converter",
    version="0.2.2",
    description="Swim meet data standardization and aggregation pipeline",
    author="Petr Faitl",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pandas>=1.5.0",
        "openpyxl>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "swim-results-converter=swim_results_converter.run_swim_data_pipeline:main",
        ],
    },
    python_requires=">=3.8",
)
