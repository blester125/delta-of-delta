import re
from setuptools import setup, find_packages

def get_version(project_name):
    regex = re.compile(r"""^__version__ = ["'](\d+\.\d+\.\d+(?:a|b|rc)?(?:\d)*?)["']$""")
    with open(f"{project_name}/__init__.py") as f:
        for line in f:
            m = regex.match(line.rstrip("\n"))
            if m is not None:
                return m.groups(1)[0]

def convert_images(text):
    image_regex = re.compile(r"!\[(.*?)\]\((.*?)\)")
    return image_regex.sub(r'<img src="\2" alt="\1">', text)

class About(object):
    NAME='delta-of-delta'
    VERSION=get_version('delta_of_delta')
    AUTHOR='blester125'
    EMAIL=f'{AUTHOR}@gmail.com'
    URL=f'https://github.com/{AUTHOR}/{NAME}'
    DL_URL=f'{URL}/archive/{VERSION}.tar.gz'
    LICENSE='MIT'
    DESCRIPTION='Delta-of-delta'

ext_modules = [
]

setup(
    name=About.NAME,
    version=About.VERSION,
    description=About.DESCRIPTION,
    long_description=convert_images(open('README.md').read()),
    long_description_content_type="text/markdown",
    author=About.AUTHOR,
    author_email=About.EMAIL,
    url=About.URL,
    download_url=About.DL_URL,
    license=About.LICENSE,
    python_requires='>=3.7',
    packages=find_packages(),
    package_data={
        'delta-of-delta': [
        ],
    },
    include_package_data=True,
    install_requires=[
    ],
    setup_requires=[
    ],
    extras_require={
        'test': ['pytest'],
    },
    keywords=[],
    ext_modules=ext_modules,
    entry_points={
        'console_scripts': [
            'delta-of-delta-demo=delta_of_delta.delta_of_delta:main'
        ],
    },
    classifiers={
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering',
    },
)
