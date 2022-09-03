# :coding: utf-8
# :copyright: Copyright (c) 2022 Luna Digital, Ltd.

import os
import re
import sys
import subprocess
import shutil

from setuptools import setup, find_packages
import setuptools

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
SOURCE_PATH = os.path.join(ROOT_PATH, 'source')
README_PATH = os.path.join(ROOT_PATH, 'README.md')
RESOURCE_PATH = os.path.join(ROOT_PATH, 'resource')
HOOK_PATH = os.path.join(ROOT_PATH, 'hook')
BUILD_PATH = os.path.join(ROOT_PATH, 'build')

class BuildPlugin(setuptools.Command):
    ''' Build plugin. '''
    description = 'Download dependencies and build plugin.'

    user_options = []

    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass

    def run(self):
        ''' Run the build step. '''
        import setuptools_scm

        release = setuptools_scm.get_version(version_scheme='post-release')
        VERSION = '.'.join(release.split('.')[:3])
        global STAGING_PATH
        STAGING_PATH = os.path.join(BUILD_PATH, 'ftrack-connect-pipeline-blender{}'.format(VERSION))

        # Clean staging path
        shutil.rmtree(STAGING_PATH, ignore_errors=True)

        # Copy resource files
        shutil.copytree(RESOURCE_PATH, os.path.join(STAGING_PATH, 'resource'))

        # Copy plugin files
        shutil.copytree(RESOURCE_PATH, os.path.join(STAGING_PATH, 'hook'))
        
        dependencies_path = os.path.join(STAGING_PATH, 'dependencies')

        os.makedirs(dependencies_path)

        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '.', '--target', dependencies_path]
        )

        shutil.make_archive(
            os.path.join(BUILD_PATH, 'ftrack-connect-pipeline-blender-{}'.format(VERSION)),
            'zip',
            STAGING_PATH
        )

version_template = '''
# :coding: utf-8
# :copyright: Copyright (c) 2022 Luna Digital, Ltd.

__version__ = {version!r}
'''

# Configuration
setup(
    name='ftrack-connect-pipeline-blender',
    description='A dialog to publish package from Blender to ftrack',
    long_description=open(README_PATH).read(),
    keywords='ftrack',
    url='https://github.com/lunadigital/ftrack-connect-pipeline-blender',
    author='Luna Digital, Ltd.',
    author_email='',
    license='Apache License (2.0)',
    packages=find_packages(SOURCE_PATH),
    package_dir={'': 'source'},
    use_scm_version={
        'write_to': 'source/ftrack_connect_pipeline_blender/_version.py',
        'write_to_template': version_template,
        'version_scheme': 'post-release'
    },
    setup_requires=[
        'setuptools>=44.0.0',
        'setuptools_scm'
    ],
    cmdclass={
        'build_plugin': BuildPlugin
    },
    zip_safe=False
)