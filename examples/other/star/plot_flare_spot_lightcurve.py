"""
Plot the lightcurve of a flaring star with spots
================================================

This example plots the lightcurve caused by a
flaring star when it also has spots.
"""

from astropy import units as u
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
import libpypsg

from VSPEC import ObservationModel,PhaseAnalyzer
from VSPEC import params
from VSPEC import config
from VSPEC.params.gcm import vspec_to_pygcm

SEED = 42
libpypsg.docker.set_url_and_run()

# %%
# Initialize the VSPEC run parameters
# -----------------------------------
#
# For this example, we will create the
# parameter objects explicitly. This can also
# be done using a YAML file.

header = params.Header(
    data_path=Path('.vspec/flare_spot_lightcurve'),
    seed=SEED,verbose=1,
    spec_grid = params.VSPECGridParameters(
        max_teff=3400*u.K,min_teff=2900*u.K,
        impl_bin='rust',impl_interp='scipy',fail_on_missing=False
    )
)

star = params.StarParameters(
    psg_star_template='M',
    teff=3300*u.K,
    mass = 0.1*u.M_sun,
    radius=0.15*u.R_sun,
    period = 6*u.day,
    misalignment_dir=0*u.deg,
    misalignment=0*u.deg,
    ld = params.LimbDarkeningParameters.solar(),
    faculae=params.FaculaParameters.none(),
    spots=params.SpotParameters(
        distribution='iso',
        initial_coverage=0.1,
        area_mean=300*config.MSH,
        area_logsigma=0.2,
        teff_umbra=2900*u.K,
        teff_penumbra=3000*u.K,
        equillibrium_coverage=0.1,
        burn_in=0*u.day,
        growth_rate=0/u.day,
        decay_rate=0*config.MSH/u.day,
        initial_area=10*config.MSH
        ),
    flares=params.FlareParameters(
        dist_teff_mean=9000*u.K,
        dist_teff_sigma=500*u.K,
        dist_fwhm_mean=3*u.hr,
        dist_fwhm_logsigma=0.4,
        alpha=-0.829,
        beta=26.87,
        min_energy=1e32*u.erg,
        cluster_size=3
    ),
    granulation=params.GranulationParameters.none(),
    grid_params=(500, 1000),
)

planet = params.PlanetParameters.std(init_phase=180*u.deg,init_substellar_lon=0*u.deg)
system = params.SystemParameters(
    distance=1.3*u.pc,
    inclination=80*u.deg,
    phase_of_periastron=0*u.deg
)
observation = params.ObservationParameters(
    observation_time=10*u.day,
    integration_time=4*u.hr
)
psg_params = params.psgParameters(
    gcm_binning=200,
    phase_binning=1,
    use_molecular_signatures=True,
    use_continuum_stellar=True,
    nmax=0,
    lmax=0,
    continuum=['Rayleigh', 'Refraction', 'CIA_all'],
)
instrument = params.InstrumentParameters.mirecle()

def gcm_getter():
    return vspec_to_pygcm(
        shape=(30,30,30),
        epsilon=7,
        star_teff=3800*u.K,
        r_star=0.2*u.R_sun,
        r_orbit=0.05*u.AU,
        lat_redistribution=0.0,
        p_surf=1*u.bar,
        p_stop=1e-5*u.bar,
        wind_u=0*u.km/u.s,
        wind_v=0*u.km/u.s,
        albedo=0.3,
        emissivity=1.0,
        gamma=1.4,
        molecules={'CO2':1e-4}
    )
gcm = params.gcmParameters(
    gcm_getter=gcm_getter,
    mean_molec_weight=28,
    is_static=True
)
parameters = params.InternalParameters(
    header = header,
    star = star,
    planet = planet,
    system = system,
    obs=observation,
    psg = psg_params,
    inst=instrument,
    gcm = gcm
)

#%%
# Run the simulation
# ------------------
#

model = ObservationModel(params=parameters)
model.build_planet()
model.build_spectra()

# %%
# Load in the data
# ----------------
#
# We can use VSPEC to read in the synthetic
# data we just created.

data = PhaseAnalyzer(model.directories['all_model'])

# %%
# Make the figure
# ---------------
#

time = (data.time - data.time[0]).to_value(u.day)
wl = data.wavelength.to_value(u.um)

emission = (data.thermal/data.total).to_value(u.dimensionless_unscaled)*1e6

variation = (data.star/data.star[:,0,np.newaxis]-1).to_value(u.dimensionless_unscaled)*100

fig,ax = plt.subplots(1,2,figsize=(8,4))

im=ax[0].pcolormesh(time,wl,emission,cmap='cividis')
fig.colorbar(im,ax=ax[0],label='Planet Thermal Emission (ppm)',location='top')
# ax[0].set_title('Planet')

im=ax[1].pcolormesh(time,wl,variation,cmap='cividis')
fig.colorbar(im,ax=ax[1],label='Stellar Variation (%)',location='top')
# ax[1].set_title('Star')

ax[0].set_ylabel('Wavelength (${\\rm \\mu m}$)')
fig.text(0.5,0.02,'Time (days)',ha='center')

