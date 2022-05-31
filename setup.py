from setuptools import setup

if __name__ == '__main__':
    # setup(name='pmd',
    #       version='0.2.1',
    #       author='Kuan-Hsuan Shen',
    #       author_email='kshen64@gatech.edu',
    #       description=('Automated generation of LAMMPS data and input '
    #                    'files for polymer molecular dynamics simulations'),
    #       keywords=['LAMMPS', 'polymer', 'SMILES'],
    #       url=('https://github.com/Ramprasad-Group'
    #            '/High-throughput-MD-simulations'),
    #       packages=find_packages(),
    #       python_requires='>=3.7',
    #       entry_points={
    #           'console_scripts': [
    #               'pmd-load = pmd.entry.load:main',
    #               'pmd-analyze = pmd.entry.analyze:main',
    #           ]
    #       },
    #       zip_safe=False)
    try:
        setup(use_scm_version={'version_scheme': 'no-guess-dev'})
    except Exception:
        print('\n\nAn error occurred while building the project, '
              'please ensure you have the most updated version of '
              'setuptools, setuptools_scm and wheel with:\n'
              '   pip install -U setuptools setuptools_scm wheel\n\n')
        raise
