PROJECT='Multi-Tenant'

# Change docs/sphinx/conf.py too!
VERSION = '0.2'

from setuptools import setup

try:
    long_description = open('README.rst', 'rt').read()
except IOError:
    long_description = ''

setup(
    name=PROJECT,
    version=VERSION,

    description='Multi-cloud API',


    url='https://gecgithub01.walmart.com/rnagpal/python-multicloudclient.git',

    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: Apache Software License',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.2',
                 'Intended Audience :: Developers',
                 'Environment :: Console',
                 ],

    platforms=['Any'],

    scripts=[],

    #provides=[],
    zip_safe=False,
    packages=['multicloudclient'],
    #include_package_data=True,

    entry_points={
        'console_scripts': [
	    'multi-cloud = multicloudclient.commandshell:main'
        ],
    },

)

