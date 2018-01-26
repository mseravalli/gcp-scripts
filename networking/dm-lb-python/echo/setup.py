from setuptools import setup
setup(
    name="echo",
    version="0.0.1",
    author="Michael Wallman",
    author_email="mwallman@google.com",
    # Packages
    packages=["echo"],
    # Include additional files into the package
    include_package_data=True,
    # Details
    #url="http://pypi.python.org/pypi/MyApplication_v010/",
    license="LICENSE.txt",
    # description="Useful towel-related stuff.",
    # long_description=open("README.txt").read(),
    # Dependent packages (distributions)
    install_requires=[
        "flask==0.12.2",
        "gunicorn"
    ]
)

