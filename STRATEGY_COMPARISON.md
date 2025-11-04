# Morty Express - Strategy Comparison

## First Run: Baseline Single-Planet Strategy

The initial approach tested each planet independently, sending all 1000 Morties through one planet per episode.

### Results:
- **Planet A (On a Cob)**: 492/1000 saved (49.2%) ❌ WORST
- **Planet B (Cronenberg World)**: 549/1000 saved (54.9%) ✅ BEST
- **Planet C (The Purge Planet)**: 525/1000 saved (52.5%)

### Key Insights:
1. All planets have roughly equal **average** success rates (~50%)
2. The probabilities change dynamically over time (as Rick hinted)
3. Simply using the "best" planet isn't optimal since probabilities vary

## Improved Strategy: Adaptive Multi-Armed Bandit

### Algorithm Overview:
The adaptive approach treats this as a classic **Multi-Armed Bandit** problem where:
- Each planet is a "slot machine" with changing odds
- We need to balance **exploration** (testing planets) vs **exploitation** (using best planet)
- Success rates change based on number of trips taken

### Key Features:

#### 1. Initial Exploration Phase
- Sends first 10 trips to each planet (30 trips total)
- Gathers baseline data for all options before committing
- Ensures we don't miss a suddenly good option

#### 2. Epsilon-Greedy Strategy
- **85% exploitation**: Use the currently best-performing planet
- **15% exploration**: Randomly test other planets to detect changes
- Prevents getting stuck on a declining option

#### 3. Sliding Window Success Tracking
- Tracks last 30 trips per planet
- Focuses on **recent** performance, not historical averages
- Adapts to changing probabilities in real-time

#### 4. Adaptive Planet Selection
```python
for each morty group:
    if in_exploration_phase:
        choose least-explored planet
    elif random() < 0.15:  # 15% exploration
        choose randomly (prefer less-used planets)
    else:  # 85% exploitation
        choose planet with best recent success rate
```

### Expected Improvements:

Based on the baseline data showing that probabilities vary:
- **Baseline best**: 549/1000 (54.9%)
- **Expected adaptive**: 570-600/1000 (57-60%)

The improvement comes from:
1. **Dynamic adaptation**: Switch away from declining planets
2. **Catching upswings**: Detect when a struggling planet improves
3. **Avoiding downswings**: Reduce usage when success rates drop
4. **Balanced exploration**: Don't over-commit to one option

### Why This Beats Single-Planet:

Rick's hint: *"The probabilities are changing with time. Some change faster than others."*

If Planet B starts at 60% but drops to 45% by trip 200, while Planet C starts at 45% but rises to 60%, the adaptive strategy will:
1. Notice Planet B declining (via sliding window)
2. Explore alternatives more frequently
3. Discover Planet C improving
4. Shift traffic to Planet C

The single-planet strategy would stubbornly stick with Planet B and lose Morties.

## Implementation Details

### Files Created:
1. **morty_analyze.py**: Original baseline single-planet analysis
2. **morty_adaptive.py**: New adaptive multi-armed bandit algorithm
3. **morty_data_20251104_092714.json**: Results from baseline runs

### Algorithm Parameters:
- `window_size=30`: Track last 30 trips per planet
- `exploration_rate=0.15`: 15% random exploration
- `initial_exploration=10`: 10 trips per planet before adapting
- `morty_group_size=3`: Send 3 Morties per trip (API default)

### Success Metrics:
- **Primary**: Total Morties saved (morties_on_planet_jessica)
- **Secondary**: Trip success rate (successful_trips / total_trips)
- **Tertiary**: Adaptation speed (how quickly we shift to best planet)

## Next Steps

To run the adaptive strategy once API access is restored:
```bash
python3 morty_adaptive.py
```

This will:
1. Run one complete episode with adaptive routing
2. Generate visualization comparing to baseline
3. Save detailed trip-by-trip data
4. Show which planets were used when and why

## Expected Competition Performance

Based on the problem structure and Rick's hint about changing probabilities:

- **Naive approach** (one planet): ~50-55%
- **Best single planet** (from testing): ~55%
- **Adaptive strategy**: ~58-62%
- **Optimal strategy** (perfect knowledge): ~65-70%

The adaptive strategy should place competitively if:
1. Our hypothesis about changing probabilities is correct
2. The 15% exploration rate is appropriate
3. The 30-trip window captures the rate of change

## Mathematical Foundation

This is a variant of the **Non-Stationary Multi-Armed Bandit** problem:
- **Stationary**: Probabilities are fixed → use UCB or Thompson Sampling
- **Non-Stationary**: Probabilities change → use sliding window + epsilon-greedy
- **Adversarial**: Probabilities adversarially set → use EXP3

Our approach (sliding window ε-greedy) is optimal for non-stationary bandits where:
- Change rate is moderate (not too fast or slow)
- We want simple, interpretable decisions
- We need to complete all trials (can't abandon Morties)
