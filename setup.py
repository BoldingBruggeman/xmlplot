from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='xmlplot',
      version='0.1',
      description=' --- update - ',
      long_description=readme(),
      url='http://github.com/BoldingBruggeman/xmlplot',
      author='Jorn Bruggeman',
      author_email='jorn@bolding-bruggeman.com',
      license='GPL',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Numerical Models :: Configuration Tools',
          'License :: OSI Approved :: GPL License',
          'Programming Language :: Python :: 2.7',
      ],
#      entry_points={
#          'console_scripts': [
#                'editscenario=editscenario.editscenario:main',
#                'nml2xml=editscenario.nml2xml:main',
#          ]
#      },
      packages=['xmlplot', 'xmlplot/data'],
      package_data={'xmlplot': ['icons/*', 'schemas/*/*']}, 
      include_package_data=True,
      zip_safe=False)
