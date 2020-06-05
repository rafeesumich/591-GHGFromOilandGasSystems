#!/usr/bin/env python
# coding: utf-8

# # SIADS 591-592 Milestone 1 Project
# 
# ## Greenhouse Gas (GHG) Emissions from Upstream and Midstream US Oil and Gas Operations
# 
# By Rafee Shaik and Greg Myers
# <br>April-May 2020
# 
# 
# ## Analysis and Visualization
# 
# ### Summary of visualizations:
# In this notebook we genearted several visualizations, most of them are time-series line+scatter plots.
# * [Fig-0](#Fig-0): A look at the historical Crude Oil and Natural Gas Production in the USA.
# * [Fig-1](#Fig-1): Trend line of total GHG emissions from US Oil and Gas Companies between 2011 and 2018.
# * [Fig-2](#Fig-2): A table showing GHG Emissions from individual US Oil and Gas Producers between 2011 and 2018
# * [Fig-3](#Fig-3): An Interactive chart - Emission trends between 2009 and 2018 from the top US emitters
# * [Fig-4](#Fig-4): An Interactive chart to compare emissions between different companies and sectors
# * [Fig-5](#Fig-5): A 4X4 Subplots to show, Emissions by sector, GHG Gas Type, Number of Operators(companies) in each sector and Total emissions
# * [Fig-6](#Fig-6): A histogram to identify the common emission quantity range from US Oil & Gas companies
# * [Fig-7](#Fig-7): An interactive chart to compare Emissions from Upstream and Midstream Sectors VS Crude Oil and Natural Gas Production
# * [Fig-8](#Fig-8): A line chart with predicted 2019 GHG Emission
# 
# 
# We prepared a linear regression model between between Hydrocarbon production and GHG emission volumes; We used this model to estimate the future emissions based on production volume
# 
# ### Visualization Technique:
# We used graph_objs and plotly.express libraries from plotly for visualizations in this analysis.
# * Most of our plots are scatter plots with line marks over time-series data.
# * We used a histogram to study the distribution of number of operators across different emission ranges
# * We used ipywidgets to add interactivity to the visualizations.
# 
# https://www.govinfo.gov/content/pkg/FR-2015-10-22/pdf/2015-25840.pdf
# 
# <b>Other libraries used:</b>
# <br>Pandas, numpy, scipy, matplotlib, sklearn
# 

# In[1]:


#Libraries for data manipulation
import pandas as pd
import numpy as np

#Libraries for linear regression and calculating r-value.
import scipy as sp
from scipy import special
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score

#plotly imports - main graphics library
import plotly as py
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib as mpl
#set the plotly offline mode
py.offline.init_notebook_mode(connected=True)

# ipywidgets for interactivity
import ipywidgets as widgets
from ipywidgets import interact
from ipywidgets import HBox,VBox, Label

# Supress warnings
import warnings
warnings.filterwarnings('ignore')

get_ipython().run_line_magic('config', 'IPCompleter.greedy=True')
get_ipython().run_line_magic('matplotlib', 'inline')


# ### Fig-0: Historic Crude Oil and Natural Gas Production in the USA
# <a id='Fig-0'></a>

# In[2]:


df_production=pd.read_csv('Processed_AnnualProductionData.csv',sep='|')
df_production = pd.concat([df_production[df_production['Product']=='Crude'] , df_production[(df_production['Product']=='Natural Gas') & (df_production['Date']>1980)]])

fig9 = px.line(df_production, x="Date", y="Production kBOE", color='Product')
fig9.update_layout(title='<b>Historical Crude Oil and Natural Gas Production in the USA</b>'
                   ,xaxis = dict(title = 'Report Year')
                   ,legend_orientation="h"
                   ,margin=dict(l=0,t=75)
                   ,legend=dict(x=.6, y=.93)
                   ,legend_title_text=''
                  )
fig9.add_annotation(go.layout.Annotation(x=2007, y=1850000, xref='x',  yref='y', text='Beginning of Shale Boom in the US – Horizontal drilling and fracking', font=dict( size=14, color="#FF7F0E" ), align="left", showarrow=True, arrowhead=1, ax=-120, ay=60))
fig9.show()


# Emissions_aggregatedData.csv is one of the main datasets for several visualizations in this analysis. Load the CSV file into a pandas data frame and select required columns used in various figures in the analysis

# In[3]:


#Read data from csv file generated from 'EmissionsDataPreparation.ipynb' file.
df_EmissionByGasSec = pd.read_csv('Emissions_aggregatedData.csv',sep='|')

#Pickup required columns and rename them
Emissioncolumns = ['STANDARD_COMPANY_NAME','REPORTING YEAR',  'GAS', 'SECTOR', 'GHG_CONTRIBUTION', '2018_UPSTREAM_RANK', '2018_MIDSTREAM_RANK', '2018_OVERALL_RANK']
df_EmissionByGasSec = df_EmissionByGasSec[Emissioncolumns]
df_EmissionByGasSec=df_EmissionByGasSec.rename(columns={'STANDARD_COMPANY_NAME':'COMPANY', 'REPORTING YEAR':'REPORTING_YEAR'})

#Aggregate the data by Company, Year and Sector
df_aggByYearComp=df_EmissionByGasSec[['COMPANY','REPORTING_YEAR', 'SECTOR', 'GHG_CONTRIBUTION']].groupby(['COMPANY','REPORTING_YEAR','SECTOR']).sum().reset_index().sort_values('GHG_CONTRIBUTION',ascending=False)

#Assign a rank by their total emission in last 9 years
#Midstream rank
df_mid = df_aggByYearComp[df_aggByYearComp['SECTOR']=='Midstream']
df_mid=df_mid[['COMPANY','GHG_CONTRIBUTION']].groupby('COMPANY').sum().reset_index().sort_values('GHG_CONTRIBUTION',ascending=False).reset_index().drop('index',axis=1).reset_index().rename(columns={'index':'MIDSTREAM_RANK'})
df_mid['MIDSTREAM_RANK']=df_mid['MIDSTREAM_RANK']+1
df_mid=df_mid.drop('GHG_CONTRIBUTION', axis=1)
#df_mid.head()

#Upstream rank
df_up = df_aggByYearComp[df_aggByYearComp['SECTOR']=='Upstream']
df_up=df_up[['COMPANY','GHG_CONTRIBUTION']].groupby('COMPANY').sum().reset_index().sort_values('GHG_CONTRIBUTION',ascending=False).reset_index().drop('index',axis=1).reset_index().rename(columns={'index':'UPSTREAM_RANK'})

df_up['UPSTREAM_RANK']=df_up['UPSTREAM_RANK']+1
df_up=df_up.drop('GHG_CONTRIBUTION', axis=1)
#df_up.head()

df_aggByYearComp=df_aggByYearComp.merge(df_mid,how='left', left_on='COMPANY', right_on='COMPANY').merge(df_up,how='left', left_on='COMPANY', right_on='COMPANY')

df_aggByYearComp['MIDSTREAM_RANK']=df_aggByYearComp['MIDSTREAM_RANK'].fillna(max(df_aggByYearComp['MIDSTREAM_RANK'])+1)
df_aggByYearComp['UPSTREAM_RANK']=df_aggByYearComp['UPSTREAM_RANK'].fillna(df_aggByYearComp['UPSTREAM_RANK'].max()+1)
df_aggByYearComp['GHG_CONTRIBUTION']=df_aggByYearComp['GHG_CONTRIBUTION'].astype(int)
#df_aggByYearComp.head()


# ### Fig-1: Trend line of total GHG emissions from US Oil and Gas Companies between 2011 and 2018.
# <a id='Fig-1'></a>

# In[4]:


df_fig1=df_aggByYearComp[['REPORTING_YEAR','GHG_CONTRIBUTION']].groupby('REPORTING_YEAR').sum().reset_index().sort_values('REPORTING_YEAR')

x=df_fig1.REPORTING_YEAR

layout=go.Layout(title='<b>Total GHG Emissions between 2011 to 2018 - (in METRIC TONS CO2e)</b>',
                 xaxis=dict(title='REPORT YEAR'),yaxis=dict(title='Emission in metric tons of CO2e'), 
                 margin=dict(l=0)
                )
trace1 =  go.Scatter(x=x,
                     y=df_fig1.GHG_CONTRIBUTION,
                     mode = 'lines+markers',
                     name='Total Emission'
                     ,line = dict(shape='spline')
                    )
fig1 = go.Figure(data=[trace1], layout=layout)
fig1.show()


# Fig-1 shows the upwards trend in GHG Emissions from Oil & Gas upstream and midstream systems

# ### Fig-2: A summary table showing GHG Emissions from the top US Oil and Gas Producers between 2011 and 2018
# <a id='Fig-2'></a>

# In[5]:


df_fig2=df_aggByYearComp[['COMPANY', 'REPORTING_YEAR', 'GHG_CONTRIBUTION']].groupby(['COMPANY', 'REPORTING_YEAR']).sum().reset_index().pivot_table(values='GHG_CONTRIBUTION',index='COMPANY',columns='REPORTING_YEAR').reset_index()

df_fig2.to_csv('PlotlyFig2.csv',index=False)
df_fig2=pd.read_csv('PlotlyFig2.csv')

df_fig2['TOTAL_EMISSION']=df_fig2.sum(axis=1)
df_fig2=df_fig2.sort_values('TOTAL_EMISSION', ascending=False).reset_index().drop('index',axis=1)

#Plotly table plot reference: https://plotly.com/python/table/

fig2 = go.Figure(data=[go.Table(columnwidth = [250,200,120,120,120,120,120,120,120,120],
    header=dict(values=['<b>COMPANY</b>', '<b>TOTAL_EMISSION</b>' ,'2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018'],
                line_color='darkslategray',
                fill_color='rgb(235, 70, 52)',
                align='center'),
    cells=dict(values=[df_fig2['COMPANY'],df_fig2['TOTAL_EMISSION'],df_fig2['2011'],df_fig2['2012'],df_fig2['2013'],df_fig2['2014'],df_fig2['2015'],df_fig2['2016'],df_fig2['2017'],df_fig2['2018']],
               fill_color='rgb(255, 191, 0)',
               align='left'))
])
fig2.update_layout(title={'text':'<b>Greenhouse Gas Emissions from the top US Oil & Gas Companies (in METRIC TONS CO2e)</b>'},
                    #font=dict(#family="Courier New, monospace",size=18 #,color="#7f7f7f"),
                   width=1000,
                   margin=dict(l=0,b=20)
                  )

fig2.show()


# ### Fig-3: An Interactive chart - Emission trends between 2009 and 2018 from the top US emitters
# <a id='Fig-3'></a>

# In[6]:


df_fig3=df_fig2.copy()
df_fig3=df_fig3[['COMPANY', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018']]

x=['2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018']

layout3=go.Layout(title='<b>GHG Emission trends between 2009 and 2018 from the top US emittors</b>',
                  xaxis = dict(title = 'REPORT YEAR'),
                  yaxis = dict(title = 'Emission Quantity in Metric Tons (CO2e)'),
                  margin=dict(l=0)
                  )
# in this figure we're going to use ipywidgets 'interact' decorator for interactivity.
@interact(numComp=widgets.IntSlider(value=7,min=1,max=len(df_fig3.COMPANY.unique()), step=1,description='Top N Companies:',
                          disabled=False,
                          continuous_update=False,
                          orientation='horizontal',
                          readout=True,
                          readout_format='d'))
def update_fig(numComp):
    fig3=go.Figure(layout=layout3)
    for i in range(numComp):
        fig3.add_scatter(x=x,
                      y=df_fig3.loc[i][['2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018']],
                      mode='lines+markers',
                      name=df_fig3.loc[i]['COMPANY']
                     )
    fig3.show()


# This chart can be used to compare GHG emissions between top US Oil and Gas companies from 2011 to 2018. 
# <br>Companies are sorted in GHG emission volume descending order.
# <br>Use the slider bar to select the number of companies to compare

# ### Fig-4: An Interactive chart to compare emissions between different companies and sectors

# ##### Widgets used:
# 1. Company - Dropdown - Multiple Selection
# 2. GAS - Checkbox
# 3. Sector - Checkbox
# 
# Code reference: https://stackoverflow.com/questions/12096252/use-a-list-of-values-to-select-rows-from-a-pandas-dataframe
# <a id='Fig-4'></a>

# In[21]:


df_fig4=df_EmissionByGasSec.copy()
cols=['COMPANY', 'REPORTING_YEAR', 'GAS', 'SECTOR', 'GHG_CONTRIBUTION']
groupby_cols=['COMPANY','REPORTING_YEAR']

x=['2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018']

y_title='Emission Quantity in Metric Tons (CO2e)'

layout4=go.Layout(title='<b>Comparision of emissions from diffrent US Upstream and Midstream Oil & Gas companies</b>',
                yaxis = dict(title = y_title),
                xaxis = dict(title = 'Report Year')
                )
cols=['COMPANY', 'REPORTING_YEAR', 'GAS', 'SECTOR', 'GHG_CONTRIBUTION']
groupby_cols=['COMPANY','REPORTING_YEAR']

#Widgets
comp_selection=widgets.SelectMultiple(options=list(df_fig4.COMPANY.unique()), description='Company:')
sec_selection=widgets.SelectMultiple(options=list(df_fig4.SECTOR.unique()),  description='Sector:')
gas_selection=widgets.SelectMultiple(options=list(df_fig4.GAS.unique()), description='GHG Gas:')

container = widgets.HBox(children=[comp_selection,sec_selection,gas_selection])

trace1=go.Scatter(x=x, y=df_fig4[cols].groupby('REPORTING_YEAR').sum()['GHG_CONTRIBUTION'], name='All companies')
fig4=go.FigureWidget(trace1,layout=layout4)

#action method
def update_plot(change):
    yaxis_title=y_title
    df_fig4selection=df_fig4
    #Clean previous selection
    fig4.data=[]
    #filter sector selection - if nothing selected then we assume all sectors are selected
    if(len(sec_selection.value)==0):
        pass
    else:
        df_fig4selection = df_fig4selection[df_fig4selection['SECTOR'].isin(list(sec_selection.value))]
    
    #filter gas selection - If nothing selected then we assume all gases are selected
    if(len(gas_selection.value)==0):
        pass
    else:
        df_fig4selection = df_fig4selection[df_fig4selection['GAS'].isin(list(gas_selection.value))]
    
    #If no company is selected then we will plot a graph with all companies
    if (len(comp_selection.value)==0):
        fig4.add_scatter(x=x,
                           y=df_fig4selection[cols].groupby('REPORTING_YEAR').sum()['GHG_CONTRIBUTION'],
                           name='All companies'
                          )
    for company in comp_selection.value:
        fig4.add_scatter(x=x,
                           y=df_fig4selection[df_fig4selection['COMPANY']==company][cols].groupby(groupby_cols).sum()['GHG_CONTRIBUTION'],
                           name=company
                          )
comp_selection.observe(update_plot, names="value")
sec_selection.observe(update_plot, names="value")
gas_selection.observe(update_plot, names="value")
widgets.VBox([container,fig4])


# This tool can be used to study the emissions from multiple companies’ individual sectors and GHG gas types.
# <br>Use above interactive chart to drilldown into individual sectors and GHG gas types

# ### Fig 5: A 4X4 Subplots to show
# 1. Emission by sector
# 2. Emissions by GHG Gas Type
# 3. Number of operators by sector and total operators
# 4. Total emissions
# <a id='Fig-5'></a>

# In[8]:


df_fig5=df_EmissionByGasSec[cols]
# Sector wise emissions
df_fig5_sec=df_fig5[['SECTOR','REPORTING_YEAR','GAS','GHG_CONTRIBUTION']].groupby(['SECTOR','REPORTING_YEAR']).sum().reset_index()

fig5 = make_subplots(
    rows=2, cols=2,specs = [[{}, {}],[{}, {}]], horizontal_spacing = 0.08,vertical_spacing=0.1,
    subplot_titles=("Total Emissions", "Emissions by Sector", "Emissions by GHG Gas type", "Number of Operators in each sector"))

# Emission by sector
for sec in df_fig5_sec.SECTOR.unique():
    trace=go.Scatter(x=x, y=df_fig5_sec[df_fig5_sec['SECTOR']==sec]['GHG_CONTRIBUTION'],name=sec)
    fig5.add_trace(trace, row=1, col=2)

# Emission by GAS type    
df_fig5_gas = df_fig5[['SECTOR','GAS','REPORTING_YEAR','GHG_CONTRIBUTION']].groupby(['GAS','REPORTING_YEAR']).sum().reset_index()
for gas in df_fig5_gas.GAS.unique():
    trace=go.Scatter(x=x, y=df_fig5_gas[df_fig5_gas['GAS']==gas]['GHG_CONTRIBUTION'],name=gas)
    fig5.add_trace(trace, row=2, col=1)    


#Number of operators 
df_fig5_oper=df_fig5[['COMPANY','SECTOR','REPORTING_YEAR']].groupby(['COMPANY','SECTOR','REPORTING_YEAR']).count().reset_index().groupby(['SECTOR','REPORTING_YEAR']).count().reset_index()

operTraceList=[]
for sec in df_fig5_oper.SECTOR.unique():
    trace=go.Scatter(x=x, y=df_fig5_oper[df_fig5_oper.SECTOR==sec]['COMPANY'], name=sec)
    fig5.add_trace(trace, row=2, col=2)

#Total emission
trace_totals = go.Scatter(x=x, y=df_EmissionByGasSec[['REPORTING_YEAR','GHG_CONTRIBUTION']].groupby('REPORTING_YEAR').sum().reset_index().GHG_CONTRIBUTION,name='Total Emission volumes',line=dict(color='#1F77B4'))
fig5.add_trace(trace_totals, row=1, col=1)

fig5.update_layout(title='<b>GHG Emission volume between 2011 to 2018 - (in METRIC TONS CO2e)</b>',
                   height=700,
                   margin=dict(l=0),
                   showlegend=False
                  )
fig5.add_annotation(go.layout.Annotation(x=2012, y=285000000, xref='x1',  yref='y1', text='<b>---</b> Total Emissions', font=dict( size=14, color="#1F77B4" ), align="left", showarrow=False, arrowhead=7, ax=10, ay=70))

fig5.add_annotation(go.layout.Annotation(x=2012, y=170000000, xref='x2',  yref='y2', text='<b>---</b> Midstream', font=dict( size=14, color="#636EFA" ), align="left", showarrow=False, arrowhead=7, ax=10, ay=70))
fig5.add_annotation(go.layout.Annotation(x=2015, y=170000000, xref='x2',  yref='y2', text='<b>---</b> Upstream', font=dict( size=14, color="#EF553B" ), align="left", showarrow=False, arrowhead=7, ax=10, ay=70))

fig5.add_annotation(go.layout.Annotation(x=2012, y=210000000, xref='x3',  yref='y3', text='<b>---</b> CO2', font=dict( size=14, color="#AB63FA" ), align="left", showarrow=False, arrowhead=7, ax=10, ay=70))
fig5.add_annotation(go.layout.Annotation(x=2014, y=210000000, xref='x3',  yref='y3', text='<b>---</b> CH4', font=dict( size=14, color="#00CC96" ), align="left", showarrow=False, arrowhead=7, ax=10, ay=70))
fig5.add_annotation(go.layout.Annotation(x=2016, y=210000000, xref='x3',  yref='y3', text='<b>---</b> N2O', font=dict( size=14, color="#FFA15A" ), align="left", showarrow=False, arrowhead=7, ax=10, ay=70))

fig5.add_annotation(go.layout.Annotation(x=2012, y=290, xref='x4',  yref='y4', text='<b>---</b> Midstream', font=dict( size=14, color="#19D3F3" ), align="left", showarrow=False, arrowhead=7, ax=10, ay=70))
fig5.add_annotation(go.layout.Annotation(x=2015, y=290, xref='x4',  yref='y4', text='<b>---</b> Upstream', font=dict( size=14, color="#FF6692" ), align="left", showarrow=False, arrowhead=7, ax=10, ay=70))


fig5.show()


# ### Fig-6: A histogram to identify the common emission quantity range from US Oil & Gas companies
# <a id='Fig-6'></a>

# In[9]:


df_fig7=df_aggByYearComp.copy(deep=True)
df_fig7 = df_fig7[df_fig7.GHG_CONTRIBUTION>=0]

fig7 = make_subplots(
    rows=2, cols=4,specs = [[{}, {},{}, {}],[{}, {},{}, {}]], horizontal_spacing = 0.05,vertical_spacing=0.15,
    subplot_titles=('2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018'))

for year in range(2011, 2019,1):
    trace_up=go.Histogram(x=df_aggByYearComp[(df_aggByYearComp['REPORTING_YEAR']==year) & (df_aggByYearComp['SECTOR']=='Upstream')]['GHG_CONTRIBUTION'],
                          #histnorm='probability', # enable the option to see the normalized histogram
                          opacity=0.75, 
                          name='Upstream Operators',
                          xbins=dict(start=0, end=15000000, size=500000),
                          marker_color='#EF553B',
                          showlegend=False
                         )
    trace_mid=go.Histogram(x=df_aggByYearComp[(df_aggByYearComp['REPORTING_YEAR']==year) & (df_aggByYearComp['SECTOR']=='Midstream')]['GHG_CONTRIBUTION'],
                           #histnorm='probability',
                           opacity=0.75, 
                           name='Midstream Operators',
                           xbins=dict(start=0, end=15000000, size=500000),
                           marker_color='#FFA15A',
                           showlegend=False
                          )
    fig7.add_trace(trace_up,row=year%2011//4+1, col=year%2011%4+1 )
    fig7.add_trace(trace_mid,row=year%2011//4+1, col=year%2011%4+1 )

fig7.add_trace(go.Scatter(x=[None], y=[None],
                          mode='markers',
                          marker=dict(size=15, color='#EF553B'),
                          showlegend=True, name='Upstream Operators'),row=1,col=1
              )
fig7.add_trace(go.Scatter(x=[None], y=[None],
                          mode='markers',
                          marker=dict(size=15, color='#FFA15A'),
                          showlegend=True, name='Midstream Operators'),row=1,col=1
              )
layout=go.Layout(title=dict(text='<b>Distribution of number of Oil & Gas Operators in different GHG Emission ranges</b>')
                 ,barmode='stack'
                 #barmode='overlay'
                 ,margin=dict(t=150)
                 ,legend_orientation="h"
                 ,legend=dict(x=.25, y=1.12)
                 ,height=650,
                 #xaxis_type="log"
                )    
fig7.update_layout(layout )

py.offline.iplot(fig7)


# ### Fig- 7: An interactive chart to compare Emissions from Upstream and Midstream Sectors VS Crude Oil and Natural Gas Production
# 
# #### With this graph we can compare 
# 1. Natural Gas Production vs Midstream Emissions
# 2. Crude Oil Production vs Upstream Emissions
# 3. Natural Gas Production vs Upstream Emissions
# 4. Crude Oil Production vs Midstream Emissions
# 5. Overall Hydrocarbon Production vs Emission from both Upstream and Midstream sectors
# <a id='Fig-7'></a>

# In[10]:


df_ProdVsEm=pd.read_csv('ProductionVsEmissionSplit.csv',sep='|')

prodList=list(df_ProdVsEm[df_ProdVsEm.Key.str.contains('Production')].Key.unique())
emiList=list(df_ProdVsEm[df_ProdVsEm.Key.str.contains('Emission')].Key.unique())

x=['2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018']

layout6=go.Layout(title='<b>Oil and Gas Production vs GHG Emissions from Upstream and Midstream sectors</b>',
                xaxis = dict(title = 'Report Year')
                )

@interact(prod_selection=widgets.SelectMultiple(options=prodList, description='Product:'), emi_selection=widgets.SelectMultiple(options=emiList, description='Sector:'))
def update_fig6(prod_selection, emi_selection):
    fig6 = make_subplots(specs=[[{"secondary_y": True}]])
    if(len(prod_selection)==0):
        prodsel=prodList
    else:
        prodsel=prod_selection
    
    for prod in prodsel:
        fig6.add_trace(go.Scatter(x=x, y=df_ProdVsEm[df_ProdVsEm.Key==prod]['Value'],name=prod),secondary_y=False, )
    
    if(len(emi_selection)==0):
        emisel=emiList
    else:
        emisel=emi_selection
    
    for emi in emisel:
        fig6.add_trace(go.Scatter(x=x, y=df_ProdVsEm[df_ProdVsEm.Key==emi]['Value'],name=emi),secondary_y=True, )
    
    fig6.update_layout(layout6)
    fig6.update_yaxes(title_text="Production Volume in kBOE", secondary_y=False)
    fig6.update_yaxes(title_text="GHG Emissions in Metric Tons CO2e", secondary_y=True)
    fig6.show()


# Most of the Oil and Gas companies emit less then 500K metric tons of GHG gases. There are very few companiew producing over 5 million tons of GHG gases

# ## A linear regression analysis between emission quantity and production volumes

# In[11]:


df_ProdVsEm=pd.read_csv('ProductionVsEmissionSplit.csv',sep='|')
df_regress=df_ProdVsEm.pivot_table(values='Value',index='REPORTING_YEAR',columns='Key').reset_index()
df_regress


# In[12]:


#Feature selction
r2Prod_cols = ['Combined Production', 'Crude Production', 'Natural Gas Production']
r2Emi_cols = ['Combined Emission', 'Midstream Emission', 'Upstream Emission']

df_r2=df_regress[df_regress['REPORTING_YEAR']<2019]
for prdcol in r2Prod_cols:
    for emicol in r2Emi_cols:
        slope, intercept, r_value, p_value, std_err=sp.stats.linregress(df_r2[prdcol],df_r2[emicol])
        print('Product:',prdcol,', Sector:',emicol ,', r-value:',r_value)


# ###### From the above analysis, we observed a higher correlation between Natural Gas Production and Combined Emission (Upstream and Midstream)

# ### Estimating combined emission quantity (upstream and midstream) for the year 2019 from Natural Gas production volume
# 
# ###### Since we have only 8 datapoints to run the linear regression we are going to use all datapoints to train the model.

# In[13]:


def emissionRegression(df_X, target_y,emission_X_pred):
    regr = linear_model.LinearRegression()
    regr.fit(df_X, target_y)
    emission_y_pred = regr.predict(emission_X_pred)
    #print('Predicted value of Combined Emission from key ',emission_X_pred ,' is :',emission_y_pred)
    return emission_y_pred


# In[14]:


df_train = df_regress[df_regress['REPORTING_YEAR']<2019]
test=df_regress[df_regress['REPORTING_YEAR']==2019]

independent_cols=['Natural Gas Production']

X=df_train[independent_cols]
y=df_train['Combined Emission']

estimated_emi_2019=emissionRegression(X.values, y ,test[independent_cols].values)
print(estimated_emi_2019[0])


# In[15]:


#df_predicted[df_predicted['REPORTING_YEAR']==2019]['Combined Emission']=estimated_emi_2019
df_predicted=df_regress.copy(deep=True)
df_predicted.at[8,'Combined Emission']=estimated_emi_2019


# ### Fig-8: Plot predicted 2019 GHG Emission on a time-series line chart
# <a id='Fig-8'></a>

# In[16]:


fig8=make_subplots(specs=[[{"secondary_y": True}]])

#Emissions line till 2018.
#df_predicted[df_predicted['REPORTING_YEAR']<=2018]
fig8.add_trace(go.Scatter(x=df_predicted[df_predicted['REPORTING_YEAR']<=2018]['REPORTING_YEAR'],
                          y=df_predicted[df_predicted['REPORTING_YEAR']<=2018]['Combined Emission'],
                          name='Combined Emission',
                          line=dict(color='royalblue')
                         ),secondary_y=False)
#Emissions line from 2018 to 2019.
fig8.add_trace(go.Scatter(x=df_predicted[df_predicted['REPORTING_YEAR']>=2018]['REPORTING_YEAR'],
                          y=df_predicted[df_predicted['REPORTING_YEAR']>=2018]['Combined Emission'],
                          name='Estimated Emission',
                          line=dict(color='royalblue', width=6, dash='dot')
                         ),secondary_y=False)
fig8.add_trace(go.Scatter(x=df_predicted['REPORTING_YEAR'],
                          y=df_predicted['Natural Gas Production'],
                          name='Natural Gas Production',
                          line=dict(color='#EF553B')
                         ),secondary_y=True)

title='<b>Estimated 2019 Combined emission(Upsteam and Midstream) is: ' +str(round(estimated_emi_2019[0]/1000000,2))+'M metric tons of CO2e</b>'

fig8.update_layout(title=title
                  ,xaxis = dict(title = 'Report Year')
                 ,legend_orientation="h"
                 ,legend=dict(x=.25, y=1.12))

fig8.update_yaxes(title_text="GHG Emissions in Metric Tons CO2e", secondary_y=False)
fig8.update_yaxes(title_text="Natural Gas Production in kBOE", secondary_y=True)

fig8.show()


# In[ ]:




