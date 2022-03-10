from os import path

from setuptools import find_packages, setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    l_d = f.read()

# Get the version.
# version = {}
# with open("nlmod/version.py") as fp:
#     exec(fp.read(), version)

setup(
    name='dawacotools',
    version='0.0.1',
    description='Dawaco tools by PWN',
    long_description=l_d,
    long_description_content_type="text/markdown",
    url='https://github.com/bdestombe/python-dawaco-tools',
    author='Bas des Tombe',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    platforms='Windows, Mac OS-X',
    # install_requires=['flopy>=3.3.2',
    #                   'xarray>=0.16.1',
	# 				  'rasterio>=1.1.0',
	# 				  'owslib>=0.24.1',
	# 				  'hydropandas>=0.3.0',
	# 				  'netcdf4>=1.5.7',
	# 				  'pyshp>=2.1.3',
	# 				  'rtree>=0.9.7',
	# 				  'openpyxl>=3.0.7',
    #                   'matplotlib'
    #                   ],
    # packages=find_packages(exclude=[]),
    # package_data={"nlmod": ["data/*"]},
    # include_package_data=True
)
