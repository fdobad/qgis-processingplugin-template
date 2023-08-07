#!python3
"""
%autoindent

Easiest installing cplex studio:
    ./cplex_studio2211.linux_x86_64.bin
During installation, don't run python setup.py when promted, but then instead:

    pip install cplex [docplex]
No need to import cplex, but must be installed to have the bindings!
"""
import numpy as np
from pyomo import environ as pyo
from pyomo.opt import SolverStatus, TerminationCondition

N = np.random.randint(1, 250000)
values = np.random.rand(N)
weights = np.random.rand(N)
fraction = np.random.rand()
capacity = weights.sum() * fraction

m = pyo.ConcreteModel()
m.N = pyo.RangeSet(0, N - 1)
m.Va = pyo.Param(m.N, within=pyo.Reals, initialize=values)
m.We = pyo.Param(m.N, within=pyo.Reals, initialize=weights)
m.Cap = pyo.Param(initialize=capacity)
m.X = pyo.Var(m.N, within=pyo.Binary)

obj_expr = pyo.sum_product(m.X, m.Va, index=m.N)
m.obj = pyo.Objective(expr=obj_expr, sense=pyo.maximize)

m.capacity = pyo.Constraint(rule=lambda m: pyo.sum_product(m.X, m.We, index=m.N) <= m.Cap)

opt = pyo.SolverFactory("cplex_direct")
results = opt.solve(m, tee=True, options_string="mipgap=0.01 timelimit=300")

status = results.solver.status
termCondition = results.solver.termination_condition

if status in [SolverStatus.error, SolverStatus.aborted, SolverStatus.unknown]:
    print(f"Solver status: {status}, termination condition: {termCondition}")
if termCondition in [
    TerminationCondition.infeasibleOrUnbounded,
    TerminationCondition.infeasible,
    TerminationCondition.unbounded,
]:
    print(f"Optimization problem is {termCondition}. No output is generated.")
if not termCondition == TerminationCondition.optimal:
    print("Output is generated for a non-optimal solution.")

response = np.array([pyo.value(m.X[i], exception=False) for i in m.X])
response[response == None] = 2
response = response.astype(np.int16)
print(f"N:{N}, fraction:{fraction:4.2%}\nresponse histogram:{np.histogram(response,bins=[0,0.5,1.5,2])}")
