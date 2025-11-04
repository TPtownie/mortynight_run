import requests
import json
import time
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
    return response.json()

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

    with open(filename, 'w') as f:
        json.dump({
            'pattern': PLANET_PATTERN,
            'morties_per_trip': MORTIES_PER_TRIP,
            'results': all_results,
            'planet_stats': planet_stats,
            'final_status': {
                'morties_on_jessica': status['morties_on_planet_jessica'],
                'morties_lost': status['morties_lost'],
                'steps_taken': status['steps_taken']
            }
        }, f, indent=2)

    print(f"💾 Results saved to: {filename}\n")

    return all_results, planet_stats

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
