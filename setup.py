from setuptools import setup, find_packages

setup(
    name='timewarrior_timesheet',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'fpdf2',
        'timew'
    ],
    entry_points={
        'console_scripts': [
            'generate-timesheet=main:main',
        ],
    },
    author='Martin Hans',
    author_email='martin@artnim.io',
    description='Generate a timesheet PDF from Timewarrior data.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/artnim/timewarrior-timesheet',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)