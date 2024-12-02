from setuptools import setup
import os


setup(name='SurfaceMineDesign',
      version="0.0.1",
      packages=['SurfaceMineDesignWB'],
      maintainer="dmh5",
      maintainer_email="denismikulich91@gmail.com",
      url="https://github.com/denismikulich91/SurfaceMineDesignWB",
      description="Parametric surface mine design tools and more",
      install_requires=['shapely'],  # should be satisfied by FreeCAD's system dependencies already
      include_package_data=True)
