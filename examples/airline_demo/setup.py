from setuptools import find_packages, setup  # type: ignore

setup(
    name="airline_demo",
    version="dev",
    author="Elementl",
    license="Apache-2.0",
    description="Dagster Examples",
    url="https://github.com/dagster-io/dagster/tree/master/examples/airline_demo",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(exclude=["test"]),
    # default supports basic tutorial & toy examples
    install_requires=["dagster"],
    extras_require={
        # full is for running the more realistic demos
        "full": [
            "dagstermill",
            "dagster-aws",
            "dagster-postgres",
            "dagster-pyspark",
            "dagster-slack",
            "dagster-snowflake",
            # These two packages, descartes and geopandas, are used in the airline demo notebooks
            "descartes",
            'geopandas; "win" not in sys_platform',
            "google-api-python-client",
            "google-cloud-storage",
            "keras",
            "matplotlib<3.4.3",
            "mock",
            "moto>=1.3.16",
            "pandas>=1.0.0",
            "pytest-mock",
            # Pyspark 2.x is incompatible with Python 3.8+
            'pyspark>=3.0.0; python_version >= "3.8"',
            'pyspark>=2.0.2; python_version < "3.8"',
            "seaborn",
            "sqlalchemy-redshift>=0.7.2",
            "SQLAlchemy-Utils==0.33.8",
            'tensorflow; python_version < "3.9"',
        ],
        "airflow": [
            "dagster_airflow",
            "docker-compose",
        ],
    },
    include_package_data=True,
)
