from setuptools import setup

if __name__ == '__main__':
    try:
        # Metadata goes in setup.cfg. These are here for GitHub's dependency
        # graph and use_scm_version
        setup(name='pmd',
              install_requires=[
                  'importlib-metadata',
                  'pyyaml>=5.0',
                  'numpy>=1.0',
                  'pandas>=1.0',
                  'matplotlib>=3.0',
                  'scipy>=1.0',
                  'rdkit-pypi>=2022.3.2',
                  'emc-pypi>=1.0.0',
              ],
              extras_require={
                  'testing': ['setuptools', 'pytest', 'pytest-cov'],
              },
              use_scm_version={'version_scheme': 'no-guess-dev'})
    except Exception:
        print('\n\nAn error occurred while building the project, '
              'please ensure you have the most updated version of '
              'setuptools, setuptools_scm and wheel with:\n'
              '   pip install -U setuptools setuptools_scm wheel\n\n')
        raise
