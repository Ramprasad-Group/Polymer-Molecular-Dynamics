# Polymer Molecular Dynamics [![License](https://img.shields.io/badge/license-MIT-blue.svg)](http://opensource.org/licenses/MIT)

Python toolkit and guides for molecular dynamics prediction of polymer properties.

- Quick overview - Check out the [Introduction page](https://high-throughput-pmd.netlify.app/docs/intro)
- Documentation - You can find it [on the website](https://high-throughput-pmd.netlify.app/api/overview).

## Guides and scripts

You can calculate various polymer properties from MD simulations with this package, including:

- Glass transition temperature (Tg) - [[Guide](http://high-throughput-pmd.netlify.app/docs/guides/glass-transition-temperature)] [[Scripts](https://github.com/Ramprasad-Group/High-Throughput-Polymer-MD-Simulations/tree/main/scripts/Tg)]
- Gas diffusivity - [[Guide](http://high-throughput-pmd.netlify.app/docs/guides/gas-diffusivity)] [[Scripts](https://github.com/Ramprasad-Group/High-Throughput-Polymer-MD-Simulations/tree/main/scripts/Gas_diffusivity)]
- Solvent diffusivity - [[Guide](http://high-throughput-pmd.netlify.app/docs/guides/solvent-diffusivity)] [[Scripts](https://github.com/Ramprasad-Group/High-Throughput-Polymer-MD-Simulations/tree/main/scripts/Solvent_diffusivity)]
- Viscosity - [[Guide](https://high-throughput-pmd.netlify.app/docs/guides/viscosity)][[Scripts](https://github.com/Ramprasad-Group/Polymer-Molecular-Dynamics/tree/main/scripts/Shear_deformation)]
- Mechanical properties (Young's modulus, tensile strengths) - [[Scripts](https://github.com/Ramprasad-Group/Polymer-Molecular-Dynamics/tree/main/scripts/Tensile_deformationy)]
- Thermal conductivity - In-progress
- Solubility - Planned
- Melting temperature (Tm) - Planned

## Example

Below is an example where we use PMD to generate LAMMPS data and input files for Tg measurement with a list of SMILES strings.

### From a python script
#### example.py
```python
import pmd

# A list of polymer SMILES strings to create simulations for
smiles_list = ['*CC*', '*CC(*)CC', '*CC(*)CCCC','*CC(*)c1ccccc1']

for smiles in smiles_list:
    # Define polymer and system specs
    syst = pmd.System(smiles=smiles, force_field=pmd.OPLS(), density=0.8,
                      natoms_total=5000, natoms_per_chain=150)

    # Customize LAMMPS simulation
    lmp = pmd.Lammps(read_data_from=syst,
                     procedures=[pmd.Minimization(min_style='cg'),
                                 pmd.Equilibration(Teq=600, Tmax=800),
                                 pmd.TgMeasurement(Tinit=600, Tfinal=200)])

    # Create job scheduler settings
    job = pmd.Torque(run_lammps=lmp, jobname=smiles, project='Your-project-id',
                     nodes=2, ppn=24, walltime='48:00:00')

    # Generate all necessary files at each SMILES folder
    run = pmd.Pmd(system=syst, lammps=lmp, job=job)
    run.create(output_dir=smiles, save_config=True)
```

### From the command line
PMD can generate config file in YAML format out of the box, which helps you keep track of all the parameters used for each simulation. At the same time, you can build PMD systems directly via the config file from the command line. For example, run the `pmd-load` command with the following `config.yaml` to get exact same setup as the above example python script (but only for '\*CC\*').

```bash
$ pmd-load config.yaml [-o output_dir]
```
#### config.yaml
```yaml
pmd.System:
  smiles: '*CC*'
  density: 0.8
  force_field: pmd.OPLS
  natoms_total: 5000
  natoms_per_chain: 150
  data_fname: data.lmps
pmd.Lammps:
  read_data: data.lmps # Has to match data_fname if build from a yaml file
  lmp_input_fname: lmp.in
  procedures:
  - pmd.Minimization:
      min_style: cg
  - pmd.Equilibration:
      Teq: 600
      Tmax: 800
  - pmd.TgMeasurement:
      Tinit: 600
      Tfinal: 200
pmd.Torque:
  run_lammps: lmp.in # Has to match lmp_input_fname if build from a yaml file
  jobname: '*CC*'
  project: Your-project-id
  nodes: 2
  ppn: 24
  walltime: '48:00:00'
  job_fname: job.pbs
```

## Installation

```bash
pip install pmd
```

### Prerequisites

- [PSP](https://github.com/Ramprasad-Group/PSP) - for generating polymer topology
- [RDKit](https://www.rdkit.org/) - for getting molecule info such as molecular weight

PSP and RDKit are required to be installed for the package to fully function.
