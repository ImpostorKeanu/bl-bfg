import setuptools

# Read README.md as a variable to pass as the package's long
# description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='bl-bfg',
    version='1.0.4',
    author='Justin Angel',
    author_email='justin@arch4ngel.ninja',
    description='A password guessing framework.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/arch4ngel/bl-bfg',
    include_package_data=True,
    package_dir={'':'src'},
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
    ],
    python_requires='>=3.9.2',
    scripts=['bfg'],
    package_data={'bfg.datasets':['*.txt', '*.yaml', '*.xml']},
    install_requires=[
        'bruteloops >= 1',
        'requests_ntlm == 1.1.0',
        'pysmb == 1.1.27',
        'lxml >= 4.6.4',
        'pyyaml',
        'xmltodict',
        'dict-toolbox',
        'pydantic == 1.10.12']
)
