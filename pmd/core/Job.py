import os
from typing import Union

from pmd.core.Lammps import Lammps
from pmd.util import Pmdlogging, build_dir


class Job():

    def __init__(self, run_lammps: Union[Lammps, str], jobname: str,
                 job_fname: str):
        self._run_lammps = run_lammps.lmp_input_fname if isinstance(
            run_lammps, Lammps) else run_lammps
        self._jobname = jobname
        self._job_fname = job_fname

    def __repr__(self) -> str:
        return type(self).__name__

    def write_job(self, output_dir: str):
        raise NotImplementedError

    def completion_log(self, output_dir: str):
        Pmdlogging.info(f'Job file - {self._job_fname} '
                        f'successfully created in {output_dir}')


class Torque(Job):
    '''Template Torque object to contain Torque job initialization settings

    Attributes:
        jobname (str): Job name
        project (str): Project name
        nodes (int): Number of nodes
        ppn (int): Number of processors (CPU)
        walltime (str): Job walltime (in format of HH:MM:SS)
        gpus (int): Number of processors (GPU)
        job_fname (str): Name of the PBS input file; default: `"job.pbs"`
    '''

    def __init__(self,
                 run_lammps: Lammps,
                 jobname: str,
                 project: str,
                 nodes: int,
                 ppn: int,
                 walltime: str,
                 gpus: int = None,
                 job_fname: str = 'job.pbs'):

        super().__init__(run_lammps, jobname, job_fname)
        self._project = project
        self._nodes = nodes
        self._ppn = ppn
        self._walltime = walltime
        self._gpus = gpus

    @build_dir
    def write_job(self, output_dir: str = '.') -> None:
        '''Method to make the Torque job scheduler input file

        Parameters:
            output_dir (str): Directory for the Torque input file; default:
            `"."`

        Returns:
            None
        '''

        with open(os.path.join(output_dir, self._job_fname), 'w') as f:
            f.write(f'#PBS -A {self._project}\n')
            f.write('#PBS -q inferno\n')
            f.write(f'#PBS -N {self._jobname}\n')
            if self._gpus:
                f.write(f'#PBS -l nodes={self._nodes}:ppn={self._ppn}:'
                        f'gpus={self._gpus}:RTX6000:default\n')
            else:
                f.write(f'#PBS -l nodes={self._nodes}:ppn={self._ppn}\n')
            f.write(f'#PBS -l walltime={self._walltime}\n')
            f.write('#PBS -j oe\n')
            f.write('#PBS -o out.$PBS_JOBID\n')
            f.write('\n')
            f.write('cd $PBS_O_WORKDIR\n')
            if self._gpus:
                f.write(
                    'module load gcc/8.3.0 mvapich2/2.3.2 lammps-gpu/29Oct20\n'
                )
                f.write(f'mpirun -np {self._nodes * self._ppn} '
                        f'lmp -sf gpu -pk gpu {self._gpus} -in '
                        f'{self._run_lammps}\n')
            else:
                f.write(
                    'module load intel/19.0.5 mvapich2/2.3.4 lammps/09Jan20\n')
                f.write(f'mpirun -np { self._nodes * self._ppn} '
                        f'lmp -in {self._run_lammps}')

        super().completion_log(output_dir)


class Slurm(Job):
    '''Template Slurm object to contain Slurm job initialization settings

    Attributes:
        jobname (str): Job name
        nodes (int): Number of nodes
        ntasks_per_node (int): Number of processors (CPU)
        time (str): Job time
        gpus (int): Number of processors (GPU)
        job_fname (str): Name of the Slurm input file; default: `"job.sh"`
    '''

    def __init__(self,
                 run_lammps: Lammps,
                 jobname: str,
                 nodes: int,
                 ntasks_per_node: int,
                 time: str,
                 gpus: int = 0,
                 job_fname: str = 'job.sh'):

        super().__init__(run_lammps, jobname, job_fname)
        self._nodes = nodes
        self._ntasks_per_node = ntasks_per_node
        self._time = time
        self._gpus = gpus

    @build_dir
    def write_job(self, output_dir: str = '.') -> None:
        '''Method to make the Slurm job scheduler input file

        Parameters:
            output_dir (str): Directory for the Slurm input file; default: `.`

        Returns:
            None
        '''
        with open(os.path.join(output_dir, self._job_fname), 'w') as f:
            f.write('#!/bin/bash')
            f.write(f'#SBATCH --job-name={self._jobname}\n')
            f.write('#SBATCH -o out.o%j \n')
            f.write('#SBATCH -e err.e%j \n')
            f.write(f'#SBATCH --nodes={self._nodes}\n')
            if self._gpus:
                f.write(f'#SBATCH --gpus={self._gpus}\n')
            else:
                f.write(
                    f'#SBATCH --ntasks-per-node={ self._ntasks_per_node}\n')
            f.write(f'#SBATCH --time={self._time}\n')
            if self._gpus:
                # TODO
                print('Have not implemented GPU Slurm yet')
            else:
                f.write('module load intel/18.0.2 impi/18.0.2 lammps/9Jan20\n')
                f.write(f'ibrun lmp -in {self._run_lammps}\n')

        super().completion_log(output_dir)
