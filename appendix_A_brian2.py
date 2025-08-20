# Appendix A – Brian2 Python code for vestibular dysfunction and adaptation modeling
# Save as: appendix_A_brian2.py
#
# Usage:
#   python appendix_A_brian2.py --mode baseline
#   python appendix_A_brian2.py --mode hypofunction
#   python appendix_A_brian2.py --mode afferent_silencing
#   python appendix_A_brian2.py --mode synaptic_blockade
#
# Requirements: brian2, numpy (see requirements.txt)

from brian2 import *
import argparse

def run_sim(mode: str = "baseline",
            duration_s: float = 1.0,
            dt_ms: float = 0.1,
            n_input: int = 10,
            n_afferent: int = 10,
            n_cerebellar: int = 5,
            input_rate_hz: float = 50.0,
            w_in_aff_mV: float = 1.0,
            w_aff_cer_mV: float = 1.2):
    """
    Build and run the 3-layer vestibular SNN for a selected scenario.

    Parameters
    ----------
    mode : {"baseline","hypofunction","afferent_silencing","synaptic_blockade"}
        Scenario to simulate.
    duration_s : float
        Simulation duration in seconds.
    dt_ms : float
        Integration time step in milliseconds.
    n_input, n_afferent, n_cerebellar : int
        Population sizes.
    input_rate_hz : float
        Baseline Poisson rate for hair cells (overridden in hypofunction).
    w_in_aff_mV, w_aff_cer_mV : float
        Synaptic increments (in mV) on pre-synaptic spikes.
    """

    # Simulation timing
    duration = duration_s * second
    defaultclock.dt = dt_ms * ms

    # Neuron constants
    tau = 10 * ms
    v_rest = -65 * mV
    v_reset = -65 * mV
    v_thresh = -50 * mV

    # ---- Scenario-specific adjustments ----
    if mode == "baseline":
        rate_hz = input_rate_hz
        w_in_aff = w_in_aff_mV * mV
        w_aff_cer = w_aff_cer_mV * mV

    elif mode == "hypofunction":
        # Reduced peripheral drive
        rate_hz = 15.0
        w_in_aff = w_in_aff_mV * mV
        w_aff_cer = w_aff_cer_mV * mV

    elif mode == "afferent_silencing":
        rate_hz = input_rate_hz
        # Cut input→afferent effective drive
        w_in_aff = 0.0 * mV
        w_aff_cer = w_aff_cer_mV * mV

    elif mode == "synaptic_blockade":
        rate_hz = input_rate_hz
        w_in_aff = w_in_aff_mV * mV
        # Cut afferent→cerebellar effective drive
        w_aff_cer = 0.0 * mV

    else:
        raise ValueError(f"Unknown mode: {mode}")

    # ---- Layers ----
    # Hair Cell Layer (Poisson input)
    input_layer = PoissonGroup(n_input, rates=rate_hz * Hz)

    # Afferent Layer (LIF with adaptation)
    eqs_afferent = '''
    dv/dt = (v_rest - v - a)/tau : volt
    da/dt = -a/(100*ms) : volt
    '''
    afferent_layer = NeuronGroup(
        n_afferent, eqs_afferent,
        threshold='v > v_thresh',
        reset='v = v_reset; a += 2*mV',
        method='euler'
    )
    afferent_layer.v = v_rest

    # Cerebellar Layer (simple integrators)
    eqs_cerebellar = 'dv/dt = (v_rest - v)/tau : volt'
    cerebellar_layer = NeuronGroup(
        n_cerebellar, eqs_cerebellar,
        threshold='v > v_thresh',
        reset='v = v_reset',
        method='euler'
    )
    cerebellar_layer.v = v_rest

    # ---- Synapses ----
    syn_input_afferent = Synapses(input_layer, afferent_layer, on_pre='v_post += w_in_aff')
    syn_input_afferent.connect(j='i')  # one-to-one mapping

    syn_afferent_cerebellar = Synapses(afferent_layer, cerebellar_layer, on_pre='v_post += w_aff_cer')
    syn_afferent_cerebellar.connect(j='i % n_cerebellar')  # round-robin fan-in

    # ---- Monitors ----
    spikemon_input = SpikeMonitor(input_layer)
    spikemon_afferent = SpikeMonitor(afferent_layer)
    spikemon_cerebellar = SpikeMonitor(cerebellar_layer)

    # Optional: record voltages if you need traces
    # statemon_cerebellar = StateMonitor(cerebellar_layer, 'v', record=True)

    # ---- Run ----
    run(duration)

    # ---- Report ----
    print(f"Scenario: {mode}")
    print("Input spikes     :", spikemon_input.num_spikes)
    print("Afferent spikes  :", spikemon_afferent.num_spikes)
    print("Cerebellar spikes:", spikemon_cerebellar.num_spikes)

    # Return monitors if you want to post-process or plot
    return {
        "input": spikemon_input,
        "afferent": spikemon_afferent,
        "cerebellar": spikemon_cerebellar,
        # "statemon_cerebellar": statemon_cerebellar,
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vestibular SNN (Brian2) – Appendix A")
    parser.add_argument(
        "--mode",
        type=str,
        default="baseline",
        choices=["baseline", "hypofunction", "afferent_silencing", "synaptic_blockade"],
        help="Select simulation scenario"
    )
    parser.add_argument("--duration", type=float, default=1.0, help="Simulation duration (seconds)")
    args = parser.parse_args()

    run_sim(mode=args.mode, duration_s=args.duration)
