"""Preview: energy shift and intrinsic flux change from SD-750 recalibration.

No measured spectra, detector response, sample-selection or exposure effects.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path(__file__).resolve().parent
STYLE=Path('/home/pbrichetto/spectuls/spectuls/common/plot_style.mplstyle')
A_OLD=13.2e15
B_OLD=1.002
A_NEW=13.2912e15
B_NEW=.9985676
PARAMETERS={'J0':1.09e-13,'gamma0':2.64,'E01_eV':1.24e17,'omega01':.49,
            'gamma1':3.34,'E12_eV':3.9e18,'omega12':.05,'gamma2':2.6}

def reference_spectrum(e):
    p=PARAMETERS
    return (p['J0']*(e/1e17)**(-p['gamma0'])
            *(1+(e/p['E01_eV'])**(1/p['omega01']))**((p['gamma0']-p['gamma1'])*p['omega01'])
            *(1+(e/p['E12_eV'])**(1/p['omega12']))**((p['gamma1']-p['gamma2'])*p['omega12']))

def forward_energy(e_old,a_old=A_OLD,b_old=B_OLD,a_new=A_NEW,b_new=B_NEW):
    return a_new*(np.asarray(e_old)/a_old)**(b_new/b_old)

def transformed_flux(e,reference=reference_spectrum,a_old=A_OLD,b_old=B_OLD,a_new=A_NEW,b_new=B_NEW):
    e=np.asarray(e)
    e_old=a_old*(e/a_new)**(b_old/b_new)
    jacobian=(b_old/b_new)*e_old/e
    return reference(e_old)*jacobian,e_old,jacobian

def checks():
    e=np.logspace(17.2,19.5,51)
    mapped=forward_energy(e,a_new=A_OLD,b_new=B_OLD)
    identity_energy_error=float(np.max(abs(mapped/e-1)))
    identity_flux,_,_=transformed_flux(e,a_new=A_OLD,b_new=B_OLD)
    identity_flux_error=float(np.max(abs(identity_flux/reference_spectrum(e)-1)))
    gamma=3.34;r=1.14
    powerlaw=lambda en:(en/1e17)**(-gamma)
    shifted,_,_=transformed_flux(e,reference=powerlaw,a_new=r*A_OLD,b_new=B_OLD)
    powerlaw_error=float(np.max(abs(shifted/powerlaw(e)-r**(gamma-1))))
    reconstructed_old=A_OLD*(forward_energy(e)/A_NEW)**(B_OLD/B_NEW)
    inverse_error=float(np.max(abs(reconstructed_old/e-1)))
    assert max(identity_energy_error,identity_flux_error,powerlaw_error,inverse_error)<1e-12
    return dict(identity_energy_max_relative_error=identity_energy_error,
                identity_flux_max_relative_error=identity_flux_error,
                constant_scale_factor=r,powerlaw_index=gamma,
                powerlaw_expected_flux_ratio=r**(gamma-1),
                powerlaw_max_ratio_error=powerlaw_error,
                calibration_inverse_max_relative_error=inverse_error)

def main():
    lg=np.linspace(17.2,19.5,700);energy=10**lg
    energy_new=forward_energy(energy)
    energy_shift=100*(energy_new/energy-1)
    flux_new,old_at_fixed_energy,jac=transformed_flux(energy)
    flux_old=reference_spectrum(energy)
    flux_shift=100*(flux_new/flux_old-1)
    pd.DataFrame(dict(log_energy_eV=lg,energy_eV=energy,
        recalibrated_energy_eV=energy_new,energy_shift_percent=energy_shift,
        old_energy_at_fixed_new_energy_eV=old_at_fixed_energy,
        density_jacobian=jac,reference_flux=flux_old,recalibrated_flux=flux_new,
        flux_shift_percent=flux_shift)).to_csv(OUT/'sd750_calibration_energy_flux.csv',index=False)
    plt.style.use(STYLE)
    fig,axes=plt.subplots(1,2,figsize=(13.6,5.6),layout='constrained')
    for ax,y in zip(axes,[energy_shift,flux_shift]):
        ax.plot(lg,y,color='C0',lw=1.7)
        ax.axhline(0,color='.55',lw=.7)
        ax.set_xlim(17.2,19.5)
        ax.set_xticks(np.arange(17.5,19.6,.5))
        ax.grid(False)
    axes[0].set_xlabel(r'$\lg(E_{\mathrm{2021}}/\mathrm{eV})$')
    axes[0].set_ylabel(r'$(E_{\mathrm{2025}}-E_{\mathrm{2021}})/E_{\mathrm{2021}}\;[\%]$')
    axes[0].set_ylim(min(energy_shift)-.1,.12)
    axes[1].set_xlabel(r'$\lg(E/\mathrm{eV})$')
    axes[1].set_ylabel(r'$(J_{\mathrm{2025}}-J_{\mathrm{2021}})/J_{\mathrm{2021}}\;[\%]$')
    axes[1].set_ylim(min(flux_shift)-.15,.18)
    for ext in ['pdf','png']:
        fig.savefig(OUT/f'sd750_calibration_energy_flux.{ext}',dpi=200,bbox_inches='tight',pad_inches=.06)
    plt.close(fig)
    references=[Path('/home/pbrichetto/phd_thesis/PhD_Thesis_Gaby/Chapter_5_Energy_reconstruction.tex'),
                Path('/home/pbrichetto/phd_thesis/PhD_Thesis_Gaby/Chapter_6_SD433_spectrum.tex'),
                Path('/home/pbrichetto/Downloads/Abreu2021_Article_TheEnergySpectrumOfCosmicRaysB.pdf')]
    def sha(p):
        with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
    meta={'scope':'Analytical energy-coordinate transformation of intrinsic spectrum. No detector response, observed points, exposures, sample selection or bad-period effects.',
          'energy_old':{'A_eV':A_OLD,'B':B_OLD},'energy_new':{'A_eV':A_NEW,'B':B_NEW},
          'reference_spectrum':'EPJC2021 Table6 central parameters in Eq11, intrinsic differential flux',
          'reference_spectrum_parameters':PARAMETERS,
          'plot_style':str(STYLE),
          'style_overrides':'None for typography or LaTeX; only figure size/layout adjusted. No plot titles.',
          'left_panel':'At fixed shower size S35: E2025=A2025*(E2021/A2021)^(B2025/B2021). Horizontal axis is old2021 energy.',
          'right_panel':'At fixed numerical energy E: Eold(E)=A2021*(E/A2025)^(B2021/B2025); J2025(E)=J2021(Eold)*B2021/B2025*Eold/E.',
          'thesis_equations':['eq:change_of_variables','eq:calibration_flux_transformation'],
          'chapter5_rounding':'Chapter5 displays13.3PeV and1.00; calculation retains exact nominal13.2912PeV and.9985676.',
          'checks':checks(),'energy_shift_endpoint_percent':[energy_shift[0],energy_shift[-1]],
          'flux_shift_endpoint_percent':[flux_shift[0],flux_shift[-1]],
          'source_sha256':{str(p):sha(p) for p in references if p.exists()}}
    (OUT/'sd750_calibration_energy_flux_metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps(meta,indent=2))
if __name__=='__main__':main()
