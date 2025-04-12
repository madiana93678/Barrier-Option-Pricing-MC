# Barrier-Option-Pricing-MC
# Barrier Option Pricing & Hedging - Monte Carlo Simulation

This project demonstrates the **pricing and hedging of barrier options** using Monte Carlo simulations, along with a detailed comparison to a **traditional delta hedging** strategy. The main objective of this project is to model, price, and hedge barrier options with different strategies to assess their performance. The project is implemented in Python and uses **object-oriented programming (OOP)** to structure the code.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Metrics for Comparison](#metrics-for-comparison)
6. [Results](#results)
7. [Project Structure](#project-structure)
8. [Technologies Used](#technologies-used)
9. [Future Improvements](#future-improvements)
10. [Hedging Strategies](#hedging-strategies)

## Project Overview
This project focuses on the **Monte Carlo simulation** technique for the pricing and hedging of **barrier options**. It includes:
- A class-based design using **object-oriented programming** for modularity and reusability.
- Two strategies for hedging the option: **normal delta hedging** and **Monte Carlo-based delta hedging**.
- Performance comparison of both strategies based on important **hedging metrics** such as mean error, standard deviation, skewness, and kurtosis.
- Visualizations of simulated price paths and the error distribution of both hedging strategies.

The project is aimed at individuals with a background in **finance**, **quantitative finance**, and **computer science**, especially those looking for a way to showcase their ability to combine **finance theory** with **programming skills**.

## Features
- **Barrier Option Pricing**: Implemented using Monte Carlo simulations to simulate multiple price paths and compute the expected payoff.
- **Delta Hedging**: Two strategies:
  - **Normal delta hedging** (with rebalancing at every time step).
  - **Monte Carlo-based delta hedging** (dynamic rebalancing using simulations).
- **Error Metrics**: Calculation of key metrics such as mean error, standard deviation, skewness, and kurtosis to compare the performance of both hedging strategies.
- **Visualizations**: Side-by-side histograms to compare the **hedging error distribution** of both strategies, as well as the **simulated price paths** of the underlying asset.

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/your-username/barrier-option-hedging.git
