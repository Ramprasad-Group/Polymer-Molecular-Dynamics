from pathlib import Path

import pytest

from pmd.entry.template import create_script, decode_anwser

test_answer = {
    'system': '1. System (amorphous homopolymer)',
    'system_size': '1. By total number of atoms',
    'chain_length': '1. By number of atoms per chain',
    'builder': '1. opls-lbcc (PSP)',
    'lammps': '1. Glass transition temperature',
    'job': '1. Torque',
    'file_name': 'mkinput.py'
}
test_answer2 = {
    'system': '2. SolventSystem (homopolymer + solvent)',
    'system_size': '2. By total number of polymer chains',
    'chain_length': '2. By number of repeating units per chain',
    'builder': '4. gaff2-am1bcc (PSP)',
    'lammps': '2. Gas/solvent diffusivity',
    'job': '1. Torque',
    'file_name': 'mkinput_solvent.py'
}


@pytest.fixture
def test_data(data_path):
    return {
        'template_file': data_path / 'mkinput.py',
        'template_file_solvent': data_path / 'mkinput_solvent.py',
    }


def test_decode_anwser():
    expected_result = ('mkinput.py', 'System', 'natoms_total=10000',
                       'natoms_per_chain=150',
                       'PSP(force_field=\'opls-lbcc\')', 'TgMeasurement',
                       'Torque')
    actual_result = decode_anwser(test_answer)
    create_script(*actual_result)

    assert actual_result == expected_result


def test_create_script(test_data):
    p = Path('mkinput.py')
    result = decode_anwser(test_answer)
    create_script(*result)
    assert p.read_text() == test_data['template_file'].read_text()

    ps = Path('mkinput_solvent.py')
    result = decode_anwser(test_answer2)
    create_script(*result)
    assert ps.read_text() == test_data['template_file_solvent'].read_text()
