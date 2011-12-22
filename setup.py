import setuptools

setuptools.setup(
    name = "jinjatag",
    version = "0.1.1",
    author = "Dave Mankoff",
    author_email = "mankyd@gmail.com",
    description = "A library to make Jinja2 Extensions Easy",
    long_description = open("README.md").read(),
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
        "License :: OSI Approved :: GNU General Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ]
)
