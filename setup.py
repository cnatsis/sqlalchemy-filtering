import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sqlalchemy-filtering",
    version="0.1.0",
    author="Christos Natsis",
    author_email="christos_na@hotmail.com",
    description="SQLAlchemy query filtering and sorting wrapper in JSON format.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cnatsis/sqlalchemy-filtering",
    project_urls={
        "Issues Tracker": "https://github.com/cnatsis/sqlalchemy-filtering/issues",
    },
    extras_require={
        'postgresql': ['psycopg2==2.8.4'],
        'mysql': ['mysqlclient==2.1.0'],
    },
    zip_safe=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Database",
    ],
    package_dir={"": "sqlalchemy_filtering"},
    packages=setuptools.find_packages(where="sqlalchemy_filtering"),
    python_requires=">=3.6",
    license='Apache License, Version 2.0',
)
