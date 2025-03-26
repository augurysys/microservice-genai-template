import setuptools


setuptools.setup(
    name='microservice-genai-template',
    description='Augury Microservice Template',
    version='0.0.1',
    packages=setuptools.find_packages(),
    package_data={'': ['*.json']},
    include_package_data=True,
    license="Proprietary",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        'License :: Other/Proprietary License',
        'Private :: Do Not Upload',
    ],
)
