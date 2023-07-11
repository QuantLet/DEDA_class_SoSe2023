import numpy as np
import cvxpy as cp
import collections
from pypfopt import exceptions
from pypfopt.discrete_allocation import DiscreteAllocation

class CustomDiscreteAllocation(DiscreteAllocation):
    def __init__(self, *args, min_value_constraints=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Add any additional initialization code specific to your custom class
        self.min_value_constraints = min_value_constraints


    def lp_portfolio(self, reinvest=False, verbose=False, solver="GUROBI"):
        # Implement your custom logic here
        # Override the lp_portfolio method with your custom implementation
        # Add your desired logic here
        # Make sure to return the allocation and leftover variables as needed

        p = self.latest_prices.values
        n = len(p)
        w = np.fromiter([i[1] for i in self.weights], dtype=float)

        # Integer allocation
        # x will hold discrete allocation for all stocks
        x = cp.Variable(n, integer=True)
        # Remaining dollars
        r = self.total_portfolio_value - p.T @ x

        # Set up linear program
        eta = w * self.total_portfolio_value - cp.multiply(x, p)
        u = cp.Variable(n)
        constraints = [eta <= u, eta >= -u, x >= 0, r >= 0]

        # Add additional constraints to ensure certain elements of x are greater than their minimum values
        if self.min_value_constraints is not None:
            for position_ticker, min_value in self.min_value_constraints.items():
                constraints.append(x[position_ticker] >= min_value)

        objective = cp.sum(u) + r

        opt = cp.Problem(cp.Minimize(objective), constraints)

        if solver is not None and solver not in cp.installed_solvers():
            raise NameError("Solver {} is not installed. ".format(solver))
        opt.solve(solver=solver)

        if opt.status not in {"optimal", "optimal_inaccurate"}:  # pragma: no cover
            raise exceptions.OptimizationError("Please try greedy_portfolio")

        vals = np.rint(x.value).astype(int)
        self.allocation = self._remove_zero_positions(
            collections.OrderedDict(zip([i[0] for i in self.weights], vals))
        )

        if verbose:
            print("Funds remaining: {:.2f}".format(r.value))
            self._allocation_rmse_error()
        return self.allocation, r.value