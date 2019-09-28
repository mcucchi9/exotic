# -*- coding: utf-8 -*-
"""
hierarchical prompt usage example
"""
import subprocess
import os
import yaml

from PyInquirer import style_from_dict, Token, prompt

dirname = os.path.dirname(__file__)

style = style_from_dict({
    Token.Separator: '#cc5454',
    Token.QuestionMark: '#673ab7 bold',
    Token.Selected: '#cc5454',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#f44336 bold',
    Token.Question: '',
})

FORCINGS = {
    'constant': {'param': ['intensity']},
    'delta': {'param': ['base intensity', 'delta intensity']},
    'step': {'param': ['base intensity', 'delta intensity']},
    'linear': {'param': ['base intensity', 'linear coefficient']},
    'sinusoidal': {'param': ['base intensity', 'epsilon', 'omega']}
}

# Read configuration file
configfile_path = os.path.join(dirname, '../config.yaml')
try:
    with open(configfile_path) as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
except FileNotFoundError:
    print('config.yaml not found')

EXECUTABLES_DIR = os.path.join(dirname, '../batch')
EXECUTABLE = os.path.join(EXECUTABLES_DIR, 'sim.sh')
try:
    EXECUTER = config['executer']
except ValueError:
    print("config.yaml does not contain configuration for executer")


def ask_forcing():
    forcings_prompt = {
        'type': 'list',
        'name': 'forcing',
        'message': 'select forcing',
        'choices': sorted(list(FORCINGS))
    }
    answers = prompt(forcings_prompt)
    return answers['forcing']


def ask_float(name, message):
    float_prompt = {
        'type': 'input',
        'name': name,
        'message': message,
    }
    answers = prompt(float_prompt)
    return answers[name]


def ask_int(name, message):
    int_prompt = {
        'type': 'input',
        'name': name,
        'message': message,
    }
    answers = prompt(int_prompt)
    return answers[name]


def ask_confirmation(message):
    confirmation_prompt = {
        'type': 'confirm',
        'name': 'confirmation',
        'message': message,
    }
    answers = prompt(confirmation_prompt)
    return answers['confirmation']


def main():
    print('Simulation CLI')
    confirmation = False
    while not confirmation:
        forcing = ask_forcing()
        forcing_params = []
        for param in FORCINGS[forcing]['param']:
            input_param = ask_float(param, 'insert ' + param)
            forcing_params.append(input_param)
        sim_start = int(ask_int('sim_start', 'insert sim_start'))
        sim_num = int(ask_int('sim_num', 'insert sim_num'))
        take_init_every_steps = int(ask_int('take_init_every_steps', 'insert take_init_every_steps'))
        command = '{cmd} {executable} {forcing} {sim_start} {sim_num} {take_init_every_steps} {forcing_params}'.format(
            cmd=EXECUTER,
            executable=EXECUTABLE,
            forcing=forcing,
            sim_start=sim_start,
            sim_num=sim_num,
            take_init_every_steps=take_init_every_steps,
            forcing_params=' '.join(forcing_params)
        )
        message = "Run the following command: '{}'?".format(command)
        confirmation = ask_confirmation(message)

    subprocess.Popen(command, shell=True, executable='/bin/bash')


if __name__ == '__main__':
    main()
