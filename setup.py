from setuptools import setup, find_packages

setup(
    name="Surface Mine Designer",
    version="0.0.1",
    description="A FreeCAD workbench for parametric mine design and more",
    long_description="This workbench provides tools for creating parametric open-pit mine designs.",
    author="Your Name",
    author_email="denismikulich91@gmail.com",
    url="https://github.com/denismikulich91/SurfaceMineDesignWB",
    packages=find_packages(),
    install_requires=[
        "shapely",  # Add other dependencies here if needed
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Specify the minimum Python version your workbench supports
)
