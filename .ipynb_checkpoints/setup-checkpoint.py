from setuptools import setup, find_packages

setup(
    name             = 'autotrading',
    version          = '1.0',
    description      = 'Python library for auto-trading',
    author           = 'Park Jae Hyun',
    author_email     = 'hyunny82@naver.com',
    license          = 'MIT',
    url              = 'https://gitlab.com/hyunny88/auto-trading',
    download_url     = '',
    install_requires = [ ],
    packages         = find_packages(exclude = ['conf','docs', 'tests*']),
    keywords         = ['autotrading', 'koribt', 'coinone', 'bithumb'],
    python_requires  = '>=3',
    package_data     =  {
    },
    zip_safe=False,
    classifiers      = [
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)
