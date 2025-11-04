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
PROGRESS_PRINT_FREQUENCY = 10
VERBOSE_MODE = True

# Trip settings
MORTIES_PER_TRIP = 3  # 1, 2, or 3 (API allows these values)
                      # Lower values = faster pattern detection but more API calls
                      # 3 = fastest completion, 1 = most granular detection

# NEW STRATEGY: Pattern Detection
SHORT_WINDOW = 10    # Detect recent performance quickly (for Planet 1 oscillations)
PHASE_THRESHOLD = 0.6  # If > 60% in last 10 trips, it's a HIGH phase
# ========================================================

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def start_episode():
    """Start a new episode"""
    response = requests.post(f"{BASE_URL}/api/mortys/start/", headers=headers)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    return response.json()

def send_morties(planet_index, morty_count=3):
    """Send morties through a portal"""
    payload = {"planet": planet_index, "morty_count": morty_count}
    response = requests.post(f"{BASE_URL}/api/mortys/portal/", headers=headers, json=payload)
    return response.json()

def get_status():
    """Get current episode status"""
    response = requests.get(f"{BASE_URL}/api/mortys/status/", headers=headers)
    return response.json()

class PatternDetector:
    """
    Detects oscillation patterns and exploits them.

    KEY INSIGHTS FROM BASELINE:
    - Planet 0: Stable ~49%, no pattern
    - Planet 1: OSCILLATES every ~20 trips between 80-90% and 20-30%
    - Planet 2: Long cycles (80 trips hot, 100 trips cold, etc.)
    """

    def __init__(self, short_window=10):
        self.short_window = short_window
        self.planet_names = [
            "Planet A (On a Cob)",
            "Planet B (Cronenberg)",
            "Planet C (Purge Planet)"
        ]

        # Track recent results with SHORT window to catch oscillations
        self.planet_windows = {
            0: deque(maxlen=short_window),
            1: deque(maxlen=short_window),
            2: deque(maxlen=short_window)
        }

        # Track total attempts
        self.planet_attempts = {0: 0, 1: 0, 2: 0}

        # Track all results
        self.all_results = []

        # Initial exploration
        self.initial_exploration_per_planet = 5  # Faster initial exploration
        self.initial_exploration_done = False

        # Track last N results for Planet 1 oscillation detection
        self.planet1_last_10 = deque(maxlen=10)
        self.planet1_phase = "UNKNOWN"  # HIGH, LOW, or UNKNOWN

    def get_recent_success_rate(self, planet_index):
        """Get very recent success rate (last 10 trips)"""
        window = self.planet_windows[planet_index]
        if len(window) == 0:
            return 0.5
        return sum(window) / len(window)

    def detect_planet1_phase(self):
        """
        Detect if Planet 1 is in HIGH or LOW phase.
        Based on pattern: HIGH (80-90%) alternates with LOW (20-30%) every ~10-20 trips
        """
        if len(self.planet1_last_10) < 5:
            return "UNKNOWN"

        recent_rate = sum(self.planet1_last_10) / len(self.planet1_last_10)

        if recent_rate >= PHASE_THRESHOLD:
            return "HIGH"
        else:
            return "LOW"

    def choose_planet(self, step):
        """
        Choose planet based on pattern detection.

        Strategy:
        1. Initial exploration (5 trips each)
        2. Detect Planet 1's phase
        3. Use Planet 1 during HIGH phase (80-90% success)
        4. Use Planet 2 during its hot cycles
        5. Fall back to best available when uncertain
        """
        import random

        # Initial exploration
        if not self.initial_exploration_done:
            for planet in range(3):
                if self.planet_attempts[planet] < self.initial_exploration_per_planet:
                    return planet
            self.initial_exploration_done = True
            print("\n🔍 Initial exploration complete! Pattern detection mode activated...\n")

        # Update Planet 1 phase detection
        self.planet1_phase = self.detect_planet1_phase()

        # Get recent success rates
        rates = {i: self.get_recent_success_rate(i) for i in range(3)}

        # STRATEGY: Use Planet 1 if it's in HIGH phase
        if self.planet1_phase == "HIGH" and self.planet_attempts[1] > 5:
            # Keep exploiting Planet 1's high phase
            return 1

        # If Planet 1 is in LOW phase, avoid it
        if self.planet1_phase == "LOW":
            # Choose best between Planet 0 and Planet 2
            if rates[2] > rates[0]:
                return 2
            else:
                return 0 if rates[0] > 0.3 else 2

        # Default: choose best performer
        # But with 10% exploration
        if random.random() < 0.1:
            return random.choice([0, 1, 2])

        best_planet = max(rates, key=rates.get)
        return best_planet

    def record_result(self, planet_index, survived):
        """Record the result of a trip"""
        self.planet_windows[planet_index].append(1 if survived else 0)
        self.planet_attempts[planet_index] += 1

        # Special tracking for Planet 1 oscillations
        if planet_index == 1:
            self.planet1_last_10.append(1 if survived else 0)

    def get_stats(self):
        """Get current statistics"""
        stats = {}
        for i in range(3):
            success_rate = self.get_recent_success_rate(i)
            stats[i] = {
                'name': self.planet_names[i],
                'success_rate': success_rate,
                'attempts': self.planet_attempts[i],
                'window_size': len(self.planet_windows[i])
            }
        return stats

def run_pattern_detector():
    """Run episode with pattern detection strategy"""
    print(f"\n{'='*70}")
    print(f"🎯 PATTERN DETECTOR - Exploiting Oscillations")
    print(f"{'='*70}")
    print(f"⚙️  Config: Window={SHORT_WINDOW}, Threshold={PHASE_THRESHOLD*100:.0f}%, Morties/Trip={MORTIES_PER_TRIP}")
    print(f"📊 Strategy: Detect Planet 1 oscillations and ride the wave!")
    print(f"{'='*70}\n")

    detector = PatternDetector(short_window=SHORT_WINDOW)

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

        # Choose planet using pattern detection
        planet_index = detector.choose_planet(step)

        # Send morties (configurable count)
        morties_to_send = min(MORTIES_PER_TRIP, status['morties_in_citadel'])
        result = send_morties(planet_index, morties_to_send)

        # Record result
        detector.record_result(planet_index, result['survived'])

        # Store results
        detector.all_results.append({
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

        # Verbose mode
        if VERBOSE_MODE and step <= 30:
            planet1_info = f"[P1 Phase: {detector.planet1_phase}]" if len(detector.planet1_last_10) >= 5 else ""
            print(f"  Trip {step}: Planet {planet_index} - {'✅' if result['survived'] else '❌'} {planet1_info} (Saved: {result['morties_on_planet_jessica']})")

        # Progress reports
        if step % PROGRESS_PRINT_FREQUENCY == 0:
            stats = detector.get_stats()

            print(f"\n📊 Step {step} Progress:")
            print(f"   Saved: {result['morties_on_planet_jessica']}, Lost: {result['morties_lost']}, Remaining: {result['morties_in_citadel']}")
            print(f"   Current success rate: {result['morties_on_planet_jessica'] / (1000 - result['morties_in_citadel']) * 100:.1f}%")
            print(f"   Last trip: Planet {planet_index} - {'✅' if result['survived'] else '❌'}")
            print(f"   Planet 1 Phase: {detector.planet1_phase} 🌊")
            print(f"\n   Recent Performance (last {SHORT_WINDOW} trips per planet):")
            for i in range(3):
                s = stats[i]
                phase_info = f" [{detector.planet1_phase}]" if i == 1 else ""
                print(f"     Planet {i}: {s['success_rate']*100:.1f}% ({s['attempts']} total){phase_info}")
            print()

        time.sleep(0.1)

    return detector

def analyze_and_plot(detector):
    """Save results"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_filename = f"morty_pattern_detector_{timestamp}.json"

    with open(data_filename, 'w') as f:
        json.dump({
            'results': detector.all_results,
            'planet_stats': {str(k): v for k, v in detector.get_stats().items()}
        }, f, indent=2)

    print(f"💾 Results saved to: {data_filename}")
    return data_filename

def main():
    print("\n" + "="*70)
    print("🎯 PATTERN DETECTOR STRATEGY")
    print("="*70)
    print("\nBased on analysis of baseline data:")
    print("  • Planet 1 oscillates: HIGH (80-90%) ↔ LOW (20-30%) every ~20 trips")
    print("  • Planet 2 has long cycles: 80 trips hot, 100 trips cold")
    print("  • Planet 0 is stable but mediocre (~49%)")
    print("\nStrategy: Detect Planet 1's phase and ride the HIGH wave! 🌊\n")

    detector = run_pattern_detector()
    analyze_and_plot(detector)

    print(f"\n✅ Done! Pattern detection complete.\n")

if __name__ == "__main__":
    main()
