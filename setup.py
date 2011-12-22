import setuptools

import jinjatag

setuptools.setup(
    name = "jinjatag",
    version = '.'.join(str(c) for c in jinjatag.__version__),
    author = "Dave Mankoff",
    author_email = "mankyd@gmail.com",
    description = "A library to make Jinja2 Extensions Easy",
    long_description = open("README.md").read(),
    test_suite = 'jinjatag.tests.test_all',
    license = "GPLv3",
    url = "https://github.com/mankyd/jinjatag",
    install_requires=[
        "jinja2>=2.5",
        ],
    packages = [
        "jinjatag",
    ],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ]
)
