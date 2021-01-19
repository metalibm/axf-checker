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
# last-modified:    Jan 17th, 2021
###############################################################################

import argparse
import sys

import metalibm_core.utility.axf_utils as axf_utils

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str, help="input file")
    args = parser.parse_args()

    axf_import = axf_utils.AXF_JSON_Importer.from_file(args.filename)

    # axf_import should contain a list of top-level approximations
    for top_level_approx in axf_import:
        ml_object = top_level_approx.to_ml_object()
        top_approx_error = ml_object.approx_error
        for sub_approx in ml_object.approx_list:
            # checking that all listed errors are below top-level error
            if not top_approx_error >= sub_approx.approx_error:
                print("[ERROR] approx-error for sub approximation {} exceeds top-level target {}".format(sub_approx.approx_error, top_approx_error))
                sys.exit(1)

