#!/usr/bin/env python3
"""
Monte Carlo Simulation for USD (English) Configuration
Validates the Bechara et al. (1994) protocol values
"""
import matplotlib.pyplot as plt
import numpy as np
import random

# USD Configuration (Bechara et al. 1994 original protocol)
USD_CONFIG = {
    "start_balance": 2000,
    "reward_bad": 100,  # Decks A, B
    "reward_good": 50,  # Decks C, D
    "penalty_a": [0, -150, 0, -200, 0, -250, 0, -300, 0, -350],
    "penalty_b": [0, 0, 0, 0, 0, 0, 0, 0, 0, -1250],
    "penalty_c": [0, -25, 0, -25, 0, -50, 0, -50, 0, -100],
    "penalty_d": [0, 0, 0, 0, 0, 0, 0, 0, 0, -250],
}

def create_schedule(base_list):
    """Create shuffled penalty schedule"""
    final_schedule = []
    full_list = base_list * 10  # 100 trials
    for i in range(0, len(full_list), 10):
        block = full_list[i:i+10]
        random.shuffle(block)
        final_schedule.extend(block)
    return final_schedule

class DeckUSD:
    def __init__(self, name, reward, penalties):
        self.name = name
        self.reward = reward
        self.schedule = create_schedule(penalties)
        self.draw_count = 0
    
    def draw_card(self):
        penalty = self.schedule[self.draw_count % len(self.schedule)]
        self.draw_count += 1
        net = self.reward + penalty
        return self.reward, penalty, net

def run_monte_carlo_usd(n_trials=10000):
    print(f"🔄 Running Monte Carlo Simulation for USD (n={n_trials})...")
    print(f"   Start Balance: ${USD_CONFIG['start_balance']}")
    print(f"   Bad Deck Reward: ${USD_CONFIG['reward_bad']}")
    print(f"   Good Deck Reward: ${USD_CONFIG['reward_good']}")
    print()
    
    decks = {
        'A': DeckUSD('A', USD_CONFIG['reward_bad'], USD_CONFIG['penalty_a']),
        'B': DeckUSD('B', USD_CONFIG['reward_bad'], USD_CONFIG['penalty_b']),
        'C': DeckUSD('C', USD_CONFIG['reward_good'], USD_CONFIG['penalty_c']),
        'D': DeckUSD('D', USD_CONFIG['reward_good'], USD_CONFIG['penalty_d'])
    }
    results = {'A': [], 'B': [], 'C': [], 'D': []}
    
    for _ in range(n_trials):
        for name, deck in decks.items():
            _, _, net = deck.draw_card()
            results[name].append(net)
    
    print("📊 Simulation Results (Expected Value per Card):")
    print("-" * 50)
    
    labels, means = [], []
    for name in ['A', 'B', 'C', 'D']:
        avg = np.mean(results[name])
        means.append(avg)
        labels.append(name)
        status = "DISADVANTAGEOUS ❌" if avg < 0 else "ADVANTAGEOUS ✅"
        print(f"  Deck {name}: ${avg:+.2f} per card ({status})")
    
    # Calculate expected values per 10 cards (like original study)
    print()
    print("📈 Expected Value per 10 Cards (100 trial simulation):")
    print("-" * 50)
    for name in ['A', 'B', 'C', 'D']:
        ev_10 = np.mean(results[name]) * 10
        deck_type = "Bad" if name in ['A', 'B'] else "Good"
        print(f"  Deck {name} ({deck_type}): ${ev_10:+.2f}")
    
    # Plot
    plt.figure(figsize=(10, 6))
    colors = ['#e74c3c', '#e67e22', '#2ecc71', '#3498db']
    bars = plt.bar(labels, means, color=colors, edgecolor='black', alpha=0.8)
    plt.axhline(0, color='black', linewidth=1)
    plt.title(f"Monte Carlo Validation - USD Configuration (n={n_trials})")
    plt.ylabel("Average Net Outcome ($)")
    plt.xlabel("Deck")
    
    # Add value labels on bars
    for bar, mean in zip(bars, means):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'${mean:+.2f}',
                ha='center', va='bottom' if height > 0 else 'top',
                fontweight='bold')
    
    output_path = 'validation_results_usd.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n✅ Plot saved to {output_path}")
    
    return means

if __name__ == "__main__":
    run_monte_carlo_usd()
