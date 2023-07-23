import argparse
import os
import random


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--from_id', type=str)

    args = parser.parse_args()

    return args
