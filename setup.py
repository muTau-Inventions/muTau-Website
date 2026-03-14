from setuptools import setup, find_packages
import subprocess
import os


def get_version():
    if not os.path.exists('.git'):
        return "0.0.0"
    
    try:
        result = subprocess.run(
            ['git', 'describe', '--tags', '--abbrev=0'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip().lstrip('v')
    except subprocess.CalledProcessError:
        result = subprocess.run(
            ['git', 'tag', '--list', '--sort=-v:refname'],
            capture_output=True, text=True, check=True
        )
        tags = [tag.strip().lstrip('v') for tag in result.stdout.splitlines()]
        return tags[0] if tags else "0.0.0"

setup(
    name="mutau-website",
    version=get_version(),
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
)