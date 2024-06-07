from setuptools import find_packages, setup

setup(
    name='ticket_firewall',
    version='1.2.3',
    description='Netbox Ticket Firewall plugin',
    install_requires=[
        "pandas", 
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)


