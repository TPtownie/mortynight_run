import requests
import json
import time
import threading
from datetime import datetime

# ==================== CONFIGURATION ====================
API_TOKEN = "a4693c12a3de0cd5ceb3f6cb742f45747c9cbd88"
BASE_URL = "https://challenge.sphinxhq.com"
# ========================================================

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

class InteractivePatternRunner:
    def __init__(self):
        self.planet_pattern = [2, 1, 0]
        self.morties_per_trip = 1
        self.paused = False
        self.stop = False
        self.all_results = []
        self.planet_stats = {0: {'attempts': 0, 'successes': 0},
                            1: {'attempts': 0, 'successes': 0},
                            2: {'attempts': 0, 'successes': 0}}
        self.planet_names = {0: "Planet A (Cob)", 1: "Planet B (Cronenberg)", 2: "Planet C (Purge)"}

    def start_episode(self):
        response = requests.post(f"{BASE_URL}/api/mortys/start/", headers=headers)
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
        return response.json()

    def send_morties(self, planet_index, morty_count):
        payload = {"planet": planet_index, "morty_count": morty_count}
        response = requests.post(f"{BASE_URL}/api/mortys/portal/", headers=headers, json=payload)
        return response.json()

    def get_status(self):
        response = requests.get(f"{BASE_URL}/api/mortys/status/", headers=headers)
        return response.json()

    def show_menu(self):
        """Show interactive menu"""
        print(f"\n{'='*70}")
        print(f"⚙️  CURRENT SETTINGS:")
        print(f"   Pattern: {self.planet_pattern}")
        print(f"   Morties/Trip: {self.morties_per_trip}")
        print(f"\n💡 COMMANDS:")
        print(f"   p <pattern>  - Change pattern (e.g., 'p 2,1,0' or 'p 1,1,2')")
        print(f"   m <number>   - Change morties per trip (e.g., 'm 3')")
        print(f"   s            - Show current stats")
        print(f"   pause        - Pause/Resume")
        print(f"   quit         - Stop and save results")
        print(f"   <enter>      - Continue")
        print(f"{'='*70}\n")

    def show_stats(self):
        """Show current statistics"""
        print(f"\n{'─'*70}")
        print(f"📊 CURRENT STATISTICS:")
        total_attempts = sum(s['attempts'] for s in self.planet_stats.values())
        total_successes = sum(s['successes'] for s in self.planet_stats.values())
        if total_attempts > 0:
            overall_rate = total_successes / total_attempts * 100
            print(f"   Overall: {total_successes}/{total_attempts} = {overall_rate:.1f}%")
        print(f"   Planet Performance:")
        for p in range(3):
            if self.planet_stats[p]['attempts'] > 0:
                p_rate = self.planet_stats[p]['successes'] / self.planet_stats[p]['attempts'] * 100
                print(f"     Planet {p} ({self.planet_names[p]}): "
                      f"{self.planet_stats[p]['successes']}/{self.planet_stats[p]['attempts']} = {p_rate:.1f}%")
        print(f"{'─'*70}\n")

    def input_thread(self):
        """Background thread to handle user input"""
        while not self.stop:
            try:
                if self.paused:
                    self.show_menu()

                cmd = input("Command (or press Enter to continue): ").strip().lower()

                if cmd == '':
                    self.paused = False
                    continue

                if cmd == 'pause':
                    self.paused = not self.paused
                    print(f"{'⏸️  PAUSED' if self.paused else '▶️  RESUMED'}")

                elif cmd == 's':
                    self.show_stats()

                elif cmd == 'quit':
                    print("\n🛑 Stopping after current trip...")
                    self.stop = True
                    break

                elif cmd.startswith('p '):
                    try:
                        pattern_str = cmd[2:].strip()
                        new_pattern = [int(x.strip()) for x in pattern_str.split(',')]
                        if all(p in [0, 1, 2] for p in new_pattern):
                            self.planet_pattern = new_pattern
                            print(f"✅ Pattern changed to: {self.planet_pattern}")
                        else:
                            print("❌ Invalid pattern! Use only 0, 1, 2")
                    except:
                        print("❌ Invalid format! Use: p 2,1,0")

                elif cmd.startswith('m '):
                    try:
                        new_morties = int(cmd[2:].strip())
                        if new_morties in [1, 2, 3]:
                            self.morties_per_trip = new_morties
                            print(f"✅ Morties per trip changed to: {self.morties_per_trip}")
                        else:
                            print("❌ Invalid! Must be 1, 2, or 3")
                    except:
                        print("❌ Invalid format! Use: m 2")

                else:
                    print("❌ Unknown command")

            except:
                pass

    def run(self):
        """Run the pattern with interactive controls"""
        print(f"\n{'='*70}")
        print(f"🎯 INTERACTIVE PATTERN MODE")
        print(f"{'='*70}")
        print(f"You can adjust the pattern and settings while it's running!")
        print(f"Initial pattern: {self.planet_pattern}")
        print(f"Initial morties/trip: {self.morties_per_trip}")
        print(f"\nType 'pause' at any time to adjust settings")
        print(f"{'='*70}\n")

        # Start episode
        print("🚀 Starting new episode...")
        result = self.start_episode()
        if not result:
            return

        print("✅ Episode started!\n")
        time.sleep(0.5)

        # Start input thread
        input_thread = threading.Thread(target=self.input_thread, daemon=True)
        input_thread.start()

        step = 0
        pattern_index = 0

        while not self.stop:
            # Wait if paused
            while self.paused and not self.stop:
                time.sleep(0.1)

            if self.stop:
                break

            # Get current status
            status = self.get_status()

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

            # Choose planet from current pattern
            planet_index = self.planet_pattern[pattern_index % len(self.planet_pattern)]

            # Send morties
            morties_to_send = min(self.morties_per_trip, status['morties_in_citadel'])
            result = self.send_morties(planet_index, morties_to_send)

            # Record result
            survived = result['survived']
            self.planet_stats[planet_index]['attempts'] += 1
            if survived:
                self.planet_stats[planet_index]['successes'] += 1

            self.all_results.append({
                'step': step,
                'pattern_index': pattern_index % len(self.planet_pattern),
                'planet': planet_index,
                'morty_count': morties_to_send,
                'survived': survived,
                'morties_on_jessica': result['morties_on_planet_jessica'],
                'morties_lost': result['morties_lost']
            })

            # Display progress
            success_marker = "✅" if survived else "❌"
            trips_taken = 1000 - status['morties_in_citadel']
            current_rate = status['morties_on_planet_jessica'] / trips_taken * 100 if trips_taken > 0 else 0

            print(f"Step {step:3d}: Planet {planet_index} {success_marker} | "
                  f"Saved: {result['morties_on_planet_jessica']:3d} | "
                  f"Lost: {result['morties_lost']:3d} | "
                  f"Rate: {current_rate:5.1f}% | "
                  f"Pattern: {self.planet_pattern}")

            step += 1
            pattern_index += 1
            time.sleep(0.05)

        self.stop = True
        self.show_stats()

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"morty_interactive_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump({
                'final_pattern': self.planet_pattern,
                'final_morties_per_trip': self.morties_per_trip,
                'results': self.all_results,
                'planet_stats': self.planet_stats
            }, f, indent=2)

        print(f"💾 Results saved to: {filename}\n")

def main():
    try:
        runner = InteractivePatternRunner()
        runner.run()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!\n")

if __name__ == "__main__":
    main()
