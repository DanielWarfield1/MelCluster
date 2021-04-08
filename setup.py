#____requirements____

#pip.req
def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]

reqs = parse_requirements('requirements.txt')

#____info____
from setuptools import setup, find_packages

setup(name='MelCluster',
      version='1.0.0',
      description='Library containing functions and programs for clustering mel spectrogram data',
      url='https://github.com/DanielWarfield1/MelCluster',
      author='Daniel Warfield',
      author_email='danielwarfield1@gmail.com',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      install_requires=reqs)
