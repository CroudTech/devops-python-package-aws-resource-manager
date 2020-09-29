from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    install_requires=[
        "boto3==1.15.5",
        "botocore==1.18.5",
        "click==7.1.2",
        "jmespath==0.10.0; python_version >= '2.6' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "python-dateutil==2.8.1; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "s3transfer==0.3.3",
        "six==1.15.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "urllib3==1.25.10; python_version != '3.4'",
    ],
    name="croudtech-helm-helper",  # Replace with your own username
    version="0.0.1",
    author="Jim Robinson",
    author_email="jscrobinson@gmail.com",
    description="Helm utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CroudTech/devops-python-package-aws-resource-manager",
    packages=["aws_resource_inventory", "aws_resource_inventory"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": ["aws-resource-inventory=aws_resource_inventory.cli:cli"],
    },
)
