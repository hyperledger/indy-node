import argparse


parser = argparse.ArgumentParser(description='The script another load script with different paramters')

parser.add_argument('-c', '--clients', default=0, type=int, required=False, dest='clients',
                    help='Number of client you want to create. '
                         '0 or less means equal to number of available CPUs. '
                         'Default value is 0')
