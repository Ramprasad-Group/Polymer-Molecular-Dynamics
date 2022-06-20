from typing import Dict, Optional, Tuple

import inquirer

from pmd.util.Log import Pmdlogging

SYSTEM_OPTIONS = ('System', 'SolventSystem', 'GasSystem')
SYSTEM_SIZE_OPTIONS = ('natoms_total=10000', 'nchains_total=50')
CHAIN_LENGTH_OPTIONS = ('natoms_per_chain=150', 'ru_per_chain=25',
                        'mw_per_chain=1000')
BUILDER_OPTIONS = ('PSP(force_field=\'opls-lbcc\')',
                   'PSP(force_field=\'opls-cm1a\')',
                   'PSP(force_field=\'gaff2-gasteiger\')',
                   'PSP(force_field=\'gaff2-am1bcc\')',
                   'EMC(force_field=\'pcff\'', 'EMC(force_field=\'opls-aa\')',
                   'EMC(force_field=\'opls-ua\'',
                   'EMC(force_field=\'trappe\')')
JOB_OPTIONS = ('Torque', 'Slurm', None)

LAMMPS_FIELDS = {
    'TgMeasurement': [
        'Tinit=600', 'Tfinal=100', 'Tinterval=20', 'step_duration=1000000',
        'dump_image=True', 'reset_timestep_before_run=True'
    ],
    'MSDMeasurement': [
        'T=300', 'group=system.solvent_group', 'create_block_every=10000000',
        'duration=200000000', 'dump_image=True',
        'reset_timestep_before_run=True'
    ],
    'ShearDeformation': [
        'duration=10**7', 'erate=10**-6', 'T=300', 'dump_image=True',
        'reset_timestep_before_run=True'
    ],
    'TensileDeformation': [
        'duration=10**7', 'erate=10**-6', 'T=300', 'P=1', 'dump_image=True',
        'reset_timestep_before_run=True'
    ],
    'HeatFluxMeasurement': [
        'duration=10**7', 'T=300', 'dump_image=True',
        'reset_timestep_before_run=True'
    ]
}


def main() -> None:
    questions = [
        inquirer.List(
            'system',
            message='What kind of system do you need?',
            choices=[
                '1. System (amorphous homopolymer)',
                '2. SolventSystem (homopolymer + solvent)',
                '3. GasSystem (homopolymer + gas)'
            ],
        ),
        inquirer.List(
            'system_size',
            message='How would you determine the system size?',
            choices=[
                '1. By total number of atoms',
                '2. By total number of polymer chains'
            ],
        ),
        inquirer.List(
            'chain_length',
            message='How would you determine the polymer chain length?',
            choices=[
                '1. By number of atoms per chain',
                '2. By number of repeating units per chain',
                '3. By polymer molecular weight'
            ],
        ),
        inquirer.List(
            'builder',
            message='What force field (Builder) do you want to use?',
            choices=[
                '1. opls-lbcc (PSP)', '2. opls-cm1a (PSP)',
                '3. gaff2-gasteiger (PSP)', '4. gaff2-am1bcc (PSP)',
                '5. pcff (EMC)', '6. opls-aa (EMC)', '7. opls-ua (EMC)',
                '8. trappe (EMC)'
            ],
        ),
        inquirer.List(
            'lammps',
            message='What property do you want to compute?',
            choices=[
                '1. Glass transition temperature',
                '2. Gas/solvent diffusivity', '3. Viscosity',
                '4. Mechanical properties', '5. Thermal conductivity'
            ],
        ),
        inquirer.List(
            'job',
            message='What job scheduling system do you use?',
            choices=['1. Torque', '2. Slurm', '3. N/A (run locally)'],
        ),
        inquirer.Text('file_name',
                      message='Create input script to file',
                      default='mkinput.py'),
    ]

    answers = inquirer.prompt(questions)
    (file_name, system, system_size, chain_length, builder, lammps,
     job) = decode_anwser(answers)
    create_script(file_name, system, system_size, chain_length, builder,
                  lammps, job)
    Pmdlogging.info(f'Template PMD script - {file_name} successfully created!')
    Pmdlogging.info('Change the fields in the file to customize your system '
                    'and simulation. Then create files by running:\n'
                    f'       $ python {file_name}')


def decode_anwser(answers: Dict) -> Tuple[str]:
    file_name = answers['file_name']

    # replace the dict's values with the leading numbers
    answers = {
        k: int(v[0]) - 1
        for k, v in answers.items() if k != 'file_name'
    }

    # use the leading number as index to get the options
    system = SYSTEM_OPTIONS[answers['system']]
    system_size = SYSTEM_SIZE_OPTIONS[answers['system_size']]
    chain_length = CHAIN_LENGTH_OPTIONS[answers['chain_length']]
    builder = BUILDER_OPTIONS[answers['builder']]
    lammps = [*LAMMPS_FIELDS][answers['lammps']]
    job = JOB_OPTIONS[answers['job']]

    return file_name, system, system_size, chain_length, builder, lammps, job


def create_script(file_name: str, system: str, system_size: str,
                  chain_length: str, builder: str, lammps: str,
                  job: Optional[str]) -> None:
    # indents
    indent = ' ' * 4
    lammps_indent = ' ' * len(f'{indent}{indent}pmd.{lammps}(')
    job_indent = ' ' * len(f'{indent}job = pmd.{job}(')

    # data
    Teq = 300 if lammps != 'TgMeasurement' else 600
    Tmax = 600 if lammps != 'TgMeasurement' else 1000
    process_number_field = 'ppn' if job == 'Torque' else 'ntasks_per_node'
    time_number_field = 'walltime' if job == 'Torque' else 'time'

    with open(file_name, 'w') as f:
        f.write('import pmd\n')
        f.write('\n')
        f.write('if __name__ == \'__main__\':\n')

        # write the System section
        f.write(f'{indent}# Define the system\n')
        f.write(f'{indent}system = pmd.{system}(\n')
        f.write(f'{indent}{indent}smiles=\'*CC*\',  '
                '# change to polymer SMILES of your interest\n')
        if system == 'SolventSystem':
            f.write(f'{indent}{indent}solvent_smiles=\'CCO\',  '
                    '# change to your solvent SMILES\n')
            f.write(f'{indent}{indent}ru_nsolvent_ratio=\'0.1\',\n')
        f.write(f'{indent}{indent}density=0.8,\n')
        f.write(f'{indent}{indent}{system_size},\n')
        f.write(f'{indent}{indent}{chain_length},\n')
        f.write(f'{indent}{indent}builder=pmd.{builder})\n')
        f.write('\n')

        # write the Lammps section
        f.write(f'{indent}# Define LAMMPS simulation procedures\n')
        f.write(f'{indent}lmp = pmd.Lammps(read_data_from=system)\n')
        f.write(f'{indent}lmp.add_procedure(pmd.Minimization())  '
                '# avoid atom overlap\n')
        f.write(f'{indent}lmp.add_procedure(pmd.Equilibration(Teq={Teq}, '
                f'Tmax={Tmax}))  # 21-step equil.\n')
        f.write(f'{indent}lmp.add_procedure(\n')
        for i, v in enumerate(LAMMPS_FIELDS[lammps]):
            if i == 0:
                f.write(f'{indent}{indent}pmd.{lammps}({v},\n')
            # special case to change the MSDMeasurement group dynamically
            elif (i == 1 and lammps == 'MSDMeasurement'
                  and system != 'SolventSystem'):
                f.write(f'{lammps_indent}group=\'type 1\', '
                        '# change the atom group to track\n')
            elif i == len(LAMMPS_FIELDS[lammps]) - 1:
                f.write(f'{lammps_indent}{v}))\n')
            else:
                f.write(f'{lammps_indent}{v},\n')

        f.write('\n')

        # write the Job section
        if job:
            f.write(f'{indent}# Define job scheduler settings\n')
            f.write(f'{indent}job = pmd.{job}(run_lammps=lmp,\n')
            f.write(f'{job_indent}jobname=\'Your-job-name\',\n')
            f.write(f'{job_indent}project=\'GT-rramprasad3-CODA20\',\n')
            f.write(f'{job_indent}nodes=1,\n')
            f.write(f'{job_indent}{process_number_field}=24,\n')
            f.write(f'{job_indent}{time_number_field}=\'24:00:00\')\n')
            f.write('\n')

        # write the Pmd section
        pmd_job = ', job=job' if job else ''
        f.write(f'{indent}# Create all the files to a folder\n')
        f.write(f'{indent}run = pmd.Pmd(system=system, lammps=lmp{pmd_job})'
                '\n')
        f.write(f'{indent}run.create(output_dir=\'.\', save_config=True)\n')


if __name__ == '__main__':
    main()
