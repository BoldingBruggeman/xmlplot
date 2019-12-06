from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='xmlplot',
      version='0.9.17',
      description=' --- update - ',
      long_description=readme(),
      url='http://github.com/BoldingBruggeman/xmlplot',
      author='Jorn Bruggeman',
      author_email='jorn@bolding-bruggeman.com',
      license='GPL',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'Programming Language :: Python :: 2 :: Only',
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
      install_requires=['xmlstore>=0.9.7', 'numpy', 'matplotlib'],
      zip_safe=False)
