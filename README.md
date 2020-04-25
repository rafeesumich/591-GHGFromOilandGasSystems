### The Effects of enhanced Hydrocarbon extraction technology on Greenhouse Gas emissions from Upstream and Midstream Oil and Gas industry

<b>Problem Statement:</b>
The purpose of this project is to examine established Greenhouse Gas (GHG) Emissions data and determine if there is a correlation between accelerated hydrocarbon (Crude oil and Natural gas) production through horizontal drilling and hydraulic fracturing in the most recent decade and GHG emissions rates. If a correlation is found, additional analysis may be able to reveal the causal source. The project will focus on three GHGs, Carbon-Dioxide (CO2), Methane (CH4), and Nitrous-Oxide (N2O).

<b>Questions to Answer:</b>
* Is there a correlation between increased hydrocarbon production and industry sector GHG emissions? 
* Does the correlation apply to the industry as a whole or to one or more individual components?

#### Source Datasets
<b>Dataset 1:</b>
><br><b>Data Type:</b> Greenhouse Gas Emissions Data
<br><b>Source:</b> US Oil and Gas Upstream (Exploration & Production) and Midstream (Pipelines and Storage) facilities can be accessed from the U.S. Environmental Protection Agency (EPA) FLIGHT database.
<br><b>Location:</b> https://ghgdata.epa.gov/ghgp/main.do
<br><b>Access Method:</b> Facility Level Information on GreenHouse gases Tool (FLIGHT) database can be accessed through the website: https://ghgdata.epa.gov/ghgp/main.do
Download the data in excel format after applying appropriate filters.
<br><b>Format:</b>  Excel spreadsheets 
<br><b>Dataset Size:</b> Six excel spreadsheets with a total of 41K records.

<b>Dataset 2:</b>
><br><b>Data Type:</b> Emission Data from other Industrial Sectors
<br><b>Source:</b> Emissions data from other Industrial sectors can be downloaded from the EAP data store. We will use this data to compare GHG emissions from Oil & Gas systems and other industrial sectors.
<br><b>Location:</b> https://cfpub.epa.gov/ghgdata/inventoryexplorer/#industry/allgas/source/all
<br><b>Access Method:</b> Web Scraping if there are no popups preventing web scraping, otherwise use the manual download option.
<br><b>Format:</b> CSV or Web Scraping, csv name will be IndustryWiseGHGEmissions.csv, if we’re not able to scrape it from the web.
<br><b>Dataset Size:</b> 243 records

<b>Dataset 3:</b>
><br><b>Data Type:</b> Crude Oil and Natural Gas Production
       <br>U.S. Field Production of Crude Oil, U.S. Natural Gas Gross Withdrawals; Yearly
<br><b>Source:</b> Energy Information Administration (EIA) datastore.
<br><b>Location:</b> https://www.eia.gov/opendata/qb.php?category=371
<br><b>Access Method:</b> API query
<br><b>Format:</b> JSON
<br><b>Dataset Size:</b> Crude records: 161; Gas records: 84; ~3 kilobytes each for crude and oil

#### Data Manipulation Methods:
<b>Processing Emissions datasets:</b>
1. CH4 and N2O emissions are represented in CO2 equivalent quantities.
2. Data is present in multiple sheets, a sheet for each year. Load each of these files into a separate data frame and flag what type of gas and which sector it is.
3. Aggregate the emission quantities by the parent company
4. Combine all the six datasets into a single data frame. Fill ‘NaN’ values with zero

<b>Processing Emissions from Other industrial sectors:</b>
1. Data is present in wide-format, unpivot the data to put it in long-format, use pandas melt method.

<b>Processing Crude and Natural Gas Production volumes datasets:</b>
1. Save API query results to a JSON file as an immutable source data reference.
2. Import JSON data (crude & gas) into Pandas data frames.
3. Perform Explode operations to separate date and production data.
4. Transform date column into a DateTime data type.
5. Create and populate a product type column and drop unused columns.
6. Append crude and gas data frames (long-format).
7. Save the data frame in CSV format as a source for continued analysis.

#### Data Integration:
Combine the above two datasets (Emissions and Production volumes) by the year, with this combined dataset we can compare greenhouse gas emission volumes with O&G production volumes.

#### Analysis and Visualization:
* A regression analysis will be conducted to estimate missing emissions date from 1990 to 2010 and for 2019. If an acceptable R-Squared value can be obtained from the regression analysis, the estimated data points will be used in the following visualizations.
* A scatterplot will be used to observe potential correlation between hydrocarbon production and Greenhouse Gas emissions. Another visualization of interest will plot GHG trend curves against U.S. Natural Gas and Petroleum production curves in the time frame beginning year 2010 to present. If time permits, an interactive heatmap will be prepared to show the GHG emissions and Hydrocarbon production at the US state level.
