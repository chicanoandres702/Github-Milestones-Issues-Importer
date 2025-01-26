from setuptools import setup, find_packages

setup(
    name='github_importer',
    version='0.1.0',
    description='A tool for importing milestones and issues to GitHub from a JSON file',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/your-github-repo',
    packages=find_packages(),
    install_requires=[
        'requests',
        'flask',
        'python-dotenv',
        'jsonschema',
    ],
    entry_points={
        'console_scripts': [
            'github-importer = github_importer.main:main',
        ],
    },
    classifiers=[
      'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ]
)