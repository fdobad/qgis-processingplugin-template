"""Tests Python Download-and-go setup.

usage: python test.py [API_KEY] [CPXCHECKLIC_BINDIR]

The API_KEY and CPXCHECKLIC_BINDIR arguments are optional.
"""
import os
import sys

import cplex

# Column limit for the Community Edition.
CPLEX_COLUMN_LIMIT = 1000

# Print the CPLEX version.
print("Version:", cplex.__version__)

# Allow the user to pass in the API key.
if len(sys.argv) > 1:
    os.environ["CPLEX_STUDIO_KEY"] = sys.argv[1]

# Allow the user to pass in the cpxchecklic bindir.
if len(sys.argv) > 2:
    os.environ["CPLEX_CPXCHECKLIC_BINDIR"] = sys.argv[2]

# Print the environment variables.
for var in ("CPLEX_STUDIO_KEY",
            "CPLEX_STUDIO_DIR1210",
            "CPLEX_CPXCHECKLIC_BINDIR"):
    print(var, "=", os.getenv(var))

# Create a model that will not work with the Community Edition.
cpx = cplex.Cplex()
cpx.variables.add(lb=[0.0] * (CPLEX_COLUMN_LIMIT + 1))

# Solve the model and print the solution status.
cpx.solve()
print("Status: {0} ({1})".format(cpx.solution.get_status_string(),
                                 cpx.solution.get_status()))
