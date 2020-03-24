"""
File to store all simulation parameters of main_corona_SEIR.py
"""
from dataclasses import dataclass

import numpy as np


@dataclass()
class DiseaseParams:
    """
    Disease parameters. Model is VERY sensitive to these, so they must be picked carefully from
    good sources.
    """
    # Beta controls how often a susceptible-infected contact results in a new infection.
    # Source:
    beta_init: float = 1.0 / 2.5  # Intial beta before lockdown
    beta_lock: float = beta_init / 2  # Used after lockdown occurs # TODO Need source

    # Gamma rate an infected recovers and moves into the recovered phase.
    # Source:
    gamma = 1.0 / (10 + 3)

    # The rate at which an exposed person becomes infective.
    # Source:
    sigma = 1.0 / (5 - 3)

    # TODO Check R values
    r0_init = beta_init / gamma
    r1_lock = beta_lock / gamma

    time_hospital: int = 20  # Days in hospital
    time_infected: int = 1.0 / gamma

    lag_communication: int = 1
    lag_testing: int = 5
    lag_symptom_to_hosp: int = 0

    rate_icu: float = 0.02  # Proportion of infected patients who end up in ICU
    rate_fatality_0: float = 0.05  # CFR of patients that 'recover' - either dead or alive
    rate_fatality_1 = rate_fatality_0 * 2  # CFR once ICU beds are saturated  #TODO Need source

    frac_asymptomatic = 0.25  # Fraction of infected that don't show symptoms
    find_ratio = (1 - frac_asymptomatic) / 2  # a lot of the mild cases will go undetected  assuming 100% correct tests


@dataclass
class SimOpts:
    """ Simulation Options"""
    sim_length: int = 200  # In days
    lockdown: bool = False  # If True, a lockdown will be simulated by changing beta
    lockdown_delay: int = 50  # In Days, from start of exposure
    icu_beds: int = 4000  # ICU units available  # Germany: 28000
    # hosp_beds: int = 0  # TODO Use this
    real_data_offset: int = -3  # How many days will the real world country data be delayed in the model
    initial_exposed: int = 1  # Number of initially exposed people
    add_delays: bool = True  # If True, will add delays to found cases, hospitalised, and deaths


@dataclass
class PlotOpts:
    plot_log: bool = True  # If true, plots will have a log y axis

