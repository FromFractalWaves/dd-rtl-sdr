# setup.py

from setuptools import setup, find_packages
import os

# Read the README file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define the package requirements
install_requires = [
    'PyYAML',
    'pydantic>=2.0,<3.0',
    'fastapi',
    'uvicorn',
    'PyQt5',
    # Add other runtime dependencies here
]

# Define extra requirements for development
extras_require = {
    'dev': [
        'pytest',
        'pytest-mock',
        'coverage',
        # Add other development dependencies here
    ],
}

setup(
    name='ddrtlsdr',
    version='1.0.0',
    description='A standalone library meant to reduce human suffering associated with pyrtlsdr',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Ethan Satcher',
    author_email='ems910@outlook.com',
    url='https://github.com/FromFractalWaves/ddrtlsdr',  # Replace with your actual repository URL
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    keywords='sdr rtl-sdr pyrtlsdr replacement fastapi pyqt',
    packages=find_packages(where='src'),  # Locate packages in 'src/'
    package_dir={'': 'src'},               # Tell setuptools packages are under 'src'
    install_requires=install_requires,
    extras_require=extras_require,
    python_requires='>=3.7',
    include_package_data=True,  # Include non-code files specified in MANIFEST.in
)
