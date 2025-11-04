import requests
import json
import time
import matplotlib.pyplot as plt
from datetime import datetime
from collections import deque

# ==================== CONFIGURATION ====================
API_TOKEN = "a4693c12a3de0cd5ceb3f6cb742f45747c9cbd88"
BASE_URL = "https://challenge.sphinxhq.com"

# Debug settings
PROGRESS_PRINT_FREQUENCY = 10  # Print stats every N steps (10 = more detail, 50 = less spam)
VERBOSE_MODE = True            # Show individual trip results

# Algorithm parameters
WINDOW_SIZE = 30               # Number of recent trips to track per planet
EXPLORATION_RATE = 0.15        # 15% exploration, 85% exploitation
INITIAL_EXPLORATION = 10       # Initial trips per planet before adapting
# ========================================================

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def start_episode():
    """Start a new episode"""
    response = requests.post(f"{BASE_URL}/api/mortys/start/", headers=headers)
    print(f"Response status: {response.status_code}")
    print(f"Response text: {response.text}")
    if response.status_code != 200:
        print(f"Error starting episode: {response.status_code}")
        return None
    data = response.json()
    print(f"Episode started: {data}")
    return data

def send_morties(planet_index, morty_count=3):
    """Send morties through a portal"""
    payload = {
        "planet": planet_index,
        "morty_count": morty_count
    }
    response = requests.post(f"{BASE_URL}/api/mortys/portal/", headers=headers, json=payload)
    return response.json()

def get_status():
    """Get current episode status"""
    response = requests.get(f"{BASE_URL}/api/mortys/status/", headers=headers)
    return response.json()

class AdaptivePlanetRouter:
    """
    Adaptive routing strategy using a multi-armed bandit approach.
    Tracks recent success rates for each planet and routes Morties accordingly.
    """

    def __init__(self, window_size=30, exploration_rate=0.15):
        """
        Args:
            window_size: Number of recent trips to consider for each planet
            exploration_rate: Fraction of trips to use for exploration vs exploitation
        """
        self.window_size = window_size
        self.exploration_rate = exploration_rate
        self.planet_names = [
            "Planet A (On a Cob)",
            "Planet B (Cronenberg)",
            "Planet C (Purge Planet)"
        ]

        # Track recent results for each planet using a sliding window
        self.planet_windows = {
            0: deque(maxlen=window_size),
            1: deque(maxlen=window_size),
            2: deque(maxlen=window_size)
        }

        # Track total attempts per planet
        self.planet_attempts = {0: 0, 1: 0, 2: 0}

        # Track all results for analysis
        self.all_results = []

        # Initial exploration: send a few trips to each planet
        self.initial_exploration_per_planet = 10
        self.initial_exploration_done = False

    def get_success_rate(self, planet_index):
        """Get recent success rate for a planet"""
        window = self.planet_windows[planet_index]
        if len(window) == 0:
            return 0.5  # Default to 50% if no data
        return sum(window) / len(window)

    def get_best_planet(self):
        """Get the planet with the best recent success rate"""
        success_rates = {i: self.get_success_rate(i) for i in range(3)}
        best_planet = max(success_rates, key=success_rates.get)
        return best_planet, success_rates

    def choose_planet(self, step):
        """
        Choose which planet to send Morties through.
        Uses epsilon-greedy strategy with initial exploration phase.
        """
        import random

        # Initial exploration: ensure each planet gets some early data
        if not self.initial_exploration_done:
            for planet in range(3):
                if self.planet_attempts[planet] < self.initial_exploration_per_planet:
                    return planet
            self.initial_exploration_done = True
            print("\n🔍 Initial exploration complete! Switching to adaptive mode...\n")

        # Epsilon-greedy: explore with probability exploration_rate
        if random.random() < self.exploration_rate:
            # Exploration: choose randomly, but prefer less-explored planets
            min_attempts = min(self.planet_attempts.values())
            candidates = [p for p in range(3) if self.planet_attempts[p] <= min_attempts + 10]
            return random.choice(candidates)
        else:
            # Exploitation: choose best performing planet
            best_planet, _ = self.get_best_planet()
            return best_planet

    def record_result(self, planet_index, survived):
        """Record the result of a trip"""
        self.planet_windows[planet_index].append(1 if survived else 0)
        self.planet_attempts[planet_index] += 1

    def get_stats(self):
        """Get current statistics for all planets"""
        stats = {}
        for i in range(3):
            success_rate = self.get_success_rate(i)
            window_size = len(self.planet_windows[i])
            stats[i] = {
                'name': self.planet_names[i],
                'success_rate': success_rate,
                'attempts': self.planet_attempts[i],
                'window_size': window_size
            }
        return stats

def run_adaptive_episode():
    """Run an episode using adaptive planet selection"""
    print(f"\n{'='*70}")
    print(f"🚀 Starting ADAPTIVE episode - Multi-Armed Bandit Strategy")
    print(f"{'='*70}")
    print(f"⚙️  Config: Window={WINDOW_SIZE}, Exploration={EXPLORATION_RATE*100:.0f}%, Initial={INITIAL_EXPLORATION}")
    print(f"📊 Debug: Progress every {PROGRESS_PRINT_FREQUENCY} steps, Verbose={VERBOSE_MODE}")
    print(f"{'='*70}\n")

    # Initialize router with config parameters
    router = AdaptivePlanetRouter(window_size=WINDOW_SIZE, exploration_rate=EXPLORATION_RATE)
    router.initial_exploration_per_planet = INITIAL_EXPLORATION

    # Start new episode
    start_episode()
    time.sleep(0.5)

    step = 0

    while True:
        status = get_status()

        if status['morties_in_citadel'] == 0:
            print(f"\n{'='*70}")
            print(f"✅ Episode complete!")
            print(f"{'='*70}")
            print(f"Final score: {status['morties_on_planet_jessica']}/1000 ({status['morties_on_planet_jessica']/10:.1f}%)")
            print(f"Morties lost: {status['morties_lost']}")
            print(f"Total steps: {status['steps_taken']}")
            print(f"{'='*70}\n")
            break

        # Choose planet adaptively
        planet_index = router.choose_planet(step)

        # Send morties (3 or whatever is left)
        morties_to_send = min(3, status['morties_in_citadel'])
        result = send_morties(planet_index, morties_to_send)

        # Record result
        router.record_result(planet_index, result['survived'])

        # Store all results for analysis
        router.all_results.append({
            'step': step,
            'planet': planet_index,
            'morties_sent': result['morties_sent'],
            'survived': result['survived'],
            'morties_in_citadel': result['morties_in_citadel'],
            'morties_on_jessica': result['morties_on_planet_jessica'],
            'morties_lost': result['morties_lost'],
            'cumulative_success_rate': result['morties_on_planet_jessica'] / (1000 - result['morties_in_citadel']) if (1000 - result['morties_in_citadel']) > 0 else 0
        })

        step += 1

        # Verbose mode: print each trip
        if VERBOSE_MODE and step <= 30:
            print(f"  Trip {step}: Planet {planet_index} [{router.planet_names[planet_index]}] - {'✅ SUCCESS' if result['survived'] else '❌ FAILED'} (Saved: {result['morties_on_planet_jessica']}/{1000 - result['morties_in_citadel']})")

        # Print progress every N steps (configurable)
        if step % PROGRESS_PRINT_FREQUENCY == 0:
            stats = router.get_stats()
            best_planet, success_rates = router.get_best_planet()

            print(f"\n📊 Step {step} Progress:")
            print(f"   Saved: {result['morties_on_planet_jessica']}, Lost: {result['morties_lost']}, Remaining: {result['morties_in_citadel']}")
            print(f"   Current success rate: {result['morties_on_planet_jessica'] / (1000 - result['morties_in_citadel']) * 100:.1f}%")
            print(f"   Last trip: Planet {planet_index} - {'✅ SUCCESS' if result['survived'] else '❌ FAILED'}")
            print(f"\n   Recent Planet Performance (last {router.window_size} trips):")
            for i in range(3):
                s = stats[i]
                indicator = " ⭐ BEST" if i == best_planet else ""
                print(f"     Planet {i}: {s['success_rate']*100:.1f}% success ({s['attempts']} total trips){indicator}")
            print()

        time.sleep(0.1)  # Small delay to avoid rate limiting

    return router

def analyze_and_plot_adaptive(router):
    """Analyze results and create visualizations for adaptive strategy"""
    results = router.all_results

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Morty Express - Adaptive Multi-Armed Bandit Strategy', fontsize=16, fontweight='bold')

    colors = ['#FF6B6B', '#4ECDC4', '#95E1D3']
    planet_names = ['Planet A (On a Cob)', 'Planet B (Cronenberg)', 'Planet C (Purge Planet)']

    # Plot 1: Cumulative Success Rate Over Time
    ax1 = axes[0, 0]
    steps = [r['step'] for r in results]
    success_rates = [r['cumulative_success_rate'] * 100 for r in results]
    ax1.plot(steps, success_rates, color='#2E86AB', linewidth=2)
    ax1.set_xlabel('Step Number')
    ax1.set_ylabel('Success Rate (%)')
    ax1.set_title('Cumulative Success Rate Over Time')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=50, color='r', linestyle='--', alpha=0.5, label='50% baseline')
    ax1.legend()

    # Plot 2: Planet Selection Over Time
    ax2 = axes[0, 1]
    planet_choices = [r['planet'] for r in results]

    # Create a stacked view showing which planet was used when
    for planet_idx in range(3):
        planet_steps = [i for i, p in enumerate(planet_choices) if p == planet_idx]
        planet_y = [planet_idx] * len(planet_steps)
        ax2.scatter(planet_steps, planet_y, color=colors[planet_idx],
                   label=planet_names[planet_idx], alpha=0.6, s=10)

    ax2.set_xlabel('Step Number')
    ax2.set_ylabel('Planet Index')
    ax2.set_yticks([0, 1, 2])
    ax2.set_yticklabels(['Planet A', 'Planet B', 'Planet C'])
    ax2.set_title('Planet Selection Over Time')
    ax2.legend(loc='upper right', fontsize=8)
    ax2.grid(True, alpha=0.3)

    # Plot 3: Planet Usage Distribution
    ax3 = axes[1, 0]
    planet_counts = [router.planet_attempts[i] for i in range(3)]
    bars = ax3.bar(range(3), planet_counts, color=colors)
    ax3.set_xticks(range(3))
    ax3.set_xticklabels(['Planet A', 'Planet B', 'Planet C'])
    ax3.set_ylabel('Number of Trips')
    ax3.set_title('Planet Usage Distribution')

    # Add value labels on bars
    for bar, count in zip(bars, planet_counts):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}\n({count/sum(planet_counts)*100:.1f}%)',
                ha='center', va='bottom', fontweight='bold')

    ax3.grid(True, alpha=0.3, axis='y')

    # Plot 4: Summary Statistics
    ax4 = axes[1, 1]
    ax4.axis('off')

    final = results[-1]
    total_trips = len(results)
    successful_trips = sum(1 for r in results if r['survived'])

    summary_text = "📊 ADAPTIVE STRATEGY RESULTS\n\n"
    summary_text += f"Final Score: {final['morties_on_jessica']}/1000 ({final['morties_on_jessica']/10:.1f}%)\n"
    summary_text += f"Morties Lost: {final['morties_lost']}\n"
    summary_text += f"Total Trips: {total_trips}\n"
    summary_text += f"Successful Trips: {successful_trips}/{total_trips} ({successful_trips/total_trips*100:.1f}%)\n\n"

    summary_text += "Planet Usage:\n"
    for i in range(3):
        stats = router.get_stats()[i]
        summary_text += f"  {planet_names[i]}:\n"
        summary_text += f"    Trips: {stats['attempts']} ({stats['attempts']/total_trips*100:.1f}%)\n"
        summary_text += f"    Final Success Rate: {stats['success_rate']*100:.1f}%\n"

    ax4.text(0.1, 0.9, summary_text, transform=ax4.transAxes,
             fontsize=10, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

    plt.tight_layout()

    # Save the plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"morty_adaptive_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"\n📈 Analysis plot saved to: {filename}")

    # Save raw data
    data_filename = f"morty_adaptive_data_{timestamp}.json"
    with open(data_filename, 'w') as f:
        json.dump({
            'results': results,
            'planet_stats': {str(k): v for k, v in router.get_stats().items()}
        }, f, indent=2)
    print(f"💾 Raw data saved to: {data_filename}")

    return filename

def main():
    """Run the adaptive strategy"""
    print("\n" + "="*70)
    print("🎯 MORTY EXPRESS - ADAPTIVE STRATEGY")
    print("="*70)
    print("\nThis algorithm uses a multi-armed bandit approach:")
    print("  • Initial exploration phase to probe all planets")
    print("  • Adaptive routing based on recent success rates")
    print("  • Sliding window to track changing probabilities")
    print("  • Epsilon-greedy strategy for exploration vs exploitation")
    print("\nLet's save those Morties! 🚀\n")

    router = run_adaptive_episode()

    print("\n" + "="*70)
    print("📊 Generating visualizations...")
    print("="*70)

    plot_file = analyze_and_plot_adaptive(router)

    print(f"\n✅ All done! Check the generated files for detailed analysis.\n")

if __name__ == "__main__":
    main()
