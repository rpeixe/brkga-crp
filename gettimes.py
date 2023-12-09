###############################################################################
# main_complete.py: comprehensive script for BRKGA-MP-IPR experiments
#                   using Python.
#
# (c) Copyright 2019, Carlos Eduardo de Andrade.
# All Rights Reserved.
#
# This code is released under LICENSE.md.
#
# Created on:  Nov 18, 2019 by ceandrade
# Last update: Nov 18, 2019 by ceandrade
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###############################################################################
"""
Usage:
  main.py -c <config_file> -s <seed> -r <stop_rule> \
-a <stop_arg> -t <max_time> -i <instance_file> [--no_evolution]

  main.py (-h | --help)

Options:
  -c --config_file <arg>    Text file with the BRKGA-MP-IPR parameters.

  -s --seed <arg>           Seed for the random number generator.

  -r --stop_rule <arg>      Stop rule where:
                            - (G)enerations: number of evolutionary
                              generations.
                            - (I)terations: maximum number of generations
                              without improvement in the solutions.
                            - (T)arget: runs until obtains the target value.

  -a --stop_arg <arg>       Argument value for '-r'.

  -t --max_time <arg>       Maximum time in seconds.

  -i --instance_file <arg>  Instance file.

  --no_evolution      If supplied, no evolutionary operators are applied. So,
                      the algorithm becomes a simple multi-start algorithm.

  -h --help           Produce help message.
"""

from copy import deepcopy
from datetime import datetime
from os.path import basename
import time

import docopt

from brkga_mp_ipr.algorithm import BrkgaMpIpr
from brkga_mp_ipr.enums import ParsingEnum, Sense
from brkga_mp_ipr.types_io import load_configuration

from crp_instance import CrpInstance
from crp_decoder import CrpDecoder

###############################################################################
# Enumerations and constants
###############################################################################

class StopRule(ParsingEnum):
    """
    Controls stop criteria. Stops either when:
    - a given number of `GENERATIONS` is given;
    - or a `TARGET` value is found;
    - or no `IMPROVEMENT` is found in a given number of iterations.
    """
    GENERATIONS = 0
    TARGET = 1
    IMPROVEMENT = 2


###############################################################################

def main() -> None:
    """
    Proceeds with the optimization. Create to avoid spread `global` keywords
    around the code.
    """

    args = docopt.docopt(__doc__)
    # print(args)

    configuration_file = args["--config_file"]
    instance_file = args["--instance_file"]
    seed = int(args["--seed"])
    stop_rule = StopRule(args["--stop_rule"])

    if stop_rule == StopRule.TARGET:
        stop_argument = float(args["--stop_arg"])
    else:
        stop_argument = int(args["--stop_arg"])

    maximum_time = float(args["--max_time"])

    if maximum_time <= 0.0:
        raise RuntimeError(f"Maximum time must be larger than 0.0. "
                           f"Given {maximum_time}.")

    perform_evolution = not args["--no_evolution"]

    ########################################
    # Load config file and show basic info.
    ########################################

    brkga_params, control_params = load_configuration(configuration_file)

    ########################################
    # Load instance and adjust BRKGA parameters
    ########################################
    for i in range(100):
        seed = i
        instance = CrpInstance(instance_file)

        ########################################
        # Build the BRKGA data structures and initialize
        ########################################

        # Usually, it is a good idea to set the population size
        # proportional to the instance size.
        brkga_params.population_size = min(brkga_params.population_size,
                                        10 * instance.num_nodes)

        # Build a decoder object.
        decoder = CrpDecoder(instance)

        # Chromosome size is the number of nodes.
        brkga = BrkgaMpIpr(
            decoder=decoder,
            sense=Sense.MINIMIZE,
            seed=seed,
            chromosome_size=instance.num_nodes,
            params=brkga_params,
            evolutionary_mechanism_on=perform_evolution
        )

        brkga.initialize()

        ########################################
        # Warm up the script/code
        ########################################

        bogus_alg = deepcopy(brkga)
        bogus_alg.evolve(2)
        bogus_alg.get_best_fitness()
        bogus_alg.get_best_chromosome()
        bogus_alg = None

        ########################################
        # Evolving
        ########################################

        best_cost = -1

        iteration = 0
        last_update_time = 0.0
        last_update_iteration = 0
        large_offset = 0
        run = True

        start_time = time.time()
        while run:
            iteration += 1

            brkga.evolve()

            fitness = brkga.get_best_fitness()
            if best_cost == -1 or fitness < best_cost:
                update_offset = iteration - last_update_iteration

                if large_offset < update_offset:
                    large_offset = update_offset

                last_update_iteration = iteration
                best_cost = fitness

            iter_without_improvement = iteration - last_update_iteration

            run = not (
                (time.time() - start_time > maximum_time)
                or
                (stop_rule == StopRule.GENERATIONS and iteration == stop_argument)
                or
                (stop_rule == StopRule.IMPROVEMENT and
                iter_without_improvement >= stop_argument)
                or
                (stop_rule == StopRule.TARGET and best_cost <= stop_argument)
            )
        total_elapsed_time = time.time() - start_time
        print(f"{total_elapsed_time:.2f}")

###############################################################################

if __name__ == "__main__":
    main()
