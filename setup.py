from pip.req import parse_requirements
from setuptools import find_packages
from setuptools import setup
from setuptools.command.install import install as _install

import os
if not os.path.exists('darknet'):
	os.system('git clone https://github.com/fizyr/keras-retinanet.git')
	os.chdir('keras-retinanet')
	os.system('pip install .')
	os.system('python setup.py build_ext --inplace')
	
	os.system('git clone https://github.com/AlexeyAB/darknet.git')
	os.chdir('darknet')
	os.system("sed -i 's/LIBSO=0/LIBSO=1/g' Makefile")
	os.system('make')
	os.system('cp libdarknet.so ..')

install_requirements = parse_requirements('requirements.txt', session=False)
requirements = [str(ir.req) for ir in install_requirements]


class install(_install):

    def run(self):
        _install.run(self)


setup(
    name='bwh-prometheus-exporter',
    version='0.4.0',
    author=u'Johannes Rumpf',
    author_email='johannes.rumpf@gmail.com',
    description='webcam : bee, wasp, hornet detector and metrics exporter',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    cmdclass={'install': install},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.7',
        ],
    )
