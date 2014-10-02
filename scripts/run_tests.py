# Copyright (c) 2014 Phil Mansfield
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import print_function

import math
import os
import subprocess
import sys
import time


ESTIMATE_FRACTION = 0.1
MAX_ESTIMATE_ITERS = 30

MIN_INT_WIDTH = 15
MIN_FLOAT_WIDTH = 15

def hasTail(fileName, tail):
    return tail == fileName[len(fileName) - len(tail):]

def isTest(fileName):
    return hasTail(fileName, "_test")

def isBenchmark(fileName):
    return hasTail(fileName, "_bench")

def getAllTests(testDir):
    return [f for f in os.listdir(testDir) if
            os.path.isfile(os.path.join(testDir, f)) and 
            isTest(f)]

def getAllBenchmarks(benchDir):
    return [f for f in os.listdir(benchDir) if
            os.path.isfile(os.path.join(benchDir, f)) and 
            isBenchmark(f)]

def runAllTests(testDir):
    tests = getAllTests(testDir)
    failSum = 0
    if len(tests) == 0: return

    col0Name = "Test Name"
    col1Name = "Passed"
    col2Name = "Failed"
    col0Width = max(max(map(len, tests)), len(col0Name))
    col1Width = len(col1Name)
    col2Width = len(col2Name)

    print("%*s %*s %*s" % (col0Width, col0Name,
                           col1Width, col1Name,
                           col2Width, col2Name))

    for test in tests:
        print("%*s" % (col0Width, test), end=" ")
        if subprocess.call(["%s" % os.path.join(testDir, test)]) == 0:
            print("%*s %*s" % (col1Width, "X", col2Width, ""))
        else:
            failSum += 1
            print("%*s %*s" % (col1Width, "", col2Width, "X"))
    if failSum == 0:
        print("All tests passed!")
    else:
        print("Failed %d/%d tests." % (failSum, len(tests)))

def powerOfTenRound(x):
    lowPow = int(10**(math.ceil(math.log10(x)) - 1))
    return int(x / lowPow) * lowPow

def estimateOpCount(bench, benchmarkTime):
    ops = 1
    eta = 0.
    iters = 0
    
    while eta < benchmarkTime * ESTIMATE_FRACTION:
        iters += 1
        ops *= 2

        t0 = time.time()
        subprocess.call(["./%s" % bench, str(ops)])
        t1 = time.time()
        eta = t1 - t0

        if iters == MAX_ESTIMATE_ITERS: break

    return max(1, powerOfTenRound(ops * benchmarkTime / eta))
        

def runAllBenchmarks(benchDir, benchmarkTime=1.0):
    benches = getAllBenchmarks(benchDir)
    if len(benches) == 0: return

    col0Name = "Test Name"
    col1Name = "Ops"
    col2Name = "Secs"
    col3Name = "Secs per op"
    col0Width = max(max(map(len, benches)), len(col0Name))
    col1Width = max(len(col1Name), MIN_FLOAT_WIDTH)
    col2Width = max(len(col2Name), MIN_FLOAT_WIDTH)
    col3Width = max(len(col3Name), MIN_FLOAT_WIDTH)

    print("%*s %*s %*s %*s" % (col0Width, col0Name,
                               col1Width, col1Name,
                               col2Width, col2Name,
                               col3Width, col3Name))

    t00 = time.time()
    for bench in benches:
        print("%*s" % (col0Width, bench), end=" ")
        ops = estimateOpCount(bench, benchmarkTime)

        t0 = time.time()
        subprocess.call(["%s" % os.path.join(benchDir, bench), str(ops)])
        t1 = time.time()

        print("%*g %*g %*g" % (col1Width, ops, col2Width, t1 - t0,
                               col3Width, (t1 - t0) / ops))

    t01 = time.time()
    print("Total benchmark time: %f s" % (t01 - t00))
        

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: '$ python runTests.py <input-dir> " + 
              "[test|bench] [benchmark-time]'.\nbenchmark-time is required" +
              "if mode is set to bench.")
        sys.exit(1)

    inDir = sys.argv[1]
    testType = "test" if len(sys.argv) == 2 else sys.argv[2]

    if testType == "test":
        print("Running all tests...")
        runAllTests(inDir)
    elif testType == "bench":
        print("Running all benchmarks...")
        if len(sys.argv) == 3:
            runAllBenchmarks(inDir)
        else:
            benchmarkTime = float(sys.argv[3])
            runAllBenchmarks(inDir, benchmarkTime)
