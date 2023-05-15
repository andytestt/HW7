from setuptools import setup, find_namespace_packages

setup(
    name='clean folder',
    version='1.0.0',
    author='Andrii',
    url="",
    author_email='your_email@gmail.com',
    include_package_data=True,
    description='A package for sorting and organizing files in a directory',
    license="",
    packages=find_namespace_packages(),
    entry_points={'console_scripts': ['startclean=clean_folder.clean:clean_folder']}
)
