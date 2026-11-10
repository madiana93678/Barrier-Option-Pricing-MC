from BarrierOption import bs_delta
from DeltaHedger import DeltaHedger


class VanillaDeltaHedger(DeltaHedger):
    """
    Naive benchmark: hedges the barrier option with the Black-Scholes delta of the
    corresponding vanilla option, ignoring the barrier until it is actually touched.

    This is what a trader would do without a barrier model. Comparing it with the
    barrier-aware hedgers shows how much the barrier matters for the hedge.
    """

    name = "Naive vanilla delta"

    def barrier_delta(self, S, tau, t):
        opt = self.option
        return bs_delta(opt.option_type, S, opt.K, tau, opt.r, opt.sigma)
