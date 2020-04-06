
# meander
Code for establishing relationship between meander-wavelength/sinuosity's and discharge using GFAS and academic datasets. 

## Scripts
A script can be run, stand-alone. These files accomplish one, specific task that I probably won't repeat or adapt in any intensive way. 
- copernicus_data_extraction.py : A script for reading the 300GB of discharge files pulled from the Copernicus CDS website and performing basic data analytics on it. This computationally intensive script currently produces a file that includes 40 year mean, max, and minima for every lat/lon point. https://cds.climate.copernicus.eu/cdsapp#!/dataset/cems-glofas-historical?tab=form

## Packages
Packages are collections of methods that I expect to use repeatedly. These can't be run standalone. 
- data_methods.py : methods for extracting and formatting data 
- vis_methods.py : methods for visualizing data. Relies heavily on matplotlib and cartopy 

## Notebooks 
Jupyter notebooks are scripts with formatted text and figures included. 
- example_notebook.ipynb : A notebook showing how to generate and perform basic analytics and visualizations on the MS_segments_averaged.xlsx file. 
- Analysis on River Segments.ipynb : A notebook relating hand-measured meander wavelengths (by Char/Brynn) and discharges calculated from GLOFAS 
- fix_nn.ipynb : A notebook comparing simple, old nearest-neighbors method with new, grid-search nearest neighbors method 
- rec_int.ipynb : A Jupyter notebook calculating relationships to recurrence intervals 

## Dependencies 
- numpy
- pandas
- cartopy
- matplotlib 
- scikit-learn 
- scipy

- pickle 
- time 