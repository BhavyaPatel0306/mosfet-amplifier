"""Reproduce baseline and experimental runs. Requires NumPy and shared ngspice.

Runs complete on circuit-analysis success, not on specification compliance.
The original schematic is not modified. AC normalization is logged explicitly.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import tempfile
import numpy as np
from ngspice_shared import Engine

ROOT = Path(__file__).resolve().parents[1]
OUT = 'net-_c6-pad1_'


def harmonics(t, voltage):
    # Uniform interpolation avoids adaptive-step weighting in harmonic fitting.
    grid = np.linspace(t[0], t[-1], 2000, endpoint=False)
    voltage = np.interp(grid, t, voltage)
    columns = [np.ones(len(grid))]
    for k in range(1, 11):
        columns.extend([np.sin(2*np.pi*100000*k*grid), np.cos(2*np.pi*100000*k*grid)])
    coefficients = np.linalg.lstsq(np.column_stack(columns), voltage, rcond=None)[0]
    amplitudes = np.hypot(coefficients[1::2], coefficients[2::2])
    return float(100*np.linalg.norm(amplitudes[1:])/amplitudes[0])


def window(t, v, end):
    grid = np.linspace(end-0.0001, end, 2001)
    values = np.interp(grid, t, v)
    return grid, values


def ac_metrics(f, out):
    db = 20*np.log10(np.abs(out))
    reference = float(np.interp(np.log10(1e5), np.log10(f), db))
    indices = np.where((f > 1e5) & (db <= reference-3))[0]
    cutoff = None
    if len(indices):
        i = int(indices[0])
        cutoff = float(10**np.interp(reference-3, db[i:i-2:-1], np.log10(f[i:i-2:-1])))
    return {'gain_100khz_db': reference, 'upper_3db_hz': cutoff}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', help='Path to ngspice DLL/shared library')
    parser.add_argument('--output', type=Path, default=ROOT/'simulations/results')
    parser.add_argument('--stop-ms', type=float, default=80)
    parser.add_argument('--max-step-ns', type=float, default=200)
    args = parser.parse_args()
    if args.stop_ms < 25 or args.max_step_ns <= 0:
        parser.error('Use stop-ms >= 25 and a positive max-step-ns.')
    args.output.mkdir(parents=True, exist_ok=True)
    engine = Engine(args.library)
    metadata = {'python': platform.python_version(), 'numpy': np.__version__,
                'unloaded_definition': 'R10 replaced by 1 Tohm DC reference; all capacitors retained. AC gain referenced to 100 kHz.',
                'temperature_c': 27, 'ngspice_compatibility': 'ps',
                'transient_stop_ms': args.stop_ms, 'max_step_ns': args.max_step_ns,
                'thd_definition': 'Harmonics 2-10 / fundamental, least squares at 100 kHz; percent',
                'results': {}}
    with tempfile.TemporaryDirectory(prefix='mosfet-') as temporary:
        working = Path(temporary)/'run.cir'
        def load(text):
            model = (ROOT/'hardware/models/nmos_t.txt').as_posix()
            text = re.sub(r'(?m)^\.include .*$', f'.include "{model}"', text)
            text = text.replace('.end', '.options temp=27 reltol=1e-4\n.end')
            working.write_text(text, encoding='utf-8')
            engine.load(working)
        for name in ['baseline', 'candidate']:
            source = ROOT/'simulations/netlists'/f'{name}.cir'
            text = source.read_text(encoding='utf-8')
            results = {'netlist_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
            load(text)
            engine.command('op')
            results['supply_current_a'] = float(-engine.vector('v1#branch')[0])
            results['dc_power_w'] = 3.3*results['supply_current_a']
            results['devices'] = {}
            for q in ['q1','q2','q3','q4']:
                device = {p: float(engine.vector(f'@m.x{q}.m0[{p}]')[0])
                          for p in ['id','vgs','vds','vth','vdsat','gm']}
                device['vgs_minus_vth_v'] = device['vgs']-device['vth']
                results['devices'][q] = device
            if name == 'baseline':
                engine.command('ac dec 10 1k 1Meg')
                results['as_saved_ac_output_max_v'] = float(np.max(np.abs(engine.vector(OUT))))
                text = text.replace(' AC 0', ' AC 1')
                results['ac_override'] = 'V2 AC magnitude changed from 0 to 1 for transfer-function measurement only'
            ac = {}
            for loadname in ['loaded','unloaded']:
                # Keep an effectively open 1 Tohm DC path at the AC-coupled output.
                # Removing R10 completely leaves the baseline output node floating.
                test = text if loadname == 'loaded' else re.sub(r'(?m)^(R10 \S+ \S+) \S+', r'\g<1> 1T', text)
                load(test)
                engine.command('ac dec 200 1 100Meg')
                frequency = engine.vector('frequency').real
                output = engine.vector(OUT)
                ac[loadname] = ac_metrics(frequency, output)
                np.savetxt(args.output/f'{name}-ac-{loadname}.csv',
                           np.column_stack([frequency,output.real,output.imag]),delimiter=',',
                           header='frequency_hz,vout_real_v,vout_imag_v',comments='',fmt='%.10g')
            results['ac'] = ac
            results['load_reduction_percent'] = 100*(1-10**((ac['loaded']['gain_100khz_db']-ac['unloaded']['gain_100khz_db'])/20))
            load(text)
            engine.command('save all @m.xq3.m0[id]')
            stop = args.stop_ms/1000
            start = stop-0.0201
            step = args.max_step_ns*1e-9
            engine.command(f'tran {step:.12g} {stop:.12g} {start:.12g} {step:.12g}')
            times = engine.vector('time')
            values = engine.vector(OUT)
            grid, final = window(times,values,stop)
            previous_grid, previous = window(times,values,stop-0.02)
            follower_current = np.interp(grid,times,engine.vector('@m.xq3.m0[id]'))
            results['transient'] = {'input_peak_v': 0.001 if name=='baseline' else 0.00075,
                'output_min_v': float(final.min()), 'output_max_v': float(final.max()),
                'output_vpp':float(np.ptp(final)), 'thd_percent':harmonics(grid,final),
                'previous_window_vpp':float(np.ptp(previous)),
                'previous_window_thd_percent':harmonics(previous_grid,previous),
                'vpp_window_change_percent':float(100*(np.ptp(final)/np.ptp(previous)-1)),
                'follower_peak_current_a':float(follower_current.max()),
                'follower_min_current_a':float(follower_current.min())}
            np.savetxt(args.output/f'{name}-transient.csv',np.column_stack([grid,final,follower_current]),
                       delimiter=',',header='time_s,vout_v,follower_id_a',comments='',fmt='%.10g')
            metadata['results'][name] = results
            print(name, json.dumps(results), flush=True)
        messages = '\n'.join(engine.messages)
        metadata['engine_banner'] = [m for m in engine.messages if 'ngspice-' in m or 'Creation Date' in m]
        metadata['source_hashes'] = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
            ['hardware/ELE404Project.kicad_sch','hardware/models/nmos_t.txt','scripts/run_simulations.py','scripts/ngspice_shared.py']}
        (args.output/'run.log').write_text(messages.replace(str(ROOT).replace('\\','/'),'<REPO>').replace(str(Path(temporary)).replace('\\','/'),'<RUN>'),encoding='utf-8')
        (args.output/'summary.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print('Runs completed. Check summary.json for failures against design targets; completion is not a compliance pass.')


if __name__ == '__main__':
    main()
