from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='vitivinicultura_flask_api-package',
    version='1.0.0',
    packages=find_packages(),
    description='Descricao da sua lib vitivinicultura_flask_api',
    author='Pedro Ulisses',
    author_email='ulissesph@gmail.com',
    url='https://github.com/ordepzero/vitivinicultura_flask_api',  
    license='MIT',  
    long_description=long_description,
    long_description_content_type='text/markdown'
)
