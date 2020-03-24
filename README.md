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

Note: Make sure you got correct number for population and available ICU units for your country.
  
## ToDo
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

## Examples
![Without Lockdown](https://github.com/cfculhane/coronaSEIR/blob/master/examples/NoLockdown.png)
![With Lockdown](https://github.com/cfculhane/coronaSEIR/blob/master/examples/Lockdown-R0-halved.png)


## License
MIT license
