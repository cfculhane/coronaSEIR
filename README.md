# coronavirus SEIR model

An SEIR model of the COVID-19 pandemic. Heavily based off a fork of [coronafighters work here](https://github.com/coronafighter/coronaSEIR)
  
## Disclaimer
This is not a scientific or medical tool. Use at your own risk. 

## Features
* SEIR epidemic model
* Reduced R0 after a certain amount of days to account for containment measures.
* Delays to allow for lagging official data etc.
* Real world data automatically updated every three hours from Johns Hopkins CSSE (https://github.com/CSSEGISandData/2019-nCoV) via  https://github.com/ExpDev07/coronavirus-tracker-api
* country population data (https://github.com/samayo/country-json)
* check out screenshots below

## Installation / Requirements / Documentation
Needs Python 3.x installed. 
  
```
$ pip3 install --upgrade numpy scipy matplotlib python-dateutil  # might need sudo -H pip3 ...
$ python3 ./corona_model/main_coronaSEIR.py
read data: 843103 bytes
r0: 5.20    r1: 1.30
doubling0 every ~3.4 days
day 60
 Infected: 119363 0.2
 Infected found: 1085 0.0
 Hospital: 787 0.0
 Recovered: 44584 0.1
 Deaths: 17 0.0
data points for Italy: 40
first data: 2020-01-31
latest data: 2020-03-10 (you can update the data manually by running fetch_data.py)

$python3 ./world_data.py  # to just plot current numbers

$python3 ./deaths_per_capita.py  # might be a better measure than cases per capita
```  
No GUI, you need to alter the script and run again to experiment.  
  
Note: Make sure you got correct number for population and available ICU units for your country.
  
## ToDo
* automatic date offset
* maybe find a better fit with lower R0
* add data about intensive care units
* ventilator patients separately?
* be more precise in differentiation between hospitalization and ICU

## Credits
Based on:  
https://github.com/ckaus/EpiPy  
https://scipython.com/book/chapter-8-scipy/additional-examples/the-sir-epidemic-model/  
  
API/Data:
https://github.com/ExpDev07/coronavirus-tracker-api
https://github.com/samayo/country-json
  
Formulas:  
https://hal.archives-ouvertes.fr/hal-00657584/document  
https://institutefordiseasemodeling.github.io/Documentation/general/model-seir.html  
  
Parameters:  
Master CoVidActNow CoVid-19 Model - https://docs.google.com/spreadsheets/d/1YEj4Vr6lG1jQ1R3LG6frijJYNynKcgTjzo2n0FsBwZA/htmlview?#

https://www.medrxiv.org/content/10.1101/2020.03.05.20031815v1  

Country Data:
https://github.com/porimol/countryinfo

## Screenshots
![model run](https://github.com/coronafighter/coronaSEIR/blob/master/screenshots/model_run.png)
![model run](https://github.com/coronafighter/coronaSEIR/blob/master/screenshots/model_run2.png)
![data](https://github.com/coronafighter/coronaSEIR/blob/master/screenshots/data.png)

## License
MIT license
