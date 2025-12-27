import sys
import os
import matplotlib.pyplot as plt
import numpy as np

# Adjust path to import Deck from src/main.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

try:
    from main import Deck, penalties_A, penalties_B, penalties_C, penalties_D, Config
except ImportError:
    # Fallback if run from root
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from src.main import Deck, penalties_A, penalties_B, penalties_C, penalties_D, Config

def run_monte_carlo(n_trials=10000):
    print(f"🔄 Running Monte Carlo Simulation (n={n_trials})...")
    decks = {
        'A': Deck('A', Config.REWARD_BAD_DECK, penalties_A),
        'B': Deck('B', Config.REWARD_BAD_DECK, penalties_B),
        'C': Deck('C', Config.REWARD_GOOD_DECK, penalties_C),
        'D': Deck('D', Config.REWARD_GOOD_DECK, penalties_D)
    }
    results = {'A': [], 'B': [], 'C': [], 'D': []}
    
    for _ in range(n_trials):
        for name, deck in decks.items():
            _, _, net = deck.draw_card()
            results[name].append(net)
            
    print("\n📊 Simulation Results (Expected Value per Card):")
    labels, means = [], []
    for name in ['A', 'B', 'C', 'D']:
        avg = np.mean(results[name])
        means.append(avg)
        labels.append(name)
        status = "BAD" if avg < 0 else "GOOD"
        print(f"Deck {name}: {avg:+.2f} TL ({status})")

    plt.figure(figsize=(10, 6))
    colors = ['#e74c3c', '#e67e22', '#2ecc71', '#3498db']
    plt.bar(labels, means, color=colors, edgecolor='black', alpha=0.8)
    plt.axhline(0, color='black', linewidth=1)
    plt.title(f"Monte Carlo Validation (n={n_trials})")
    plt.ylabel("Average Net Outcome (TL)")
    plt.savefig('validation_results.png')
    print("✅ Plot saved to validation_results.png")

if __name__ == "__main__":
    run_monte_carlo()