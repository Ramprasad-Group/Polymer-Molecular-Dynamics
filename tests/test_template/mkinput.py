import pmd

if __name__ == '__main__':
    # Define the system
    system = pmd.System(
        smiles='*CC*',  # change to polymer SMILES of your interest
        density=0.8,
        natoms_total=10000,
        natoms_per_chain=150,
        builder=pmd.PSP(force_field='opls-lbcc'))

    # Define LAMMPS simulation procedures
    lmp = pmd.Lammps(read_data_from=system)
    lmp.add_procedure(pmd.Minimization())  # avoid atom overlap
    lmp.add_procedure(pmd.Equilibration(Teq=600, Tmax=1000))  # 21-step equil.
    lmp.add_procedure(
        pmd.TgMeasurement(Tinit=600,
                          Tfinal=100,
                          Tinterval=20,
                          step_duration=1000000,
                          dump_image=True,
                          reset_timestep_before_run=True))

    # Define job scheduler settings
    job = pmd.Torque(run_lammps=lmp,
                     jobname='Your-job-name',
                     project='GT-rramprasad3-CODA20',
                     nodes=1,
                     ppn=24,
                     walltime='24:00:00')

    # Create all the files to a folder
    run = pmd.Pmd(system=system, lammps=lmp, job=job)
    run.create(output_dir='.', save_config=True)
