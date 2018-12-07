import os

from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='Flask-Bulma',
    version='0.0.1',
    url='',
    license='MIT',
    author='fastare08',
    author_email='adriantfelismino@gmail.com',
    description='An extension that includes BULMA in your project.',
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    packages=['flask_bulma'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=['Flask'],
    classifiers=[
        'Environment :: Web Environment', 'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent', 'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ])
