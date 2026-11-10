import numpy as np
from pathlib import Path
import sys
import json

import xobjects as xo
import xtrack as xt
import xpart as xp
import xobjects as xo
import xcoll as xc

#Parameters
qx = 20.13
qy = 20.18
xi_x = 0.405
xi_y = 0.35

num_particles = 2000
num_turns = 3000
plane = str(sys.argv[2])
print(f'Sweeping plane: {plane}')
start_at_turn= 500
nemitt_x = 2e-6
nemitt_y = 2e-6
coll_gap = float(sys.argv[6])
tidp_ap_tot = 147e-3
block_mvt = 29e-3

total_crab_voltage = 1e6
crab_frequency = 400.787294e6
phase = float(sys.argv[3])
print(f'Crab cavities phase: {phase} deg, {np.radians(phase)} rad')

sweep = 6000
sweep = -abs(sweep) if plane == 'DPpos' else abs(sweep)
sweep_per_turn = sweep/num_turns

#Loading line and environment
line = xt.load(str(sys.argv[1]))
env = line.env

#Installing crab cavities
rotation_angle = float(sys.argv[4]) * np.pi/2
print(f'Crab cavities rotation angle: {rotation_angle} rad')
crab1 = xt.CrabCavity(crab_voltage=0, frequency = crab_frequency, phase=np.radians(phase), rot_s_rad=rotation_angle)
crab2 = xt.CrabCavity(crab_voltage=0, frequency = crab_frequency, phase=np.radians(phase), rot_s_rad=rotation_angle)
env.element_dict['acfcah.61738'] = crab1
env.element_dict['acfcah.61739'] = crab2

#Installing errors
if int(sys.argv[5]) == 1:
    [b1, b2, b3, b4, b5, b6] = [0, 0, 1, 1, 1, 1]
    tte = env.elements.get_table()
    mask_rbends = tte.element_type == 'RBend'
    mask_quads = tte.element_type == 'Quadrupole'
    mask_sextupoles = tte.element_type == 'Sextupole'

    mba = tte.rows[mask_rbends].rows['mba.*'].name
    mbb = tte.rows[mask_rbends].rows['mbb.*'].name
    qf = tte.rows[mask_quads].rows['qf.*'].name
    qd = tte.rows[mask_quads].rows['qd.*'].name
    lsf = tte.rows[mask_sextupoles].rows['lsf.*'].name
    lsd = tte.rows[mask_sextupoles].rows['lsd.*'].name

    for nn in mba:
        env[nn].knl = np.array([b1*0., b2*0., b3*8.92863062376558e-06,   b4*0.,       b5*-1.6271899631371554,  b6*0.])
    for nn in mbb:
        env[nn].knl = np.array([b1*0., b2*0., b3*-2.606543641240525e-05,  b4*0.,       b5*-1.1800693058580867,  b6*0.])
    for nn in qf:
        env[nn].knl = np.array([b1*0., b2*0., b3*0.,        b4*0.025520870077609926,  b5*0.,     b6*-114.8869977018476])
    for nn in qd:
        env[nn].knl = np.array([b1*0., b2*0., b3*0.,        b4*-0.029783873625363777, b5*0.,     b6*-749.9978975055122])

#Optimising tune and chroma
env.vars['qph_setvalue'] = xi_x
env.vars['qpv_setvalue'] = xi_y
opt = line.match(
    method='6d', # <- passed to twiss
    vary=[
        xt.VaryList(['kqf0', 'kqd0'], step=1e-8, tag='quad'),
        xt.VaryList(['qph_setvalue', 'qpv_setvalue'], step=1e-4, tag='sext'),
    ],
    targets = [
        xt.TargetSet(qx=qx, qy=qy, tol=1e-6, tag='tune'),
        xt.TargetSet(dqx=xi_x*qx, dqy=xi_y*qy, tol=1e-2, tag='chrom'),
    ])

# Installing collimators
line.discard_tracker()
tidp = xc.EverestCollimator(length=4.3, material=xc.materials.CarbonFibreCarbon, jaw_L= tidp_ap_tot/2 + block_mvt, jaw_R = -tidp_ap_tot/2 + block_mvt)
tcsm = xc.EverestCollimator(length=1.83, gap=coll_gap, material=xc.materials.CarbonFibreCarbon)
line.xcoll.collimators.install(names=['tidp.11434', 'tcsm.51932'], elements=[tidp, tcsm])

tt = line.get_table()

tw = line.twiss()
line.xcoll.collimators.assign_optics(twiss=tw, nemitt_x=nemitt_x, nemitt_y=nemitt_y)

#Generating particles
part = xp.generate_matched_gaussian_bunch(nemitt_x=nemitt_x,
                                          nemitt_y=nemitt_y,
                                          sigma_z=0.224, num_particles=num_particles, line=line)

print('Ramping crab cavities')
for turn in range(1,101):
    if turn % 10 == 0:
        print(f'  Turn {turn}')
    line['acfcah.61738'].crab_voltage = total_crab_voltage * turn / 100
    # line['acfcah.61739'].crab_voltage = total_crab_voltage * turn / 100
    line.track(part, num_turns=1, with_progress=False)
    
rf_sweep = xc.RFSweep(line)
sweep_per_turn = -abs(sweep_per_turn) if plane == 'DPpos' else abs(sweep_per_turn)
rf_sweep.prepare(sweep_per_turn=sweep_per_turn)
rf_sweep.info()

# Track during RF sweep:
line.discard_tracker()
line.build_tracker(_context=xo.ContextCpu(omp_num_threads='12'))
line.xcoll.scattering.enable()
line.track(particles=part, num_turns=num_turns, time=True, with_progress=5)
line.xcoll.scattering.disable()
print(f"Done sweeping RF in {line.time_last_track:.1f}s.")

ThisLM = xc.LossMap(line = line, line_is_reversed=False, part=part, interpolation=False)
crab_plane = 'H' if rotation_angle == 0 else 'V'
errors_on_str = 'with_errors' if int(sys.argv[5]) == 1 else 'wo_errors'
ThisLM.to_json(f'LM_off_momentum__{plane}_collgap_{coll_gap}_phase_{phase}_crab_plane_{crab_plane}_{errors_on_str}.json')
ThisLM.save_summary(f'summary__off_momentum__{plane}_collgap_{coll_gap}_phase_{phase}_crab_plane_{crab_plane}_{errors_on_str}.out')

# #For testing
# import matplotlib.pyplot as plt
# print('Particle states: ', np.unique(part.state, return_counts=True))
# ThisLM.plot(norm='raw', savefig = 'Test.png')
# mask = part.state > 0
# unique_turns, counts = np.unique(part.at_turn[~mask], return_counts=True)

# fig, ax = plt.subplots(figsize=(8, 6))
# # Plot histogram-like bar chart
# ax.bar(unique_turns, counts, width=1.0, edgecolor='black')
# ax.set_xlabel("Turn number")
# ax.set_ylabel("Number of particles")
# ax.set_title("Particle losses per turn")
# ax.grid(True, linestyle='--', alpha=0.5)
# fig.tight_layout()
# plt.savefig(f'dead_particles_off_momentum__{plane}_phase_{phase}_crab_plane_{'H' if rotation_angle == 0 else 'V'}.png', dpi=300)
# # plt.savefig(f'plots/adt_ramping/scheme1_10000part.png', dpi=300)
# plt.show()
