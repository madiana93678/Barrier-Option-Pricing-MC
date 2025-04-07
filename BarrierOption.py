# -*- coding: utf-8 -*-
from math import *
from random import *
import matplotlib.pyplot as plt 
import numpy as np




class BarrierOption():

    def __init__(self,option_type,knock_in,up,S,K,B,T,r,sigma,N,M):
        """
        option_type (str): "call" or "put"
        knock_in (bool) : True if acitivation typeis knock_in False otherwise
        up (bool): True if option activates when S>B, False if it activates when S<B
        S (float): initial spot price
        K (float): strike price
        B (float): barrier price
        T (float): maturity in years
        r (float): risk-free rate
        sigma (float): volatility
        N (int): number of steps
        M (int): number of paths
        
        """
        self.option_type=option_type
        self.knock_in=knock_in
        self.up=up
        self.S=S
        self.K=K
        self.B=B
        self.T=T
        self.r=r
        self.sigma=sigma
        self.N=N
        self.M=M

    def simulate_paths(self,n_paths):
        dt = self.T / self.N
        path = np.zeros((n_paths, self.N + 1))
        path[:,0]=self.S
        Z = np.random.normal(0, 1, (n_paths, self.N))

        for k in range(1,self.N+1):
            path[:,k] = path[:,k-1] * np.exp((self.r - 0.5*self.sigma**2)*dt + self.sigma * sqrt(dt) * Z[:,k-1])

        return path 
    
    def pricing(self):
        
        payoff_mean = 0 

        path = self.simulate_paths(self.M)

        # Détection des barrières
        if self.up:
            barrier_hit = (path[:, 1:] >= self.B).any(axis=1)
        else:
            barrier_hit = (path[:, 1:] <= self.B).any(axis=1)

        # Sélection des trajectoires valides
        if self.knock_in:
            valid_paths = barrier_hit
        else:
            valid_paths = ~barrier_hit


        # Calcul des payoffs pour chaque type d'option
        if self.option_type == "call":
            payoffs_1 = np.maximum(path[valid_paths, -1] - self.K, 0)
        else:
            payoffs_1 = np.maximum(self.K - path[valid_paths, -1], 0)

        # On concatène tous les payoffs valides (des 2 chemins)
        payoff_mean = np.mean(payoffs_1)

        # Prix actualisé
        return exp(-self.r * self.T) * payoff_mean
    

    def plot_paths(self, n_paths=10):
        plt.figure(figsize=(10, 6))

        paths = self.simulate_paths(n_paths)

        # Détection des trajectoires qui touchent la barrière
        if self.up:
            hit_barrier = (paths[:, 1:] >= self.B).any(axis=1)
        else:
            hit_barrier = (paths[:, 1:] <= self.B).any(axis=1)

        # Tracé des trajectoires avec couleurs différentes
        for i in range(paths.shape[0]):
            color = "red" if hit_barrier[i] else "blue"
            label = "Touches barrier" if hit_barrier[i] else "Avoids barrier"
            plt.plot(paths[i], alpha=0.7, color=color)

        # Affichage de la barrière
        plt.axhline(self.B, color="black", linestyle="--", label=f"Barrier = {self.B}")
        plt.title(f"Simulated Paths - {self.option_type.upper()} {'Knock-In' if self.knock_in else 'Knock-Out'}")
        plt.xlabel("Time Steps")
        plt.ylabel("Price")
        plt.grid(True)
        plt.legend()
        plt.show()


                
    def summary(self):
        print(f"Option {self.option_type.upper()} - {'Knock-In' if self.knock_in else 'Knock-Out'}")
        print(f"Spot: {self.S}, Strike: {self.K}, Barrier: {self.B}")
        print(f"Up: {self.up}, Maturity: {self.T} years, Vol: {self.sigma}, r: {self.r}")


barrier = BarrierOption("call", True, True, 100, 100, 120, 2, 0.04, 0.2, 1000,10)
barrier.plot_paths(n_paths=15)
"""price = barrier.pricing()
barrier.summary()

print(price)"""
    