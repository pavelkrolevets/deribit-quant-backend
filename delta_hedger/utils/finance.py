from math import log, sqrt, exp
from scipy import stats
import math
from numpy import *
from time import time


class call_option(object):
    ''' Class for European call options in BSM model.

    Attributes
    ==========
    S0 : float
        initial stock/index level
    K : float
        strike price
    T : float
        maturity (in year fractions)
    r : float
        constant risk-free short rate
    sigma : float
        volatility factor in diffusion term

    Methods
    =======
    value : float
        return present value of call option
    vega : float
        return Vega of call option
    imp_vol: float
        return implied volatility given option quote
    '''

    def __init__(self, S0, K, T, r, sigma):
        self.S0 = float(S0)
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma

    def value(self):
        ''' Returns option value. '''
        d1 = ((log(self.S0 / self.K)
               + (self.r + 0.5 * self.sigma ** 2) * self.T)
              / (self.sigma * sqrt(self.T)))
        d2 = ((log(self.S0 / self.K)
               + (self.r - 0.5 * self.sigma ** 2) * self.T)
              / (self.sigma * sqrt(self.T)))
        value = (self.S0 * stats.norm.cdf(d1, 0.0, 1.0)
                 - self.K * exp(-self.r * self.T) * stats.norm.cdf(d2, 0.0, 1.0))
        return value

    def vega(self):
        ''' Returns Vega of option. '''
        d1 = ((log(self.S0 / self.K)
               + (self.r + 0.5 * self.sigma ** 2) * self.T)
              / (self.sigma * sqrt(self.T)))
        vega = self.S0 * stats.norm.pdf(d1, 0.0, 1.0) * sqrt(self.T)
        return vega
    def delta(self):
        ''' Returns Delta of option. '''


    def imp_vol(self, C0, sigma_est=0.2, it=1000):
        ''' Returns implied volatility given option price. '''
        option = call_option(self.S0, self.K, self.T, self.r, sigma_est)
        for i in range(it):
            option.sigma -= (option.value() - C0) / option.vega()
        return option.sigma

    def mc_value(self):
        random.seed(20000)
        t0 = time()

        # Parameters
        M = 50
        dt = self.T / M
        I = 250000 * 2

        # Simulating I paths with M time steps
        ran = random.standard_normal((M + 1, I))
        ran -= ran.mean()  # corrects 1st moment
        ran /= ran.std()  # corrects 2nd moment
        S = zeros_like(ran)
        S[0] = self.S0
        S[1:] = self.S0 * exp(cumsum((self.r - 0.5 * self.sigma ** 2) * dt
                                + self.sigma * math.sqrt(dt) * ran[1:], axis=0))
        # sum instead of cumsum would also do
        # if only the final values are of interest

        # Calculating the Monte Carlo estimator
        C0 = math.exp(-self.r * self.T) * sum(maximum(S[-1] - self.K, 0)) / I

        # Results output
        tnp2 = time() - t0
        print("Duration in Seconds   %7.3f" % tnp2)
        return C0

class put_option(object):
    ''' Class for European call options in BSM model.

    Attributes
    ==========
    S0 : float
        initial stock/index level
    K : float
        strike price
    T : float
        maturity (in year fractions)
    r : float
        constant risk-free short rate
    sigma : float
        volatility factor in diffusion term

    Methods
    =======
    value : float
        return present value of call option
    vega : float
        return Vega of call option
    imp_vol: float
        return implied volatility given option quote
    '''

    def __init__(self, S0, K, T, r, sigma):
        self.S0 = float(S0)
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma

    def value(self):
        ''' Returns option value. '''
        d1 = ((log(self.S0 / self.K)
               + (self.r + 0.5 * self.sigma ** 2) * self.T)
              / (self.sigma * sqrt(self.T)))
        d2 = ((log(self.S0 / self.K)
               + (self.r - 0.5 * self.sigma ** 2) * self.T)
              / (self.sigma * sqrt(self.T)))
        value = (-self.S0 * stats.norm.cdf(-d1, 0.0, 1.0)
                 + self.K * exp(-self.r * self.T) * stats.norm.cdf(-d2, 0.0, 1.0))
        return value

    def vega(self):
        ''' Returns Vega of option. '''
        d1 = ((log(self.S0 / self.K)
               + (self.r + 0.5 * self.sigma ** 2) * self.T)
              / (self.sigma * sqrt(self.T)))
        vega = self.S0 * stats.norm.pdf(d1, 0.0, 1.0) * sqrt(self.T)
        return vega

    def imp_vol(self, C0, sigma_est=0.2, it=100):
        ''' Returns implied volatility given option price. '''
        option = call_option(self.S0, self.K, self.T, self.r, sigma_est)
        for i in range(it):
            option.sigma -= (option.value() - C0) / option.vega()
        return option.sigma

    def mc_value(self):
        random.seed(20000)
        t0 = time()

        # Parameters
        M = 50
        dt = self.T / M
        I = 250000 * 2

        # Simulating I paths with M time steps
        ran = random.standard_normal((M + 1, I))
        ran -= ran.mean()  # corrects 1st moment
        ran /= ran.std()  # corrects 2nd moment
        S = zeros_like(ran)
        S[0] = self.S0
        S[1:] = self.S0 * exp(cumsum((self.r - 0.5 * self.sigma ** 2) * dt
                                + self.sigma * math.sqrt(dt) * ran[1:], axis=0))
        # sum instead of cumsum would also do
        # if only the final values are of interest

        # Calculating the Monte Carlo estimator
        C0 = math.exp(-self.r * self.T) * sum(maximum(self.K - S[-1], 0)) / I

        # Results output
        tnp2 = time() - t0
        print("Duration in Seconds   %7.3f" % tnp2)
        return C0