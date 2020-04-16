"""
File to store all simulation parameters of main_corona_SEIR.py
"""
from dataclasses import dataclass


@dataclass()
class DiseaseParams:
    """
    Disease parameters. Model is VERY sensitive to these, so they must be picked carefully from
    good sources.
    """
    # Beta controls how often a susceptible-infected contact results in a new infection.
    # Source:
    beta_init: float = 1.0 / 2.5  # Intial beta before lockdown
    beta_lock: float = beta_init * 0.5  # Used after lockdown occurs # TODO Need source

    # Gamma rate an infected recovers and moves into the recovered phase.
    # Source:
    gamma: float = 1.0 / (10 + 3)

    # The rate at which an exposed person becomes infective.
    # Source:
    sigma: float = 1.0 / (5 - 3)

    # TODO Check R values
    r0_init: float = beta_init / gamma
    r1_lock: float = beta_lock / gamma

    time_hospital: int = 10  # Days in hospital, after which patient either recovers or dies
    time_infected: int = 1.0 / gamma

    lag_communication: int = 0
    lag_testing: int = 2
    lag_symptom_to_hosp: int = 1

    rate_icu: float = 0.02  # Proportion of infected patients who end up in ICU
    rate_fatality_0: float = 0.008  # CFR of patients that 'recover' - either dead or alive
    rate_fatality_1: float = rate_fatality_0 * 2  # CFR once ICU beds are saturated  #TODO Need source

    frac_asymptomatic: float = 0.5  # Fraction of infected that don't show symptoms
    find_ratio: float = (1 - frac_asymptomatic)  # Proportion of infected which are found


@dataclass
class SimOpts:
    """ Simulation Options"""
    sim_length: int = 200  # In days
    lockdown: bool = True  # If True, a lockdown will be simulated by changing beta
    lockdown_delay: int = 25  # In Days, from start of exposure
    icu_beds: int = 4000  # ICU units available
    # hosp_beds: int = 0  # TODO Use this
    real_data_offset: int = 19  # How many days will the real world country data be delayed in the model
    initial_exposed: int = 1  # Number of initially exposed people
    add_delays: bool = True  # If True, will add delays to found cases, hospitalised, and deaths based on lags in DiseaseParams


@dataclass
class PlotOpts:
    plot_log: bool = True  # If true, plots will have a log y axis
