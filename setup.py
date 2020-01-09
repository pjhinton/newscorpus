from setuptools import setup, find_namespace_packages

setup(
    name='newscorpus',
    version='0.1.0',
    author='P.J. Hinton',
    author_email='pjhinton@aim.com',
    description='Builds a SQLite database for a text corpus of Fox News Channel website articles.',
    url='https://github.com/pjhinton/newscorpus',
    python_repquires='>=3.8',
    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src'),
    scripts=[
        'bin/nc_process_feeds',
        'bin/nc_setup_db'
    ],
    install_requires=[
        'beautifulsoup4==4.8.2',
        'requests==2.22.0',
        'SQLAlchemy==1.3.12'
    ]
)
