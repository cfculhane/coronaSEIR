import json
import logging
import pickle
import time
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import scipy.ndimage.interpolation  # shift function
import yaml
from dateutil import parser as dateparser
from tqdm import tqdm

from corona_model import PROJECT_DIR

logger = logging.getLogger(__name__)
logging.getLogger("matplotlib").setLevel(logging.INFO)

SCRIPT_DIR = Path(__file__).parent
CONFIG = yaml.safe_load(SCRIPT_DIR.joinpath("config.yaml").read_text(encoding="utf-8"))
COVID_DATA_CACHETIME = CONFIG["covid_data"]["cache_time"]


class CovidData(object):
    """
    Handles the loading of covid data pulled from Johns Hopkins
    """

    url = 'https://coronavirus-tracker-api.herokuapp.com/all'
    covid_data_pth = Path(PROJECT_DIR, CONFIG["paths"]["covid_data"])
    y_vars = ["confirmed", "deaths", "recovered"]

    def __init__(self):
        if self.covid_data_pth.exists() is False or \
                (self.covid_data_pth.stat().st_mtime < time.time() - COVID_DATA_CACHETIME):
            raw_data = self.get_covid_data()
            self.country_data = self.parse_rawdata(raw_data)
            self.covid_data_pth.write_bytes(pickle.dumps(self.country_data))
            logger.info(f"Covid data successfully written to {self.covid_data_pth}")

        else:
            self.country_data = pickle.loads(self.covid_data_pth.read_bytes())
            logger.info(f"Covid data successfully read from {self.covid_data_pth}")

    def get_covid_data(self, country_code: Optional[str] = None) -> str:
        """
        Gets the latest covid data from Johns Hopkins dataset via  an API:
            https://github.com/ExpDev07/coronavirus-tracker-api
        :param country_code: The ISO (alpha-2 country_code) for the country
        :returns: JSON encoded string of response
        """
        req = requests.get(self.url, params={"country_code": country_code})
        return req.text

    @staticmethod
    def delay(arr: np.ndarray, days: int):
        return scipy.ndimage.interpolation.shift(arr, days, cval=0)

    def parse_rawdata(self, raw_json: str):
        data_raw = json.loads(raw_json)
        country_data = {}  # Country data keyed with country_code
        for y_var in self.y_vars:
            for loc in tqdm(data_raw[y_var]["locations"], desc=f"Parsing {y_var} data"):
                country_code = loc["country_code"]
                province = loc["province"] if loc["province"] != "" else "all"
                new_hist = {}
                for str_date, y_val in loc["history"].items():  # Note USA datetime ordering in source
                    date_obj = dateparser.parse(str_date, dayfirst=False)
                    date_key = str(date_obj.date())
                    new_hist[date_key] = {"date": date_obj, y_var: y_val}
                new_hist = sorted(new_hist.values(), key=lambda k: k["date"])

                if country_data.get(country_code) is None:
                    country_data[country_code] = {}

                if country_data[country_code].get(province) is None:
                    country_data[country_code][province] = pd.DataFrame(new_hist).set_index("date")
                else:
                    country_data[country_code][province][y_var] = [d[y_var] for d in new_hist]

        # Sum totals for countries with provinces
        for country in country_data.values():
            if country.get("all") is None:
                country["all"] = sum([df for df in country.values()])

        return country_data

    def plot_location(self, ax: plt.Axes, country_code: str, province: str = "all", logscale=True):
        chosen_df = self.country_data[country_code][province]
        ax.plot(chosen_df.confirmed, 'b', alpha=0.5, lw=2, label='confirmed')
        ax.plot(chosen_df.deaths, 'y', alpha=0.5, lw=2, label='deaths')
        ax.plot(chosen_df.recovered, 'r--', alpha=0.5, lw=1, label='recovered')
        ax.legend(title=f"COVID-19 data (beta): {country_code} {province}")
        if logscale is True:
            ax.set_yscale("log", nonposy='clip')
        return ax


if __name__ == '__main__':
    covid_data = CovidData()
    fig = plt.figure(figsize=(10, 10), dpi=200)
    ax1 = fig.add_subplot(211)
    covid_data.plot_location(ax1, "AU")

    ax2 = fig.add_subplot(212)
    covid_data.plot_location(ax2, "CN", "Hubei")

    plt.show()
    # # plt.savefig('data.png')
