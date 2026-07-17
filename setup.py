from setuptools import setup, find_packages

setup(
    name="project_tracker",
    version="1.0.0",
    description="Advanced daily project update tool with multi-level approval workflow for ERPNext v15+",
    author="Your Company",
    author_email="admin@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    python_requires=">=3.10",
)
