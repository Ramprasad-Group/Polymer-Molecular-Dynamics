import pmd

if __name__ == '__main__':
    # Define the system
    system = pmd.SolventSystem(
        smiles='*CC*',  # change to polymer SMILES of your interest
        solvent_smiles='CCO',  # change to your solvent SMILES
        ru_nsolvent_ratio='0.1',
        density=0.8,
        nchains_total=50,
        ru_per_chain=25,
        builder=pmd.PSP(force_field='gaff2-am1bcc'))

    # Define LAMMPS simulation procedures
    lmp = pmd.Lammps(read_data_from=system)
    lmp.add_procedure(pmd.Minimization())  # avoid atom overlap
    lmp.add_procedure(pmd.Equilibration(Teq=300, Tmax=600))  # 21-step equil.
    lmp.add_procedure(
        pmd.MSDMeasurement(T=300,
                           group=system.solvent_group,
                           create_block_every=10000000,
                           duration=200000000,
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
