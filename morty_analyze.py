import requests
import json
import time
import matplotlib.pyplot as plt
from datetime import datetime

API_TOKEN = "a4693c12a3de0cd5ceb3f6cb742f45747c9cbd88"
BASE_URL = "https://challenge.sphinxhq.com"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def start_episode():
    """Start a new episode"""
    response = requests.post(f"{BASE_URL}/api/mortys/start/", headers=headers)
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

def run_single_planet_episode(planet_index, planet_name):
    """Run a complete episode using only one planet"""
    print(f"\n{'='*60}")
    print(f"Starting episode for {planet_name} (Planet {planet_index})")
    print(f"{'='*60}\n")
    
    # Start new episode
    start_episode()
    time.sleep(0.5)
    
    results = []
    step = 0
    
    while True:
        status = get_status()
        
        if status['morties_in_citadel'] == 0:
            print(f"\nEpisode complete!")
            print(f"Final score: {status['morties_on_planet_jessica']}/1000 ({status['morties_on_planet_jessica']/10:.1f}%)")
            print(f"Morties lost: {status['morties_lost']}")
            print(f"Total steps: {status['steps_taken']}")
            break
        
        # Send 3 morties (or whatever is left)
        morties_to_send = min(3, status['morties_in_citadel'])
        
        result = send_morties(planet_index, morties_to_send)
        
        results.append({
            'step': step,
            'morties_sent': result['morties_sent'],
            'survived': result['survived'],
            'morties_in_citadel': result['morties_in_citadel'],
            'morties_on_jessica': result['morties_on_planet_jessica'],
            'morties_lost': result['morties_lost'],
            'cumulative_success_rate': result['morties_on_planet_jessica'] / (1000 - result['morties_in_citadel']) if (1000 - result['morties_in_citadel']) > 0 else 0
        })
        
        step += 1
        
        # Print progress every 50 steps
        if step % 50 == 0:
            print(f"Step {step}: {result['morties_on_planet_jessica']} saved, {result['morties_lost']} lost, {result['morties_in_citadel']} remaining")
        
        time.sleep(0.1)  # Small delay to avoid rate limiting
    
    return results

def analyze_and_plot(results_dict):
    """Analyze results and create visualizations"""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Morty Express - Single Planet Analysis', fontsize=16, fontweight='bold')
    
    colors = ['#FF6B6B', '#4ECDC4', '#95E1D3']
    planet_names = ['Planet A (On a Cob)', 'Planet B (Cronenberg)', 'Planet C (Purge Planet)']
    
    # Plot 1: Cumulative Success Rate Over Time
    ax1 = axes[0, 0]
    for i, (planet_idx, results) in enumerate(results_dict.items()):
        steps = [r['step'] for r in results]
        success_rates = [r['cumulative_success_rate'] * 100 for r in results]
        ax1.plot(steps, success_rates, label=planet_names[planet_idx], color=colors[i], linewidth=2)
    
    ax1.set_xlabel('Step Number')
    ax1.set_ylabel('Success Rate (%)')
    ax1.set_title('Cumulative Success Rate Over Time')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Survival per Trip (Moving Average)
    ax2 = axes[0, 1]
    window = 20
    for i, (planet_idx, results) in enumerate(results_dict.items()):
        survivals = [1 if r['survived'] else 0 for r in results]
        # Calculate moving average
        moving_avg = []
        for j in range(len(survivals)):
            start_idx = max(0, j - window + 1)
            moving_avg.append(sum(survivals[start_idx:j+1]) / (j - start_idx + 1) * 100)
        
        steps = [r['step'] for r in results]
        ax2.plot(steps, moving_avg, label=planet_names[planet_idx], color=colors[i], linewidth=2)
    
    ax2.set_xlabel('Step Number')
    ax2.set_ylabel('Success Rate (%) - 20-step Moving Average')
    ax2.set_title('Success Rate Trend (Moving Average)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Final Scores Comparison
    ax3 = axes[1, 0]
    final_scores = []
    for planet_idx in sorted(results_dict.keys()):
        results = results_dict[planet_idx]
        final_score = results[-1]['morties_on_jessica']
        final_scores.append(final_score)
    
    bars = ax3.bar(range(len(planet_names)), final_scores, color=colors)
    ax3.set_xticks(range(len(planet_names)))
    ax3.set_xticklabels(planet_names, rotation=15, ha='right')
    ax3.set_ylabel('Morties Saved')
    ax3.set_title('Final Scores by Planet')
    ax3.set_ylim([0, 1000])
    
    # Add value labels on bars
    for bar, score in zip(bars, final_scores):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{score}\n({score/10:.1f}%)',
                ha='center', va='bottom', fontweight='bold')
    
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Plot 4: Summary Statistics
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    summary_text = "Summary Statistics:\n\n"
    for planet_idx in sorted(results_dict.keys()):
        results = results_dict[planet_idx]
        final = results[-1]
        
        total_trips = len(results)
        successful_trips = sum(1 for r in results if r['survived'])
        trip_success_rate = (successful_trips / total_trips * 100) if total_trips > 0 else 0
        
        summary_text += f"{planet_names[planet_idx]}:\n"
        summary_text += f"  Final Score: {final['morties_on_jessica']}/1000 ({final['morties_on_jessica']/10:.1f}%)\n"
        summary_text += f"  Morties Lost: {final['morties_lost']}\n"
        summary_text += f"  Total Trips: {total_trips}\n"
        summary_text += f"  Successful Trips: {successful_trips}/{total_trips} ({trip_success_rate:.1f}%)\n\n"
    
    ax4.text(0.1, 0.9, summary_text, transform=ax4.transAxes,
             fontsize=11, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    
    # Save the plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"morty_analysis_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"\nAnalysis plot saved to: {filename}")
    
    # Also save raw data
    data_filename = f"morty_data_{timestamp}.json"
    with open(data_filename, 'w') as f:
        # Convert dict keys to strings for JSON
        json_data = {str(k): v for k, v in results_dict.items()}
        json.dump(json_data, f, indent=2)
    print(f"Raw data saved to: {data_filename}")
    
    return filename

def main():
    """Run the complete analysis"""
    print("Morty Express - Planet Analysis")
    print("="*60)
    print("\nThis will run 3 complete episodes, one for each planet.")
    print("Each episode sends all 1000 Morties through a single planet.")
    print("\nThis will take a few minutes...\n")
    
    results_dict = {}
    
    planet_names = [
        "Planet A (On a Cob)",
        "Planet B (Cronenberg World)",
        "Planet C (The Purge Planet)"
    ]
    
    for planet_idx in range(3):
        results = run_single_planet_episode(planet_idx, planet_names[planet_idx])
        results_dict[planet_idx] = results
        
        # Wait a bit between episodes
        if planet_idx < 2:
            print(f"\nWaiting 5 seconds before next episode...\n")
            time.sleep(5)
    
    print("\n" + "="*60)
    print("Analysis complete! Generating visualizations...")
    print("="*60)
    
    plot_file = analyze_and_plot(results_dict)
    
    print(f"\nAll done! Check the generated files for detailed analysis.")

if __name__ == "__main__":
    main()