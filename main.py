import numpy as np
from BarrierOption import BarrierOption
from VanillaDeltaHedger import VanillaDeltaHedger
from BarrierDeltaHedging import BarrierDeltaHedger

# Paramètres de l'option barrière
option = BarrierOption(
    option_type="call",       # ou "put"
    knock_in=True,            # knock-in ou knock-out
    up=True,                  # up = barrière au-dessus
    S=100,                    # spot
    K=100,                    # strike
    B=120,                    # barrière
    T=1,                      # maturité (1 an)
    r=0.05,                   # taux sans risque
    sigma=0.2,                # volatilité
    N=252,                    # pas de temps (daily)
    M=1000                   # nombre de trajectoires simulées
)

# Création du hedger barrière
hedger = BarrierDeltaHedger(option)

# Lancement du hedging
errors = hedger.run_barrier_hedging()

# Résultats
print(f"\nRésultats pour {option.option_type.upper()} {'Knock-In' if option.knock_in else 'Knock-Out'}")
print(f"Nombre de trajectoires : {len(errors)}")
print(f"Moyenne de l'erreur : {np.mean(errors):.4f}")
print(f"Écart-type : {np.std(errors):.4f}")

# Affichage histogramme
hedger.plot_hedging_errors(errors)
