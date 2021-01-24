# -*- coding: utf-8 -*-

###############################################################################
# MIT License
#
# Copyright (c) 2021 - Nicolas Brunie
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###############################################################################
# created:          Jan 17th, 2021
# last-modified:    Jan 24th, 2021
###############################################################################

import argparse
import sys
import sollya
from sollya import sup

import matplotlib.pyplot as plt
import numpy as np

import metalibm_core.utility.axf_utils as axf_utils

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str, help="input file")
    parser.add_argument("--error-hist", action="store_const", const=True,
                        default=False,
                        help="display error distribution histogram")
    parser.add_argument("--exit-on-error", action="store_const", const=True,
                        default=False,
                        help="exit at first encountered error")
    parser.add_argument("--check-level", action="store", default="light",
                        choices=["light", "strong"],
                        help="select checking strength (light: check against registered bound, strong: compute bounds and check")
    args = parser.parse_args()

    axf_import = axf_utils.AXF_JSON_Importer.from_file(args.filename)

    # global error_count
    error_count = 0

    # axf_import should contain a list of top-level approximations
    for top_level_approx in axf_import:
        top_approx_error = top_level_approx.approx_error

        # displaying error histogram
        if args.error_hist:
            np_errors = np.array([float(sub_approx.approx_error.value) for sub_approx in top_level_approx.approx_list])

            # logarithmic bining from https://stackoverflow.com/questions/47850202/plotting-a-histogram-on-a-log-scale-with-matplotlib?rq=1
            # # histogram on log scale.
            # Use non-equal bin sizes, such that they look equal on log scale.
            min_error = min(np_errors)
            max_error = max(np_errors)
            print("min error: {}".format(min_error))
            print("max error: {}".format(max_error))
            NUM_BINS = 200
            logbins = np.logspace(np.log10(min_error),np.log10(max_error), NUM_BINS)
            fig, ax = plt.subplots(tight_layout=True)
            plt.hist(np_errors, bins=logbins)
            plt.xscale('log')
            plt.show()

        # checking error correctness
        for sub_id, sub_approx in enumerate(top_level_approx.approx_list):
            # checking that all listed errors are below top-level error
            if not top_approx_error >= sub_approx.approx_error:
                print("[ERROR] approx-error for sub approximation (#{}) {} exceeds top-level target {}".format(sub_id, sub_approx.approx_error.value, top_approx_error.value))
                error_count += 1
                if args.exit_on_error:
                    sys.exit(1)

            if args.check_level in ["strong"]:
                sub_function = sub_approx.function
                sub_approx_poly = sub_approx.poly.get_sollya_object()
                # TODO/FIXME errorType should be derived from approx
                #            error target type
                # TODO/FIXME: manage accuracy properly
                error_type = sub_approx.approx_error.sollya_error_type
                eval_approx_error = sup(abs(sollya.supnorm(sub_approx_poly,
                                                           sub_function,
                                                           sub_approx.interval,
                                                           error_type,
                                                           2**-24)))
                eval_approx_error_inf = sup(abs(sollya.infnorm(sub_approx_poly - sub_function,
                                                               sub_approx.interval)))
                if sub_approx.approx_error.value > eval_approx_error and sub_approx.approx_error.value > eval_approx_error_inf:
                    print("[ERROR] approx-error for sub approximation (#{}) infnorm={}, supnorm={} exceeds registered value {}".format(sub_id, eval_approx_error, eval_approx_error_inf, sub_approx.approx_error.value,))
                    error_count += 1
                    if args.exit_on_error:
                        sys.exit(1)

    if error_count:
        sys.exit(1)
