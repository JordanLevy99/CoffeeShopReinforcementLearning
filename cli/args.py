import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-name', default='default', type=str, metavar='run name',
                        help='Name with which to call our run')
    parser.add_argument('-e', '--epoch', default=1, type=int, metavar='num epochs',
                        help='Number of epochs to run')
    parser.add_argument('--baseline', action='store_true',
                        help='Run baseline model only, otherwise will run RL model. '
                             'May expand this to be more than boolean once we have more models.')
    parser.add_argument('--learn', action='store_true',
                        help='If true, will (in theory) activate model learning. '
                             'Otherwise it will be in data collection mode.')
    return parser.parse_args()
