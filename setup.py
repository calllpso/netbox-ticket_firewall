from setuptools import find_packages, setup

setup(
    name='ticket_firewall',
    version='1.2.1',
    description='Netbox Ticket Firewall plugin',
    install_requires=[
        "pandas", 
    ],
    # "pandas==1.1.5", for python 3.6 
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)


