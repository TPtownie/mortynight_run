import requests
import json
import time
import matplotlib.pyplot as plt
from datetime import datetime

# ==================== CONFIGURATION ====================
API_TOKEN = "a4693c12a3de0cd5ceb3f6cb742f45747c9cbd88"
BASE_URL = "https://challenge.sphinxhq.com"

# ==================== YOUR PATTERN ====================
# Define your repeating pattern here:
PLANET_PATTERN = [2, 1, 0]  # Will repeat: 2,1,0,2,1,0,2,1,0...
MORTIES_PER_TRIP = 1        # 1, 2, or 3

# Example patterns to try:
# PLANET_PATTERN = [2, 1, 0]           # Test all three in order
# PLANET_PATTERN = [1, 1, 1, 0]        # Mostly planet 1, occasional planet 0
# PLANET_PATTERN = [2, 2, 2, 1, 1, 0]  # Heavy on planet 2 early
# PLANET_PATTERN = [1]                 # Only planet 1 (single planet test)
# ========================================================

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def start_episode():
    """Start a new episode"""
    response = requests.post(f"{BASE_URL}/api/mortys/start/", headers=headers)
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None
    return response.json()

def send_morties(planet_index, morty_count):
    """Send morties through a portal"""
    payload = {"planet": planet_index, "morty_count": morty_count}
    response = requests.post(f"{BASE_URL}/api/mortys/portal/", headers=headers, json=payload)
    return response.json()

def get_status():
    """Get current episode status"""
    response = requests.get(f"{BASE_URL}/api/mortys/status/", headers=headers)
    if response.status_code != 200:
        print(f"\n❌ API Error on status check:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        return None
    try:
        return response.json()
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON Decode Error:")
        print(f"   Response text: {response.text}")
        print(f"   Error: {e}")
        return None

def run_pattern():
    """Run with configured pattern"""
    planet_names = {0: "Planet A (Cob)", 1: "Planet B (Cronenberg)", 2: "Planet C (Purge)"}

    print(f"\n{'='*70}")
    print(f"🎯 MORTY EXPRESS - PATTERN MODE")
    print(f"{'='*70}")
    print(f"⚙️  Configuration:")
    print(f"   Pattern: {PLANET_PATTERN}")
    print(f"   Pattern Names: {[planet_names[p] for p in PLANET_PATTERN]}")
    print(f"   Morties per trip: {MORTIES_PER_TRIP}")
    print(f"   Pattern will repeat: {' → '.join(map(str, PLANET_PATTERN))} → {' → '.join(map(str, PLANET_PATTERN))}...")
    print(f"{'='*70}\n")

    # Start episode
    print("🚀 Starting new episode...")
    result = start_episode()
    if not result:
        return

    print("✅ Episode started!\n")
    time.sleep(0.5)

    # Track results
    all_results = []
    planet_stats = {0: {'attempts': 0, 'successes': 0},
                    1: {'attempts': 0, 'successes': 0},
                    2: {'attempts': 0, 'successes': 0}}

    step = 0
    pattern_index = 0

    while True:
        # Get current status
        status = get_status()

        # Handle API errors
        if status is None:
            print(f"\n⚠️  API error occurred. Saving partial results...")
            break

        # Check if done
        if status['morties_in_citadel'] == 0:
            print(f"\n{'='*70}")
            print(f"🎉 EPISODE COMPLETE!")
            print(f"{'='*70}")
            print(f"Final Score: {status['morties_on_planet_jessica']}/1000 ({status['morties_on_planet_jessica']/10:.1f}%)")
            print(f"Morties Lost: {status['morties_lost']}")
            print(f"Total Steps: {status['steps_taken']}")
            print(f"{'='*70}\n")
            break

        # Choose planet from pattern
        planet_index = PLANET_PATTERN[pattern_index % len(PLANET_PATTERN)]

        # Send morties
        morties_to_send = min(MORTIES_PER_TRIP, status['morties_in_citadel'])
        result = send_morties(planet_index, morties_to_send)

        # Record result
        survived = result['survived']
        planet_stats[planet_index]['attempts'] += 1
        if survived:
            planet_stats[planet_index]['successes'] += 1

        all_results.append({
            'step': step,
            'pattern_index': pattern_index % len(PLANET_PATTERN),
            'planet': planet_index,
            'morty_count': morties_to_send,
            'survived': survived,
            'morties_on_jessica': result['morties_on_planet_jessica'],
            'morties_lost': result['morties_lost'],
            'morties_in_citadel': result['morties_in_citadel']
        })

        # Display progress
        success_marker = "✅" if survived else "❌"
        trips_taken = 1000 - status['morties_in_citadel']
        current_rate = status['morties_on_planet_jessica'] / trips_taken * 100 if trips_taken > 0 else 0

        print(f"Step {step:3d}: Planet {planet_index} [{planet_names[planet_index][:15]:15s}] {success_marker} | "
              f"Saved: {result['morties_on_planet_jessica']:3d} | "
              f"Lost: {result['morties_lost']:3d} | "
              f"Rate: {current_rate:5.1f}%")

        # Show stats every 50 steps
        if step > 0 and step % 50 == 0:
            print(f"\n{'─'*70}")
            print(f"📊 PROGRESS AFTER {step} STEPS:")
            print(f"   Overall: {result['morties_on_planet_jessica']}/{trips_taken} = {current_rate:.1f}%")
            print(f"   Planet Performance:")
            for p in range(3):
                if planet_stats[p]['attempts'] > 0:
                    p_rate = planet_stats[p]['successes'] / planet_stats[p]['attempts'] * 100
                    print(f"     Planet {p}: {planet_stats[p]['successes']}/{planet_stats[p]['attempts']} = {p_rate:.1f}%")
            print(f"{'─'*70}\n")

        step += 1
        pattern_index += 1
        time.sleep(0.05)  # Small delay to avoid rate limiting

    # Final statistics
    print(f"\n{'='*70}")
    print(f"📊 FINAL STATISTICS")
    print(f"{'='*70}")
    print(f"Pattern used: {PLANET_PATTERN}")
    print(f"Morties per trip: {MORTIES_PER_TRIP}")
    print(f"\nPlanet Performance:")
    for p in range(3):
        if planet_stats[p]['attempts'] > 0:
            p_rate = planet_stats[p]['successes'] / planet_stats[p]['attempts'] * 100
            print(f"  {planet_names[p]}: {planet_stats[p]['successes']}/{planet_stats[p]['attempts']} = {p_rate:.1f}%")
        else:
            print(f"  {planet_names[p]}: Not used")
    print(f"{'='*70}\n")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"morty_pattern_{timestamp}.json"

    # Prepare final status (handle case where API failed)
    final_status = {}
    if status and all_results:
        final_status = {
            'morties_on_jessica': status.get('morties_on_planet_jessica', all_results[-1]['morties_on_jessica']),
            'morties_lost': status.get('morties_lost', all_results[-1]['morties_lost']),
            'steps_taken': status.get('steps_taken', len(all_results))
        }
    elif all_results:
        # Use last result if status is None
        final_status = {
            'morties_on_jessica': all_results[-1]['morties_on_jessica'],
            'morties_lost': all_results[-1]['morties_lost'],
            'steps_taken': len(all_results)
        }

    with open(filename, 'w') as f:
        json.dump({
            'pattern': PLANET_PATTERN,
            'morties_per_trip': MORTIES_PER_TRIP,
            'results': all_results,
            'planet_stats': planet_stats,
            'final_status': final_status,
            'completed': status is not None and status.get('morties_in_citadel', 1) == 0
        }, f, indent=2)

    print(f"💾 Results saved to: {filename}\n")

    # Generate visualization if we have results
    if all_results:
        print(f"📊 Generating visualization...")
        png_filename = create_visualization(all_results, planet_stats, timestamp)
        print(f"📈 Visualization saved to: {png_filename}\n")

    return all_results, planet_stats

def create_visualization(all_results, planet_stats, timestamp):
    """Create visualization of the pattern run"""
    colors = ['#FF6B6B', '#4ECDC4', '#95E1D3']
    planet_names_short = ['Planet A', 'Planet B', 'Planet C']

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'Pattern Run: {PLANET_PATTERN} (Morties/Trip: {MORTIES_PER_TRIP})',
                 fontsize=16, fontweight='bold')

    # Plot 1: Success Rate Over Time
    ax1 = axes[0, 0]
    steps = [r['step'] for r in all_results]
    # Calculate cumulative success rate
    cumulative_rates = []
    for i, r in enumerate(all_results):
        trips_so_far = i + 1
        successes = sum(1 for x in all_results[:i+1] if x['survived'])
        cumulative_rates.append(successes / trips_so_far * 100)

    ax1.plot(steps, cumulative_rates, color='#2E86AB', linewidth=2)
    ax1.set_xlabel('Step Number')
    ax1.set_ylabel('Success Rate (%)')
    ax1.set_title('Cumulative Success Rate Over Time')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=50, color='r', linestyle='--', alpha=0.5, label='50% baseline')
    ax1.legend()

    # Plot 2: Planet Usage Over Time
    ax2 = axes[0, 1]
    planet_choices = [r['planet'] for r in all_results]
    for planet_idx in range(3):
        planet_steps = [i for i, p in enumerate(planet_choices) if p == planet_idx]
        planet_y = [planet_idx] * len(planet_steps)
        ax2.scatter(planet_steps, planet_y, color=colors[planet_idx],
                   label=planet_names_short[planet_idx], alpha=0.6, s=10)

    ax2.set_xlabel('Step Number')
    ax2.set_ylabel('Planet Used')
    ax2.set_yticks([0, 1, 2])
    ax2.set_yticklabels(planet_names_short)
    ax2.set_title('Planet Selection Pattern')
    ax2.legend(loc='upper right', fontsize=8)
    ax2.grid(True, alpha=0.3, axis='x')

    # Plot 3: Planet Performance
    ax3 = axes[1, 0]
    planets_used = [p for p in range(3) if planet_stats[p]['attempts'] > 0]
    if planets_used:
        success_rates = []
        for p in planets_used:
            rate = planet_stats[p]['successes'] / planet_stats[p]['attempts'] * 100
            success_rates.append(rate)

        bars = ax3.bar([planet_names_short[p] for p in planets_used],
                      success_rates,
                      color=[colors[p] for p in planets_used])
        ax3.set_ylabel('Success Rate (%)')
        ax3.set_title('Success Rate by Planet')
        ax3.set_ylim([0, 100])
        ax3.grid(True, alpha=0.3, axis='y')

        # Add value labels
        for bar, rate, p in zip(bars, success_rates, planets_used):
            height = bar.get_height()
            attempts = planet_stats[p]['attempts']
            successes = planet_stats[p]['successes']
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{rate:.1f}%\n({successes}/{attempts})',
                    ha='center', va='bottom', fontweight='bold')

    # Plot 4: Summary Stats
    ax4 = axes[1, 1]
    ax4.axis('off')

    final_result = all_results[-1]
    total_trips = len(all_results)
    successful_trips = sum(1 for r in all_results if r['survived'])

    summary_text = f"PATTERN RUN SUMMARY\n\n"
    summary_text += f"Pattern: {PLANET_PATTERN}\n"
    summary_text += f"Morties/Trip: {MORTIES_PER_TRIP}\n\n"
    summary_text += f"Final Score: {final_result['morties_on_jessica']}/1000\n"
    summary_text += f"  ({final_result['morties_on_jessica']/10:.1f}%)\n\n"
    summary_text += f"Morties Lost: {final_result['morties_lost']}\n"
    summary_text += f"Total Trips: {total_trips}\n"
    summary_text += f"Successful Trips: {successful_trips}/{total_trips}\n"
    summary_text += f"  ({successful_trips/total_trips*100:.1f}%)\n\n"

    summary_text += "Planet Usage:\n"
    for p in range(3):
        if planet_stats[p]['attempts'] > 0:
            rate = planet_stats[p]['successes'] / planet_stats[p]['attempts'] * 100
            summary_text += f"  {planet_names_short[p]}: {planet_stats[p]['attempts']} trips "
            summary_text += f"({rate:.1f}%)\n"

    ax4.text(0.1, 0.9, summary_text, transform=ax4.transAxes,
             fontsize=11, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

    plt.tight_layout()

    png_filename = f"morty_pattern_{timestamp}.png"
    plt.savefig(png_filename, dpi=300, bbox_inches='tight')
    plt.close()

    return png_filename

def main():
    print("\n" + "="*70)
    print("To change the pattern, edit the CONFIGURATION section at the top:")
    print("  PLANET_PATTERN = [2, 1, 0]  # Your repeating pattern")
    print("  MORTIES_PER_TRIP = 1        # 1, 2, or 3")
    print("="*70)

    try:
        run_pattern()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!\n")

if __name__ == "__main__":
    main()
