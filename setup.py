from setuptools import setup, find_packages

setup(
    name='ZipVersionControl',
    version='0.0.0.4',
    packages=find_packages(),
    url='https://bitbucket.org/TSDude/zipversioncontrol',
    license='MIT License',
    author='team1790',
    author_email='ts-programs@outlook.com',
    description='Allows git version control with zip archives',
    install_requires=['colorama', 'gitpython']
)
