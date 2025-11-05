import streamlit as st
import json
import glob
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Morty Express Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00A9FF;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
    }
    .planet-0 { color: #FF6B6B; font-weight: bold; }
    .planet-1 { color: #4ECDC4; font-weight: bold; }
    .planet-2 { color: #95E1D3; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

PLANET_NAMES = {
    0: "Planet A (On a Cob)",
    1: "Planet B (Cronenberg)",
    2: "Planet C (Purge Planet)"
}

PLANET_COLORS = {
    0: "#FF6B6B",
    1: "#4ECDC4",
    2: "#95E1D3"
}

@st.cache_data
def load_all_runs():
    """Load all JSON result files from the directory"""
    runs = []

    # Load baseline runs (morty_data_*.json)
    for filepath in glob.glob("morty_data_*.json"):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                timestamp = Path(filepath).stem.replace("morty_data_", "")

                # This is the baseline format with planet indices as keys
                runs.append({
                    'filename': filepath,
                    'timestamp': timestamp,
                    'type': 'baseline',
                    'data': data
                })
        except Exception as e:
            st.sidebar.error(f"Error loading {filepath}: {e}")

    # Load pattern runs (morty_pattern_*.json)
    for filepath in glob.glob("morty_pattern_*.json"):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                timestamp = Path(filepath).stem.replace("morty_pattern_", "")

                runs.append({
                    'filename': filepath,
                    'timestamp': timestamp,
                    'type': 'pattern',
                    'data': data
                })
        except Exception as e:
            st.sidebar.error(f"Error loading {filepath}: {e}")

    # Load pattern detector runs
    for filepath in glob.glob("morty_pattern_detector_*.json"):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                timestamp = Path(filepath).stem.replace("morty_pattern_detector_", "")

                runs.append({
                    'filename': filepath,
                    'timestamp': timestamp,
                    'type': 'detector',
                    'data': data
                })
        except Exception as e:
            st.sidebar.error(f"Error loading {filepath}: {e}")

    return sorted(runs, key=lambda x: x['timestamp'], reverse=True)

def parse_baseline_data(data):
    """Parse baseline format data (planet indices as keys)"""
    all_results = []
    planet_stats = {0: [], 1: [], 2: []}

    for planet_idx_str, results in data.items():
        planet_idx = int(planet_idx_str)
        for result in results:
            result['planet'] = planet_idx
            all_results.append(result)
            planet_stats[planet_idx].append(result)

    return all_results, planet_stats

def parse_pattern_data(data):
    """Parse pattern run data"""
    all_results = data.get('results', [])
    planet_stats = data.get('planet_stats', {})

    # Convert string keys to int
    planet_stats = {int(k): v for k, v in planet_stats.items()}

    return all_results, planet_stats, data.get('pattern', []), data.get('final_status', {})

def parse_detector_data(data):
    """Parse pattern detector data"""
    all_results = data.get('results', [])
    planet_stats_raw = data.get('planet_stats', {})

    # Convert detector format to standard format
    planet_stats = {}
    for planet_idx_str, stats in planet_stats_raw.items():
        planet_idx = int(planet_idx_str)
        # Detector format has different structure
        planet_stats[planet_idx] = {
            'attempts': stats.get('attempts', 0),
            'successes': int(stats.get('success_rate', 0) * stats.get('attempts', 0))
        }

    return all_results, planet_stats

def create_success_rate_over_time(results):
    """Create line chart of success rate over time"""
    df = pd.DataFrame(results)

    if 'cumulative_success_rate' in df.columns:
        df['success_rate_pct'] = df['cumulative_success_rate'] * 100
    else:
        # Calculate it
        df['success_rate_pct'] = (df.index + 1).map(
            lambda i: sum(df['survived'][:i+1]) / (i+1) * 100
        )

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['step'],
        y=df['success_rate_pct'],
        mode='lines',
        name='Success Rate',
        line=dict(color='#667eea', width=3),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.2)'
    ))

    fig.add_hline(y=50, line_dash="dash", line_color="red",
                  annotation_text="50% Baseline", annotation_position="right")

    fig.update_layout(
        title="Cumulative Success Rate Over Time",
        xaxis_title="Step Number",
        yaxis_title="Success Rate (%)",
        hovermode='x unified',
        template='plotly_white'
    )

    return fig

def create_planet_usage_chart(results):
    """Create scatter plot of planet usage over time"""
    df = pd.DataFrame(results)

    if 'planet' not in df.columns:
        return None

    df['planet_name'] = df['planet'].map(PLANET_NAMES)
    df['color'] = df['planet'].map(PLANET_COLORS)
    df['success_marker'] = df['survived'].map({True: '✅', False: '❌'})

    fig = go.Figure()

    for planet_idx in sorted(df['planet'].unique()):
        planet_df = df[df['planet'] == planet_idx]

        fig.add_trace(go.Scatter(
            x=planet_df['step'],
            y=[planet_idx] * len(planet_df),
            mode='markers',
            name=PLANET_NAMES[planet_idx],
            marker=dict(
                color=PLANET_COLORS[planet_idx],
                size=8,
                symbol=planet_df['survived'].map({True: 'circle', False: 'x'})
            ),
            customdata=planet_df[['success_marker']],
            hovertemplate='<b>Step %{x}</b><br>%{customdata[0]}<extra></extra>'
        ))

    fig.update_layout(
        title="Planet Selection Over Time",
        xaxis_title="Step Number",
        yaxis_title="Planet",
        yaxis=dict(
            tickmode='array',
            tickvals=[0, 1, 2],
            ticktext=[PLANET_NAMES[i] for i in range(3)]
        ),
        hovermode='closest',
        template='plotly_white',
        height=400
    )

    return fig

def create_planet_performance_chart(planet_stats):
    """Create bar chart of planet performance"""
    planets = []
    success_rates = []
    attempts = []

    for planet_idx in sorted(planet_stats.keys()):
        stats = planet_stats[planet_idx]

        # Handle different formats
        if isinstance(stats, list):
            # Baseline format - list of results
            planet_attempts = len(stats)
            successes = sum(1 for r in stats if r.get('survived', False))
        else:
            # Pattern/detector format - dict with attempts/successes
            planet_attempts = stats.get('attempts', 0)
            successes = stats.get('successes', 0)

        if planet_attempts > 0:
            planets.append(PLANET_NAMES[planet_idx])
            success_rates.append(successes / planet_attempts * 100)
            attempts.append(planet_attempts)

    if not planets:
        return None

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=planets,
        y=success_rates,
        text=[f"{rate:.1f}%<br>({att} trips)" for rate, att in zip(success_rates, attempts)],
        textposition='auto',
        marker=dict(
            color=[PLANET_COLORS[i] for i in sorted(planet_stats.keys()) if
                   (len(planet_stats[i]) if isinstance(planet_stats[i], list) else planet_stats[i].get('attempts', 0)) > 0]
        )
    ))

    fig.update_layout(
        title="Success Rate by Planet",
        xaxis_title="Planet",
        yaxis_title="Success Rate (%)",
        yaxis=dict(range=[0, 100]),
        template='plotly_white',
        height=400
    )

    return fig

def create_survival_heatmap(results):
    """Create heatmap showing survival patterns"""
    df = pd.DataFrame(results)

    if 'planet' not in df.columns:
        return None

    # Create bins of 50 steps
    df['step_bin'] = (df['step'] // 50) * 50

    # Calculate success rate per planet per bin
    heatmap_data = df.groupby(['step_bin', 'planet'])['survived'].mean().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='planet', columns='step_bin', values='survived')

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values * 100,
        x=[f"{int(col)}-{int(col)+50}" for col in heatmap_pivot.columns],
        y=[PLANET_NAMES[int(idx)] for idx in heatmap_pivot.index],
        colorscale='RdYlGn',
        text=heatmap_pivot.values * 100,
        texttemplate='%{text:.1f}%',
        textfont={"size": 10},
        colorbar=dict(title="Success Rate (%)")
    ))

    fig.update_layout(
        title="Success Rate Heatmap (50-step bins)",
        xaxis_title="Step Range",
        yaxis_title="Planet",
        template='plotly_white',
        height=300
    )

    return fig

def main():
    # Header
    st.markdown('<div class="main-header">🚀 Morty Express Analytics Dashboard</div>',
                unsafe_allow_html=True)

    # Load all runs
    runs = load_all_runs()

    if not runs:
        st.error("No data files found! Run some experiments first (morty_analyze.py, morty_pattern_runner.py, etc.)")
        return

    # Sidebar
    st.sidebar.title("⚙️ Configuration")

    # Run selection
    st.sidebar.subheader("Select Run")
    run_options = []
    for run in runs:
        run_type = run['type'].capitalize()
        timestamp_str = run['timestamp']
        run_options.append(f"{run_type} - {timestamp_str}")

    selected_run_idx = st.sidebar.selectbox(
        "Choose a run to analyze",
        range(len(run_options)),
        format_func=lambda i: run_options[i]
    )

    selected_run = runs[selected_run_idx]

    # Display run info
    st.sidebar.info(f"""
    **Run Type:** {selected_run['type'].capitalize()}
    **Timestamp:** {selected_run['timestamp']}
    **File:** {selected_run['filename']}
    """)

    # Parse data based on type
    if selected_run['type'] == 'baseline':
        all_results, planet_stats = parse_baseline_data(selected_run['data'])
        st.sidebar.success("Baseline run: All planets tested in isolation")
        pattern_info = None
        final_status = None
    elif selected_run['type'] == 'pattern':
        all_results, planet_stats, pattern, final_status = parse_pattern_data(selected_run['data'])
        pattern_info = pattern
        st.sidebar.success(f"Pattern run: {pattern}")
    else:  # detector
        all_results, planet_stats = parse_detector_data(selected_run['data'])
        st.sidebar.success("Pattern detector: Adaptive strategy")
        pattern_info = None
        final_status = None

    # Summary metrics
    st.subheader("📊 Summary Metrics")

    col1, col2, col3, col4 = st.columns(4)

    total_trips = len(all_results)
    successful_trips = sum(1 for r in all_results if r.get('survived', False))
    success_rate = successful_trips / total_trips * 100 if total_trips > 0 else 0

    if final_status:
        final_saved = final_status.get('morties_on_jessica', all_results[-1].get('morties_on_jessica', 0))
        final_lost = final_status.get('morties_lost', all_results[-1].get('morties_lost', 0))
    else:
        final_saved = all_results[-1].get('morties_on_jessica', 0) if all_results else 0
        final_lost = all_results[-1].get('morties_lost', 0) if all_results else 0

    with col1:
        st.metric("Morties Saved", f"{final_saved}/1000",
                 delta=f"{final_saved/10:.1f}%")

    with col2:
        st.metric("Morties Lost", final_lost,
                 delta=f"{final_lost/10:.1f}%", delta_color="inverse")

    with col3:
        st.metric("Total Trips", total_trips)

    with col4:
        st.metric("Trip Success Rate", f"{success_rate:.1f}%")

    # Main visualizations
    st.subheader("📈 Performance Analysis")

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Success Rate", "🌍 Planet Usage", "🎯 Planet Performance", "🔥 Heatmap"])

    with tab1:
        fig = create_success_rate_over_time(all_results)
        st.plotly_chart(fig, use_container_width=True)

        # Additional insights
        if all_results:
            df = pd.DataFrame(all_results)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**🎯 Best Streak**")
                # Calculate longest winning streak
                max_streak = 0
                current_streak = 0
                for r in all_results:
                    if r.get('survived', False):
                        current_streak += 1
                        max_streak = max(max_streak, current_streak)
                    else:
                        current_streak = 0
                st.info(f"Longest winning streak: **{max_streak}** consecutive successful trips")

            with col2:
                st.markdown("**📉 Worst Streak**")
                max_fail_streak = 0
                current_fail_streak = 0
                for r in all_results:
                    if not r.get('survived', False):
                        current_fail_streak += 1
                        max_fail_streak = max(max_fail_streak, current_fail_streak)
                    else:
                        current_fail_streak = 0
                st.warning(f"Longest losing streak: **{max_fail_streak}** consecutive failed trips")

    with tab2:
        fig = create_planet_usage_chart(all_results)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

            # Planet usage stats
            df = pd.DataFrame(all_results)
            if 'planet' in df.columns:
                st.markdown("**Planet Usage Distribution**")
                usage_counts = df['planet'].value_counts().sort_index()

                cols = st.columns(3)
                for idx, (planet_idx, count) in enumerate(usage_counts.items()):
                    with cols[idx]:
                        pct = count / len(df) * 100
                        st.metric(
                            PLANET_NAMES[planet_idx],
                            f"{count} trips",
                            delta=f"{pct:.1f}%"
                        )
        else:
            st.info("Planet usage data not available for this run type")

    with tab3:
        fig = create_planet_performance_chart(planet_stats)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

            # Detailed planet stats
            st.markdown("**Detailed Planet Statistics**")

            planet_data = []
            for planet_idx in sorted(planet_stats.keys()):
                stats = planet_stats[planet_idx]

                if isinstance(stats, list):
                    planet_attempts = len(stats)
                    successes = sum(1 for r in stats if r.get('survived', False))
                else:
                    planet_attempts = stats.get('attempts', 0)
                    successes = stats.get('successes', 0)

                if planet_attempts > 0:
                    planet_data.append({
                        'Planet': PLANET_NAMES[planet_idx],
                        'Attempts': planet_attempts,
                        'Successes': successes,
                        'Failures': planet_attempts - successes,
                        'Success Rate': f"{successes/planet_attempts*100:.1f}%"
                    })

            if planet_data:
                st.dataframe(pd.DataFrame(planet_data), use_container_width=True)
        else:
            st.info("Planet performance data not available")

    with tab4:
        fig = create_survival_heatmap(all_results)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Shows how success rates change over time for each planet. Darker green = higher success rate.")
        else:
            st.info("Heatmap not available for this run type")

    # Pattern info (if applicable)
    if pattern_info:
        st.subheader("🔄 Pattern Information")
        st.info(f"**Pattern Used:** {pattern_info}")
        st.caption("This run used a predefined repeating pattern to send Morties.")

    # Raw data viewer
    with st.expander("🔍 View Raw Data"):
        st.json(selected_run['data'])

    # Comparison mode
    st.subheader("⚖️ Compare Runs")
    if len(runs) > 1:
        compare_runs = st.multiselect(
            "Select runs to compare",
            range(len(run_options)),
            format_func=lambda i: run_options[i],
            default=[selected_run_idx]
        )

        if len(compare_runs) > 1:
            comparison_data = []

            for idx in compare_runs:
                run = runs[idx]

                if run['type'] == 'baseline':
                    results, _ = parse_baseline_data(run['data'])
                elif run['type'] == 'pattern':
                    results, _, _, final = parse_pattern_data(run['data'])
                else:
                    results, _ = parse_detector_data(run['data'])

                if results:
                    final_saved = results[-1].get('morties_on_jessica', 0)
                    total_trips = len(results)
                    successful_trips = sum(1 for r in results if r.get('survived', False))

                    comparison_data.append({
                        'Run': run_options[idx],
                        'Type': run['type'].capitalize(),
                        'Morties Saved': final_saved,
                        'Success Rate': f"{final_saved/10:.1f}%",
                        'Total Trips': total_trips,
                        'Trip Success Rate': f"{successful_trips/total_trips*100:.1f}%"
                    })

            st.dataframe(pd.DataFrame(comparison_data), use_container_width=True)

            # Comparison chart
            fig = go.Figure()
            for data in comparison_data:
                fig.add_trace(go.Bar(
                    name=data['Run'],
                    x=['Morties Saved', 'Total Trips'],
                    y=[data['Morties Saved'], data['Total Trips']],
                ))

            fig.update_layout(
                title="Run Comparison",
                barmode='group',
                template='plotly_white'
            )

            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run more experiments to enable comparison mode!")

if __name__ == "__main__":
    main()
