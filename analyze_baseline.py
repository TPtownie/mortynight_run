import json
import matplotlib.pyplot as plt
import numpy as np

# Load baseline data
with open('morty_data_20251104_092714.json', 'r') as f:
    data = json.load(f)

planet_names = {
    '0': 'Planet A (On a Cob)',
    '1': 'Planet B (Cronenberg World)',
    '2': 'Planet C (The Purge Planet)'
}

colors = ['#FF6B6B', '#4ECDC4', '#95E1D3']

# Create comprehensive analysis
fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# Main title
fig.suptitle('Morty Express - Baseline Analysis: Dynamic Probability Discovery',
             fontsize=18, fontweight='bold')

# Plot 1: Success Rate Over Time for Each Planet (Large)
ax1 = fig.add_subplot(gs[0, :])
for planet_idx, color in zip(['0', '1', '2'], colors):
    results = data[planet_idx]
    steps = [r['step'] for r in results]
    success_rates = [r['cumulative_success_rate'] * 100 for r in results]
    ax1.plot(steps, success_rates, label=planet_names[planet_idx],
             color=color, linewidth=2, alpha=0.8)

ax1.set_xlabel('Trip Number', fontsize=12)
ax1.set_ylabel('Cumulative Success Rate (%)', fontsize=12)
ax1.set_title('How Success Rates Evolve Over Time (The Key Insight)', fontsize=14)
ax1.legend(fontsize=11)
ax1.grid(True, alpha=0.3)
ax1.axhline(y=50, color='red', linestyle='--', alpha=0.5, linewidth=1)
ax1.text(300, 50.5, '50% baseline', fontsize=10, color='red')

# Plot 2: Moving Average Success Rate (Shows trends)
ax2 = fig.add_subplot(gs[1, 0])
window = 20
for planet_idx, color in zip(['0', '1', '2'], colors):
    results = data[planet_idx]
    survivals = [1 if r['survived'] else 0 for r in results]

    # Calculate moving average
    moving_avg = []
    for j in range(len(survivals)):
        start_idx = max(0, j - window + 1)
        window_data = survivals[start_idx:j+1]
        moving_avg.append(sum(window_data) / len(window_data) * 100)

    steps = [r['step'] for r in results]
    ax2.plot(steps, moving_avg, label=planet_names[planet_idx],
             color=color, linewidth=2)

ax2.set_xlabel('Trip Number', fontsize=10)
ax2.set_ylabel('Success Rate (%)', fontsize=10)
ax2.set_title(f'{window}-Trip Moving Average\n(Recent Performance)', fontsize=11)
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)
ax2.axhline(y=50, color='red', linestyle='--', alpha=0.3, linewidth=1)

# Plot 3: Success Rate by Trip Phase (Early/Mid/Late)
ax3 = fig.add_subplot(gs[1, 1])
phases = ['Early\n(0-100)', 'Mid\n(100-200)', 'Late\n(200+)']
phase_ranges = [(0, 100), (100, 200), (200, 400)]

x = np.arange(len(phases))
width = 0.25

for i, planet_idx in enumerate(['0', '1', '2']):
    results = data[planet_idx]
    phase_rates = []

    for start, end in phase_ranges:
        phase_results = [r for r in results if start <= r['step'] < end]
        if phase_results:
            successes = sum(1 for r in phase_results if r['survived'])
            rate = successes / len(phase_results) * 100
            phase_rates.append(rate)
        else:
            phase_rates.append(0)

    offset = width * (i - 1)
    ax3.bar(x + offset, phase_rates, width, label=f"Planet {planet_idx}", color=colors[i])

ax3.set_ylabel('Success Rate (%)', fontsize=10)
ax3.set_title('Success Rate by Phase\n(Shows Probability Change)', fontsize=11)
ax3.set_xticks(x)
ax3.set_xticklabels(phases, fontsize=9)
ax3.legend(fontsize=9)
ax3.grid(True, alpha=0.3, axis='y')
ax3.axhline(y=50, color='red', linestyle='--', alpha=0.3, linewidth=1)

# Plot 4: Volatility Analysis (Standard Deviation)
ax4 = fig.add_subplot(gs[1, 2])
volatilities = []
labels_short = []

for planet_idx, color in zip(['0', '1', '2'], colors):
    results = data[planet_idx]

    # Calculate moving average to see volatility
    survivals = [1 if r['survived'] else 0 for r in results]
    window_size = 30
    moving_avgs = []

    for j in range(window_size, len(survivals)):
        window_data = survivals[j-window_size:j]
        moving_avgs.append(sum(window_data) / len(window_data))

    volatility = np.std(moving_avgs) * 100
    volatilities.append(volatility)
    labels_short.append(f"Planet {planet_idx}")

bars = ax4.barh(labels_short, volatilities, color=colors)
ax4.set_xlabel('Volatility (Std Dev %)', fontsize=10)
ax4.set_title('Probability Volatility\n(Higher = More Change)', fontsize=11)
ax4.grid(True, alpha=0.3, axis='x')

# Add value labels
for bar, vol in zip(bars, volatilities):
    width = bar.get_width()
    ax4.text(width, bar.get_y() + bar.get_height()/2.,
            f'{vol:.2f}%', ha='left', va='center', fontsize=10)

# Plot 5: Final Scores
ax5 = fig.add_subplot(gs[2, 0])
final_scores = []
for planet_idx in ['0', '1', '2']:
    results = data[planet_idx]
    final_score = results[-1]['morties_on_jessica']
    final_scores.append(final_score)

bars = ax5.bar(range(3), final_scores, color=colors)
ax5.set_xticks(range(3))
ax5.set_xticklabels(['Planet A', 'Planet B', 'Planet C'], fontsize=9)
ax5.set_ylabel('Morties Saved', fontsize=10)
ax5.set_title('Final Results', fontsize=11)
ax5.set_ylim([0, 1000])
ax5.grid(True, alpha=0.3, axis='y')

for bar, score in zip(bars, final_scores):
    height = bar.get_height()
    ax5.text(bar.get_x() + bar.get_width()/2., height,
            f'{score}\n{score/10:.1f}%',
            ha='center', va='bottom', fontweight='bold', fontsize=10)

# Plot 6: Consecutive Success/Failure Streaks
ax6 = fig.add_subplot(gs[2, 1])
max_streaks = []

for planet_idx, color in zip(['0', '1', '2'], colors):
    results = data[planet_idx]
    survivals = [1 if r['survived'] else 0 for r in results]

    # Find max success streak
    current_streak = 0
    max_success_streak = 0

    for s in survivals:
        if s == 1:
            current_streak += 1
            max_success_streak = max(max_success_streak, current_streak)
        else:
            current_streak = 0

    max_streaks.append(max_success_streak)

bars = ax6.bar(range(3), max_streaks, color=colors)
ax6.set_xticks(range(3))
ax6.set_xticklabels(['Planet A', 'Planet B', 'Planet C'], fontsize=9)
ax6.set_ylabel('Consecutive Successes', fontsize=10)
ax6.set_title('Longest Success Streak\n(Indicates Hot Streaks)', fontsize=11)
ax6.grid(True, alpha=0.3, axis='y')

for bar, streak in zip(bars, max_streaks):
    height = bar.get_height()
    ax6.text(bar.get_x() + bar.get_width()/2., height,
            f'{streak}',
            ha='center', va='bottom', fontweight='bold', fontsize=10)

# Plot 7: Key Insights Text Box
ax7 = fig.add_subplot(gs[2, 2])
ax7.axis('off')

insights = """
KEY INSIGHTS FROM BASELINE:

1. All planets average ~50-55%
   but with dynamic changes

2. Planet B performed best (54.9%)
   but had high volatility

3. Success rates vary significantly
   within each episode

4. Different planets have different
   volatility patterns

WHY ADAPTIVE STRATEGY WINS:

✓ Detects when a planet "heats up"
✓ Abandons declining planets
✓ Balances exploration vs exploitation
✓ Adapts to changing probabilities

EXPECTED IMPROVEMENT:
Baseline best: 549/1000 (54.9%)
Adaptive target: 570-600/1000 (57-60%)

IMPROVEMENT: +4-8% more Morties saved
"""

ax7.text(0.05, 0.95, insights, transform=ax7.transAxes,
         fontsize=10, verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.2))

plt.savefig('baseline_analysis_comprehensive.png', dpi=300, bbox_inches='tight')
print("✅ Comprehensive analysis saved to: baseline_analysis_comprehensive.png")

# Print numerical summary
print("\n" + "="*70)
print("BASELINE ANALYSIS SUMMARY")
print("="*70)

for planet_idx in ['0', '1', '2']:
    results = data[planet_idx]
    survivals = [1 if r['survived'] else 0 for r in results]

    # Phase analysis
    early = survivals[:100]
    mid = survivals[100:200]
    late = survivals[200:]

    print(f"\n{planet_names[planet_idx]}:")
    print(f"  Overall: {sum(survivals)}/{len(survivals)} ({sum(survivals)/len(survivals)*100:.1f}%)")
    print(f"  Early (0-100):   {sum(early)}/{len(early)} ({sum(early)/len(early)*100:.1f}%)")
    print(f"  Mid (100-200):   {sum(mid)}/{len(mid)} ({sum(mid)/len(mid)*100:.1f}%)")
    print(f"  Late (200+):     {sum(late)}/{len(late)} ({sum(late)/len(late)*100:.1f}%)")

    # Calculate standard deviation of moving average
    window_size = 30
    moving_avgs = []
    for j in range(window_size, len(survivals)):
        window_data = survivals[j-window_size:j]
        moving_avgs.append(sum(window_data) / len(window_data) * 100)

    volatility = np.std(moving_avgs)
    print(f"  Volatility (σ): {volatility:.2f}%")

print("\n" + "="*70)
print("\n🎯 CONCLUSION: Probabilities change over time!")
print("   An adaptive strategy that responds to these changes")
print("   should outperform any single-planet approach.\n")
