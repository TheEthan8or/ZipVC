from setuptools import setup, find_packages

setup(
    name='ZipVC',
    version='1.0.0.dev6',
    packages=find_packages(),
    url='https://bitbucket.org/TSDude/zipversioncontrol',
    license='MIT',
    author='team1790',
    author_email='ts-programs@outlook.com',
    description='Allows git version control with zip archives',
    install_requires=['colorama', 'gitpython'],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Database :: Front-Ends',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
    ],
    keywords='zip file archive git version control',
    python_requires='>=3.6',
)
