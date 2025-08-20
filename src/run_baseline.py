from brian2 import *
import os

os.makedirs("results", exist_ok=True)

# Simulation parameters
duration = 1*second
defaultclock.dt = 0.1*ms

# Common neuron constants
tau = 10*ms
v_rest = -65*mV
v_reset = -65*mV
v_thresh = -50*mV

# Layers
n_input = 10
input_layer = PoissonGroup(n_input, rates=50*Hz)

n_afferent = 10
eqs_aff = '''
dv/dt = (v_rest - v - a)/tau : volt
da/dt = -a/(100*ms) : volt
'''
afferent = NeuronGroup(n_afferent, eqs_aff, threshold='v>v_thresh',
                       reset='v=v_reset; a+=2*mV', method='euler')
afferent.v = v_rest

n_cer = 5
eqs_cer = 'dv/dt = (v_rest - v)/tau : volt'
cerebellar = NeuronGroup(n_cer, eqs_cer, threshold='v>v_thresh',
                         reset='v=v_reset', method='euler')
cerebellar.v = v_rest

# Synapses
syn_in_aff = Synapses(input_layer, afferent, on_pre='v_post += 1.0*mV'); syn_in_aff.connect(j='i')
syn_aff_cer = Synapses(afferent, cerebellar, on_pre='v_post += 1.2*mV'); syn_aff_cer.connect(j='i % n_cer')

# Monitors
M_in = SpikeMonitor(input_layer)
M_aff = SpikeMonitor(afferent)
M_cer = SpikeMonitor(cerebellar)

run(duration)

print("Baseline → Input:", M_in.num_spikes,
      "Afferent:", M_aff.num_spikes,
      "Cerebellar:", M_cer.num_spikes)
