import requests
import json
import time
from datetime import datetime

# ==================== CONFIGURATION ====================
API_TOKEN = "a4693c12a3de0cd5ceb3f6cb742f45747c9cbd88"
BASE_URL = "https://challenge.sphinxhq.com"
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

def display_status(status):
    """Display current game status"""
    print(f"\n{'='*70}")
    print(f"📊 CURRENT STATUS")
    print(f"{'='*70}")
    print(f"  🏰 Morties in Citadel: {status['morties_in_citadel']}")
    print(f"  ✅ Morties on Jessica: {status['morties_on_planet_jessica']} ({status['morties_on_planet_jessica']/10:.1f}%)")
    print(f"  💀 Morties Lost: {status['morties_lost']}")
    print(f"  🎯 Steps Taken: {status['steps_taken']}")
    if status['morties_in_citadel'] > 0:
        success_rate = status['morties_on_planet_jessica'] / (1000 - status['morties_in_citadel']) * 100
        print(f"  📈 Success Rate: {success_rate:.1f}%")
    print(f"{'='*70}\n")

def manual_control():
    """Run manual control mode"""
    print(f"\n{'='*70}")
    print(f"🎮 MORTY EXPRESS - MANUAL CONTROL MODE")
    print(f"{'='*70}")
    print(f"You will manually choose:")
    print(f"  • Which planet to send Morties to (0, 1, or 2)")
    print(f"  • How many Morties to send (1, 2, or 3)")
    print(f"\nPlanet Options:")
    print(f"  0 = Planet A (On a Cob)")
    print(f"  1 = Planet B (Cronenberg World)")
    print(f"  2 = Planet C (The Purge Planet)")
    print(f"{'='*70}\n")

    # Start episode
    print("🚀 Starting new episode...")
    result = start_episode()
    if not result:
        return

    print("✅ Episode started!\n")
    time.sleep(0.5)

    # Track results for analysis
    all_results = []
    step = 0

    while True:
        # Get current status
        status = get_status()
        display_status(status)

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

        # Get user input
        print("🎮 YOUR TURN!")
        print("-" * 70)

        # Choose planet
        while True:
            try:
                planet = input("Choose planet (0=Cob, 1=Cronenberg, 2=Purge): ").strip()
                planet = int(planet)
                if planet in [0, 1, 2]:
                    break
                else:
                    print("❌ Invalid! Must be 0, 1, or 2")
            except (ValueError, KeyboardInterrupt):
                print("\n👋 Exiting...")
                return
            except:
                print("❌ Invalid input! Try again.")

        # Choose morty count
        while True:
            try:
                max_available = min(3, status['morties_in_citadel'])
                morty_count = input(f"How many Morties? (1-{max_available}): ").strip()
                morty_count = int(morty_count)
                if 1 <= morty_count <= max_available:
                    break
                else:
                    print(f"❌ Invalid! Must be between 1 and {max_available}")
            except (ValueError, KeyboardInterrupt):
                print("\n👋 Exiting...")
                return
            except:
                print("❌ Invalid input! Try again.")

        # Send the morties
        print(f"\n🚪 Sending {morty_count} Morty{'s' if morty_count > 1 else ''} to Planet {planet}...")
        result = send_morties(planet, morty_count)

        # Display result
        if result['survived']:
            print(f"✅ SUCCESS! All {morty_count} Morties made it to Planet Jessica!")
        else:
            print(f"❌ FAILURE! {morty_count} Morty{'s' if morty_count > 1 else ''} lost...")

        # Track result
        all_results.append({
            'step': step,
            'planet': planet,
            'morty_count': morty_count,
            'survived': result['survived']
        })

        step += 1
        time.sleep(0.3)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"morty_manual_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump({
            'results': all_results,
            'final_status': status
        }, f, indent=2)
    print(f"💾 Session saved to: {filename}\n")

    # Show summary
    print("📊 YOUR PLANET USAGE:")
    planet_counts = {0: 0, 1: 0, 2: 0}
    planet_success = {0: 0, 1: 0, 2: 0}
    for r in all_results:
        planet_counts[r['planet']] += 1
        if r['survived']:
            planet_success[r['planet']] += 1

    planet_names = {0: "Planet A (Cob)", 1: "Planet B (Cronenberg)", 2: "Planet C (Purge)"}
    for p in range(3):
        if planet_counts[p] > 0:
            success_rate = planet_success[p] / planet_counts[p] * 100
            print(f"  {planet_names[p]}: {planet_success[p]}/{planet_counts[p]} = {success_rate:.1f}%")
        else:
            print(f"  {planet_names[p]}: Not used")

def main():
    try:
        manual_control()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!\n")

if __name__ == "__main__":
    main()
