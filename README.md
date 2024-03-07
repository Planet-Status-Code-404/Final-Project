# Planet Status Code: 404
Exploring Climate Change’s Effects Through an Equity Lens 

Group Members: Gayathri, Gregory, Kiran, Onur 
GitHub userids: gregthemitch, gayathrij-hub, KiranJivnani, onurcan-b  

This project seeks to explore the multifaceted impacts of climate change and its distributional effects on communities across the United States.  We aim to understand how climate-induced factors such as floods, heatwaves, and hurricanes disproportionately affect vulnerable populations particularly in redlined communities. Leveraging data from the EPA, FEMA, Richmond Redlining dataset, Census, and a well-designed Climate Vulnerability Index, we will provide a tool to explore the ways climate change will affect communities differently and how those impacts may (or may not) disproportionately affect marginalized groups. This project focuses on Chicago, New Orleans, Los Angeles, Seattle, Dallas, and Houston, selected for their diversity in climate vulnerability.  

## User guide

### Instructions to run this project  
This application should be run through the terminal. Prior to running the data_collection code, please make sure you have added “master_cvi_data_indicators.csv” and “fema_nri_census_tracts.csv” to your project_404/data_collection/source_data folder. Both files are in the Drobox [link](https://www.dropbox.com/home/Planet%20Status%20Code%20404).

To run the data collection code, run: 
<p align="center">
$ poetry run python -m project_404 data_collection 
</p>

This process will take a few moments. After data_collection is complete you can then begin to run the chatbot.

To run the climate chatbot, run: 
<p align="center">
$ poetry run python -m project_404 climate_bot
</p>

The user will then be prompted to input a Ngrok tunnel key. The chatbot relies on an LLM self-hosted on Google Colab, and the key is generated every time the server is started. The key is located at the bottom of the file. To get access to the Google Colab Jupiter notebook, contact Gregory Mitchell (gmitchelljr@uchicago.edu).  

Once, the tunnel key has been inputted, the user can now make requests for the chatbot to provide maps or other data summaries. For best results, please refer to the “standardized” variable name documentation in GitHub (link)--these are the vairable names that follow the pattern psc_###. 

## Chatbot
The main functionality of the chatbot is to use SQL to help summarize data and to generate maps. You can add restrictions to the data as well (e.g., where life expectancy is less than 60). Again, because of the nature of LLMs, the ability for the chatbot to correctly parse input from the user is often inconsistent. While our code has been written around this fact, some trial and error with prompts may be needed. Also, due to time constraints, map making was the primary feature focused on and tested, but the bot can otherwise summarize the data. The details of the LLMs function calling abilities are below: 

Data summaries:  

- Available function names  
- Find top k  
- Sum  
- Average  
- Count  
- Median  

Map making  

- To make a map, you must specify the data to be mapped, and can specify the color of the map and the location/city of focus 

- The color can be a hexcode, a word, or a two-color name separated by hyphen (e.g., red-green).  

- The maps are programmed to open up in your browser automatically, however, if this doesn’t happen, you may have to open it up manually. To do this go to “Final-Project/project_404/chatbot/maps” and open the desired map. Once opened, the map will be interactive in the browser. 

Examples: 

If a user wanted to learn about average earthquake risk in Los Angeles, an example of a data summary request to the chatbot would be:  

>>> What is the average psc_83 in Los Angeles?  

An example of a map request would be:  

>>> Make me a green map of psc_83 in Los Angeles 

To add a condition, for example you were interested in mapping earthquake risk in tracts that have a homeless population greater than 500: 

>>> Make me a green map of psc_83 in Los Angeles if psc_30 is greater than 500 

## Reflection
Our group started this project with the intention of examining if climate change would have an outsized impact on vulnerable populations across the United States-particularly in redlined communities. We intended to do this via visualizations and data summarizations generated by an AI Chatbot. For the most part, our group accomplished most of these goals. We were able to collect significant amounts of data and feed said data into a chatbot which is programmed to summarize the data and create visualizations. However, we were not able to fully gauge if climate change impacts redlined communities more than other ones in the same city due to time constraints. Additionally, the chatbot, while often successful has its limitations. The Mistral 7B model allows for consumer, local use of LLMs, but the inconsistency and and hallucinations of the chatbot lead to some unreliability. This especially true with the large number of variables and instructions we provided it, and its relatively small context window. 

## Other notes
- Two data sources (FEMA National Risk Index and Climate Vulnerability Index (indicators) were too large to be uploaded to GitHub. Instead, please find them here. 

- The combined climate vulnerability index created during this project were too large to be uploaded to GitHub. Please find it here. 

- The EPA API found in epa.pyscript takes about 2 hours to run per city, amounting to a total of 8 hours. Additionally, the API produces successful calls only around 80% of the time.  
