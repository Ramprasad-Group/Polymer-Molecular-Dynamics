from pmd.core import GAFF2, OPLS, System

test_smiles = '*CC*'
test_force_field = GAFF2()
syst = System('*CC*', test_force_field, 0.8, 5000, natoms_per_chain=150)


def test_system_initialization():
    assert syst.smiles == test_smiles
    assert syst.force_field == test_force_field


def test_system_update():
    new_smiles = '*CC(*)CC'
    new_force_field = OPLS()
    syst.smiles = new_smiles
    assert syst.smiles == new_smiles
    assert syst.force_field == new_force_field
