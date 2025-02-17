from setuptools import setup, find_packages

setup(
    name='htmlizer',
    version='0.1',
    packages=find_packages(),
    install_requires=[  # List your dependencies here (e.g., argparse, any other libraries)
        'argparse',
        'flask'
    ],
    entry_points={
        'console_scripts': [
            'htmlizer=htmlizer.main:main',  # 'mycli' is the command that will run the 'main' function in cli.py
        ],
    },
    include_package_data=True,  # Ensures files listed in MANIFEST are included
    package_data={
        'htmlizer': ['templates/*'],  # Include all files in the 'templates' folder
    },
    description='JUnit XML to HTML Report Generator',
    author='Pablo Calvo',
    author_email='pjcalvov@gmail.com',
    url='https://github.com/pjcalvo/htmlizer',
)
