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
            input_param = ask_float(param, param)
            forcing_params.append(input_param)
        sim_first = int(ask_int('sim_first', 'first sim'))
        sim_last = int(ask_int('sim_last', 'last sim'))
        time_between_init_cond = int(
            ask_int('time_between_init_cond', 'time between consecutive initial conditions')
        )
        integration_time = float(
            ask_float('integration_time', 'time length of each simulation')
        )
        time_between_single_records = float(
            ask_float('time_between_single_records', 'time between records of one (first) node')
        )
        time_between_complete_records = float(
            ask_float('time_between_complete_records', 'time between records of all nodes')
        )
        sim_num = (sim_last - sim_first) + 1
        command = f"{EXECUTER} {EXECUTABLE} {forcing} {sim_first} {sim_num} " \
                  f"{time_between_init_cond} {integration_time} {time_between_single_records} " \
                  f"{time_between_complete_records} {' '.join(forcing_params)}"
        message = f"Run the following command: '{command}'?"
        confirmation = ask_confirmation(message)

    subprocess.Popen(command, shell=True, executable='/bin/bash')


if __name__ == '__main__':
    main()
