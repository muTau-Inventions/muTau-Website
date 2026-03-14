from setuptools import setup, find_packages
import os
import re


def get_version():
    tags_dir = '.git/refs/tags/'
    
    if not os.path.exists(tags_dir):
        return "0.0.0"
    
    tag_names = []
    for tag_file in os.listdir(tags_dir):
        if re.match(r'^v?\d+\.\d+\.\d+', tag_file):
            clean_version = tag_file.lstrip('v')
            tag_names.append(clean_version)
    
    if not tag_names:
        return "0.0.0"
    
    tag_names.sort(key=lambda v: tuple(map(int, v.split('.'))), reverse=True)
    return tag_names[0]

setup(
    name="mutau-website",
    version=get_version(),
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
)