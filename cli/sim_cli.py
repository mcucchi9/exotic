# -*- coding: utf-8 -*-
"""
hierarchical prompt usage example
"""
#from __future__ import print_function, unicode_literals
from pprint import pprint
import subprocess

from PyInquirer import style_from_dict, Token, prompt

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
    'linear': {'param': []},
    'sinusoidal': {'param': []}
}


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
        command = 'sbatch sim.sh {} {} {} {}'.format(forcing, ' '.join(forcing_params), sim_start, sim_num)
        message = "Run the following command: '{}'?".format(command)
        confirmation = ask_confirmation(message)


if __name__ == '__main__':
    main()
