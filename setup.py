from setuptools import setup
__version__ = "0.0.1"


setup(name='SurfaceMineDesignWB',
      version=__version__,
      packages=['SurfaceMineDesignWB',
                'SurfaceMineDesignWB.commands',
                'SurfaceMineDesignWB.descriptions',
                'SurfaceMineDesignWB.design_assets',
                'SurfaceMineDesignWB.features',
                'SurfaceMineDesignWB.ui',
                'SurfaceMineDesignWB.utils',
                ],
      maintainer="Denis_M",
      maintainer_email="denismikulich91@gmail.com",
      url="https://github.com/denismikulich91/SurfaceMineDesignWB",
      description="Parametric surface mine design tools and more",
      install_requires=["python3-shapely"], 
      include_package_data=True)
