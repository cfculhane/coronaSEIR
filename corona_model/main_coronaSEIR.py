import logging
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Tuple
import dataclasses
import matplotlib.pyplot as plt
import matplotlib.widgets  # Cursor
import numpy as np
import pandas as pd
import pprintpp
import scipy.integrate
import scipy.ndimage.interpolation

from corona_model import PROJECT_DIR, log_pth
from corona_model.countryinfo import CountryInfo
from corona_model.params import DiseaseParams, SimOpts, PlotOpts
from corona_model.world_data import CovidData

logger = logging.getLogger(__name__)
logging.getLogger("matplotlib").setLevel(logging.INFO)


@dataclass
class SimResults:
    """ Class to store results"""
    T: np.ndarray  # Time-step (days), vector variable of ODEs
    S: np.ndarray  # Susceptible at each timestep
    E: np.ndarray  # Exposed at each timestep
    I: np.ndarray  # Infected at each timestep
    R: np.ndarray  # Recovered at each timestep
    D: np.ndarray = np.zeros(0)  # Deaths at each timestep
    F: np.ndarray = np.zeros(0)  # Found at each timestep
    H: np.ndarray = np.zeros(0)  # Hospitalised at each timestep
    P: np.ndarray = np.zeros(0)  # Probability of random person being infected at each timestep


class SEIRModel(object):
    """ A SEIR model of the COVID-19 including ICU Saturation and testing delays."""

    def __init__(self, country_name: str):
        """
        :param country_name: Full name of country, e.g. "Australia"
        """
        self.country = CountryInfo(country_name)
        self.n_pop = self.country.population()

    def model_seir(self, t: float, state: Iterable[np.ndarray], d_params: DiseaseParams,
                   s_opts: SimOpts) -> Tuple[float, float, float, float]:
        """
        Definition of SEIR model
        :param t: Time-step (days), dependant variable of ODEs
        :param state: Vector of ODE State variables [S, E, I, R]
        :param d_params: DiseaseParams dataclass from params, or your own/modified version
        :param s_opts: SimOpts dataclass from params, or your own/modified version
        :returns: 4-element tuple of change in each of the state variables
        """
        N = self.n_pop  # Population of country
        S, E, I, R = state

        if s_opts.lockdown is True:
            beta = d_params.beta_init if t <= s_opts.lockdown_delay else d_params.beta_lock
        else:
            beta = d_params.beta_init

        sigma = d_params.sigma
        gamma = d_params.gamma

        dS = - beta * S * I / N
        dE = beta * S * I / N - sigma * E
        dI = sigma * E - gamma * I
        dR = gamma * I
        return dS, dE, dI, dR

    def run_model(self, d_params: DiseaseParams, s_opts: SimOpts) -> SimResults:
        """
        Solves the ODE model and returns results.
        :param d_params: d_params: DiseaseParams dataclass from params, or your own/modified version
        :param s_opts: s_opts: SimOpts dataclass from params, or your own/modified version
        :returns: 5-element Tuple of arrays of results
        """
        T = np.arange(s_opts.sim_length)  # time-step Array
        Y0 = [self.n_pop - s_opts.initial_exposed, s_opts.initial_exposed, 0, 0]  # S, E, I, R at initial step

        logger.info(f"Starting run of model...")
        logger.info(f"DiseaseParams : {pprintpp.pformat(dataclasses.asdict(disease_params))}")
        logger.info(f"SimOpts : {pprintpp.pformat(dataclasses.asdict(sim_opts))}")
        logger.info(f"Initial conditions (S E I R): {Y0}")

        Y_RESULTS = scipy.integrate.solve_ivp(self.model_seir, t_span=[T[0], T[-1]],
                                              y0=Y0, args=(d_params, s_opts),
                                              t_eval=T)

        S, E, I, R = Y_RESULTS.y  # transpose and unpack

        logger.info(f"Solve complete!")
        raw_results = SimResults(T=T, S=S, E=E, I=I, R=R)
        parsed_results = self._parse_results(raw_results, d_params, s_opts)
        logger.info(f"Results successfully parsed.")
        return parsed_results

    def _parse_results(self, res: SimResults, d_params: DiseaseParams, s_opts: SimOpts) -> SimResults:
        """
        Parses the results created in run_model()
        :param res: SimResults from a model run
        :param d_params: d_params: DiseaseParams dataclass from params, or your own/modified version
        :param s_opts: s_opts: SimOpts dataclass from params, or your own/modified version
        :returns:
        """
        T, S, E, I, R = res.T, res.S, res.E, res.I, res.R
        F = I * d_params.find_ratio
        H = I * d_params.rate_icu * d_params.time_hospital / d_params.time_hospital
        P = I / self.n_pop * 1000000  # Probability of random person to be infected

        # estimate deaths from recovered
        D = np.arange(s_opts.sim_length)
        RPrev = 0
        DPrev = 0
        for i, t in enumerate(res.T):
            IFR = d_params.rate_fatality_0 if H[i] <= s_opts.icu_beds else d_params.rate_fatality_1
            D[i] = DPrev + IFR * (R[i] - RPrev)
            RPrev = R[i]
            DPrev = D[i]

        if s_opts.add_delays is True:
            F = self.delay(F, d_params.lag_symptom_to_hosp + d_params.lag_testing + d_params.lag_communication)
            H = self.delay(H, d_params.lag_symptom_to_hosp)  # ICU  from I
            D = self.delay(D, d_params.time_hospital + d_params.lag_communication)  # deaths  from R

        # Update result object
        res.P = P
        res.F = F
        res.H = P
        res.D = D

        return res

    @staticmethod
    def delay(arr: np.ndarray, days: int):
        return scipy.ndimage.interpolation.shift(arr, days, cval=0)


class ResultAnalyser(object):
    """ Handles the analysing of the results. to add more results just add more functions and call them in .run()"""
    output_dir = PROJECT_DIR.joinpath("outputs")

    def __init__(self, results: SimResults, p_opts: PlotOpts, date_range: pd.DatetimeIndex, n_pop: int,
                 s_opts: SimOpts, country_data):
        self.results = results
        self.p_opts = p_opts
        self.date_range = date_range
        self.n_pop = n_pop
        self.s_opts = s_opts
        self.country_data = country_data

    def run(self):
        """ Runs analyses"""
        logger.info(f"Predicted Starting values:")
        self.print_info(0, self.results)
        logger.info(f"Predicted Ending values:")
        self.print_info(self.results.T[-1], self.results)
        logger.info(f"Predicted Values now:")
        timestep_now = np.where(self.date_range <= pd.Timestamp.now())[0][-1]
        self.print_info(timestep_now, self.results)
        logger.info(f"REAL Confirmed: {self.country_data['all'].confirmed[-1]}")
        logger.info(f"REAL Deaths: {self.country_data['all'].deaths[-1]}")

        date_iculimit = self.icu_results()
        self.plot(self.results, self.date_range, date_iculimit)

        # Copy log file
        shutil.copy2(Path(log_pth), self.output_dir.joinpath(Path(log_pth).name))

    def print_info(self, t: int, res: SimResults):
        logger.info("-" * 50)
        logger.info(f"Day {t} | Date: {self.date_range[t]}")
        logger.info(f"Infected: {int(res.I[t])}, {self.per_pop(res.I[t])} %")
        logger.info(f"Found in testing: {int(res.F[t])}, {self.per_pop(res.F[t])} %")
        logger.info(f"In ICU: {int(res.H[t])}, {self.per_pop(res.H[t])} %")
        logger.info(f"Recovered: {int(res.R[t])}, {self.per_pop(res.R[t])} %")
        logger.info(f"Deaths: {int(res.D[t])}, {self.per_pop(res.D[t])} %")
        logger.info("-" * 50)

    def per_pop(self, var):
        return round((100 * var / self.n_pop), 4)

    def icu_results(self):
        icu_limit = self.s_opts.icu_beds
        try:
            tstep_iculimit = np.where(self.results.H >= icu_limit)[0][0]
            date_iculimit = self.date_range[tstep_iculimit]
            logger.info(f"Date when ICU limit hit: {date_iculimit.date()}")
            logger.info(f"ICU limit hit in: {(date_iculimit - datetime.now()).days}")
        except IndexError:
            logger.info(f"ICU Limit never reached. \n Maximum Hospitalised = {max(self.results.H)}")
            date_iculimit = None
        return date_iculimit

    def plot(self, results: SimResults, date_range, date_iculimit):
        fig = plt.figure(dpi=75, figsize=(20, 16))
        ax = fig.add_subplot(111)
        if plot_opts.plot_log:
            ax.set_yscale("log", nonposy='clip')

        # ax.plot(date_range, results.S, 'b', alpha=0.5, lw=2, label='Susceptible')
        # ax.plot(date_range, results.E, 'y', alpha=0.5, lw=2, label='Exposed')
        ax.plot(date_range, results.I, 'r--', alpha=0.5, lw=1, label='Infected')
        ax.plot(date_range, results.F, color='purple', alpha=0.5, lw=2, label='Number detected in testing')
        ax.plot(date_range, results.H, 'r', alpha=0.5, lw=2, label='Number in ICU')
        # ax.plot(X, R, 'g', alpha=0.5, lw=1, label='Recovered with immunity')
        ax.plot(date_range, results.P, 'c', alpha=0.5, lw=1, label='Probability of infection')
        ax.plot(date_range, results.D, 'k', alpha=0.5, lw=1, label='Deaths')

        ax.plot([min(date_range), max(date_range)], [sim_opts.icu_beds, sim_opts.icu_beds], 'r-.', alpha=1, lw=1,
                label='Number of ICU available')
        ax.plot([datetime.now(), datetime.now()], [min(results.I), max(results.I)],
                '-', alpha=0.5, lw=2, label='TODAY')

        if date_iculimit is not None:
            ax.plot([date_iculimit, date_iculimit], [min(results.I), max(results.I)],
                    'r-', alpha=0.5, lw=2, label=f'ICU LIMIT REACHED ({date_iculimit.date()})')

        if self.s_opts.lockdown is True:
            lockdown_date = date_range[self.s_opts.lockdown_delay].to_pydatetime().date()
            logger.info(f"Lockdown date: {lockdown_date}")
            ax.plot([lockdown_date, lockdown_date], [min(results.I), max(results.I)],
                    'b-.', alpha=0.5, lw=1, label=f'Lockdown Starts ({lockdown_date})')

        # Real data
        ax.plot(country_data["all"].confirmed, 'o', color='orange', alpha=0.5, lw=1,
                label='Confirmed Cases')
        ax.plot(country_data["all"].deaths, 'x', color='black', alpha=0.5, lw=1,
                label='Deceased cases')

        ax.set_xlabel('Time (days)')
        ax.set_ylabel('Number')
        ax.set_ylim(bottom=1.0)

        ax.grid(linestyle=':')
        legend = ax.legend(title=f"COVID-19 SEIR model: {COUNTRY}, population: {round(model.n_pop / 1E6)} million \n"
                                 f"Model is for beta use only!")
        legend.get_frame().set_alpha(0.5)
        for spine in ('top', 'right', 'bottom', 'left'):
            ax.spines[spine].set_visible(False)
        cursor = matplotlib.widgets.Cursor(ax, color='black', linewidth=1)
        plt.show()
        fig.savefig(Path(self.output_dir, f"model_run_{datetime.now().date()}.png"))


if __name__ == '__main__':
    # Load in options and parameters
    COUNTRY = "Australia"
    country_info = CountryInfo(COUNTRY)
    disease_params = DiseaseParams()
    sim_opts = SimOpts()
    plot_opts = PlotOpts()

    # Over-ride any options here on the fly, check params.py for all parameters!
    sim_opts.sim_length = 100
    sim_opts.real_data_offset = 16  # How many days will the real world country data be delayed in the model

    sim_opts.add_delays = True  # If True, will add delays to found cases, hospitalised, and deaths based on lags in DiseaseParams
    sim_opts.lockdown = True  # If True, a lockdown will be simulated by changing beta
    sim_opts.lockdown_delay = 46  # In Days, from start of exposure
    disease_params.beta_lock = 0.25 * disease_params.beta_init
    plot_opts.plot_log = True  # If true, plots will have a log y axis

    # Get real data and shift if required
    covid_data = CovidData()
    country_data = covid_data.world_data[country_info.iso(2)]

    # Run model
    model = SEIRModel("Australia")
    results = model.run_model(disease_params, sim_opts)

    # Analyse
    start_date = country_data["all"].index[0] + pd.Timedelta(days=sim_opts.real_data_offset)
    date_range = pd.date_range(start_date, periods=len(results.T), freq="D")

    analyser = ResultAnalyser(results, plot_opts, date_range, n_pop=model.n_pop, s_opts=sim_opts,
                              country_data=country_data)
    analyser.run()
