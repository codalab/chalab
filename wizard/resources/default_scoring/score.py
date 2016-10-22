#!/usr/bin/env python

# Default scoring program for the Chalab wizard.
# Isabelle Guyon and Arthur Pesah, ChaLearn, August-November 2014

# ALL INFORMATION, SOFTWARE, DOCUMENTATION, AND DATA ARE PROVIDED "AS-IS". 
# ISABELLE GUYON, CHALEARN, AND/OR OTHER ORGANIZERS OR CODE AUTHORS DISCLAIM
# ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR ANY PARTICULAR PURPOSE, AND THE
# WARRANTY OF NON-INFRINGEMENT OF ANY THIRD PARTY'S INTELLECTUAL PROPERTY RIGHTS. 
# IN NO EVENT SHALL ISABELLE GUYON AND/OR OTHER ORGANIZERS BE LIABLE FOR ANY SPECIAL, 
# INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF SOFTWARE, DOCUMENTS, MATERIALS, 
# PUBLICATIONS, OR INFORMATION MADE AVAILABLE FOR THE CHALLENGE. 

# Some libraries and options
import os
import sys
from subprocess import call

from . import libscores as l

# Default I/O directories:
root_dir = "/Users/isabelleguyon/Documents/Projects/Codalab/AutoMLcompetition/StartingKit/"
default_input_dir = root_dir + "scoring_input5"
default_output_dir = root_dir + "scoring_output5"

# Debug flag 0: no debug, 1: show all scores, 2: also show version amd listing of dir
debug_mode = 1

# Constant used for a missing score
missing_score = -0.999999

# Version number
scoring_version = 0.9


def generate_result(name, input_dir, output_dir):
    submission = os.path.join(input_dir, 'res', '%s.predict' % name)

    if os.path.exists(submission):
        return submission

    program = os.path.join(input_dir, 'res', '%s.program' % name)
    call([program, submission])

    return submission


def evaluate_submission(name, input_dir, output_dir):
    submission_file = os.path.join(input_dir, 'res', '%s.predict' % name)
    solution_file = os.path.join(input_dir, 'ref', '%s.solution' % name)
    info_file = os.path.join(input_dir, 'ref', '%s_public.info' % name)

    info = l.get_info(info_file)
    task_name, metric_name = info['task'], info['metric']

    solution = l.read_array(solution_file)
    prediction = l.read_array(submission_file)

    # Prepare the data
    if info['metric'] == 'r2_metric' or info['metric'] == 'a_metric':
        solution, prediction = l.sanitize_arrays(solution, prediction)
    else:
        [solution, prediction] = l.normalize_array(solution, prediction)

    score = getattr(l, info['metric'])(solution, prediction, task_name)

    return score


def main(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # Get all the solution files from the solution directory
    solution_files = sorted(l.ls(os.path.join(input_dir, 'ref', '*.solution')))
    solution_names = [os.path.splitext(os.path.basename(x))[0] for x in solution_files]

    generated = [generate_result(x, input_dir, output_dir) for x in solution_names]
    scores = [evaluate_submission(x, input_dir, output_dir) for x in solution_names]

    with open(os.path.join(output_dir, 'scores.txt'), 'wb') as score_f:
        score_f.writelines(['set%d_score: %0.12f' % (i + 1, score)
                            for i, score in enumerate(scores)])


if __name__ == '__main__':
    main(*sys.argv[1:])
