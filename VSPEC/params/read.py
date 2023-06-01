"""
Module to read parameters
"""
from pathlib import Path
import yaml
from astropy import units as u

from VSPEC.params.base import BaseParameters
from VSPEC.params.stellar import StarParameters
from VSPEC.params.planet import PlanetParameters,SystemParameters
from VSPEC.params.gcm import gcmParameters,psgParameters
from VSPEC.params.observation import InstrumentParameters, ObservationParameters

class Header(BaseParameters):
    """
    Header for VSPEC simulation

    Parameters:
    -----------
    data_path : pathlib.Path
        The path to store run data.
    max_teff : astropy.units.Quantity
        The maximum Teff to bin.
    min_teff : astropy.units.Quantity
        The minimum Teff to bin.
    seed : int, default=None
        The seed for the random number generator.
    desc : str, default=None
        A description of the run.
    
    Attributes:
    -----------
    data_path : pathlib.Path
        The path to store run data.
    max_teff : astropy.units.Quantity
        The maximum Teff to bin.
    min_teff : astropy.units.Quantity
        The minimum Teff to bin.
    seed : int or None
        The seed for the random number generator.
    desc : str or None
        A description of the run.

    """
    def __init__(
        self,
        data_path:Path,
        teff_min:u.Quantity,
        teff_max:u.Quantity,
        seed: int,
        desc:str=None
    ):
        self.data_path = data_path
        self.teff_min = teff_min
        self.teff_max = teff_max
        self.seed = seed
        self.desc = desc
    @classmethod
    def _from_dict(cls, d: dict):
        return cls(
            data_path = Path(d['data_path']),
            teff_min = u.Quantity(d['teff_min']),
            teff_max = u.Quantity(d['teff_max']),
            seed = None if d.get('seed',None) is None else int(d.get('seed',None)),
            desc = None if d.get('desc',None) is None else str(d.get('desc',None))
        )


class Parameters(BaseParameters):
    """
    Class to store parameters for a VSPEC simulation.

    Parameters:
    -----------
    header : Header
        The VSPEC simulation header.
    star : StarParameters
        The parameters related to the star.
    planet : PlanetParameters
        The parameters related to the planet.
    system : SystemParameters
        The parameters related to the system.
    obs : ObservationParameters
        The parameters related to the observation.
    psg : psgParameters
        The PSG parameters.
    inst : InstrumentParameters
        The instrument parameters.
    gcm : gcmParameters
        The GCM parameters.

    Attributes:
    -----------
    header : Header
        The VSPEC simulation header.
    star : StarParameters
        The parameters related to the star.
    planet : PlanetParameters
        The parameters related to the planet.
    system : SystemParameters
        The parameters related to the system.
    obs : ObservationParameters
        The parameters related to the observation.
    psg : psgParameters
        The PSG parameters.
    inst : InstrumentParameters
        The instrument parameters.
    gcm : gcmParameters
        The GCM parameters.
    
    Class Methods:
    --------------
    from_yaml(cls, path: Path)
        Create a `Parameters` instance from a YAML file.


    """

    def __init__(
        self,
        header:Header,
        star:StarParameters,
        planet:PlanetParameters,
        system:SystemParameters,
        obs:ObservationParameters,
        psg:psgParameters,
        inst:InstrumentParameters,
        gcm:gcmParameters
    ):
        self.header = header
        self.star = star
        self.planet = planet
        self.system = system
        self.obs = obs
        self.psg = psg
        self.inst = inst
        self.gcm = gcm
    @classmethod
    def _from_dict(cls, d: dict):
        return cls(
            header = Header.from_dict(d['header']),
            star = StarParameters.from_dict(d['star']),
            planet = PlanetParameters.from_dict(d['planet']),
            system = SystemParameters.from_dict(d['system']),
            obs = ObservationParameters.from_dict(d['obs']),
            psg = psgParameters.from_dict(d['psg']),
            inst = InstrumentParameters.from_dict(d['inst']),
            gcm = gcmParameters.from_dict(d)
        )
    @classmethod
    def from_yaml(cls, path: Path) -> 'Parameters':
        """
        Create a `Parameters` instance from a YAML file.

        Parameters:
        -----------
        path : Path
            The path to the YAML file.

        Returns:
        --------
        Parameters
            An instance of the `Parameters` class.

        """
        with open(path, 'r',encoding='UTF-8') as file:
            data = yaml.safe_load(file)
        return cls.from_dict(data)
    def to_psg(self)->dict:
        config = {
            'GENERATOR-NOISEFRAMES': str(int(round(
                (self.obs.integration_time/self.inst.detector.integration_time).to_value(u.dimensionless_unscaled)
            )))
        }
        config.update(self.star.to_psg())
        config.update(self.planet.to_psg())
        config.update(self.system.to_psg())
        config.update(self.psg.to_psg())
        config.update(self.inst.to_psg())
        return config
    @property
    def flux_correction(self)->float:
        """
        Correction for the solid angle of the star.
        """
        return (self.star.radius/self.system.distance).to_value(u.dimensionless_unscaled)**2
    @property
    def star_total_images(self)->int:
        """
        The total number of epochs to simulate the star.
        """
        return self.obs.total_images
    @property
    def planet_total_images(self)->int:
        """
        The total number of epochs to simulate the planet.
        """
        return self.obs.total_images // self.psg.phase_binning
    