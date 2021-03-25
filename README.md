# Gen - protein - other info finding in WikiData scripts

###Repo contains two scripts: 
- ### read_write_files.py
<br /> Script to read file with information that has to be found:
<br /> *file_example (input_file)*: 

```
SCO3114,SCO3114,protein transport,,integral component of membrane
SPy_0779,SPy0779,,,
Serine transporter BC3398,serine transporter BC3398,amino acid transmembrane transport,,integral component of membrane
kdsD,PP_0957,carbohydrate metabolic process,metal ion binding,
smi_1464,smi_1464,,,integral component of membrane
```

<br /> Output of the script is file with links:
<br /> *file_example (output_file)*: 

```
https://www.wikidata.org/wiki/Q23284357,https://www.wikidata.org/wiki/Q27750183,https://www.wikidata.org/wiki/Q14860325,https://www.wikidata.org/wiki/,https://www.wikidata.org/wiki/Q14327652
https://www.wikidata.org/wiki/Q23235634,https://www.wikidata.org/wiki/Q23497168,https://www.wikidata.org/wiki/,https://www.wikidata.org/wiki/,https://www.wikidata.org/wiki/
https://www.wikidata.org/wiki/Q23196205,https://www.wikidata.org/wiki/Q23514357,https://www.wikidata.org/wiki/Q14905294,https://www.wikidata.org/wiki/,https://www.wikidata.org/wiki/Q14349455
https://www.wikidata.org/wiki/Q22311550,https://www.wikidata.org/wiki/Q22318912,https://www.wikidata.org/wiki/Q2734081,https://www.wikidata.org/wiki/Q13667380,https://www.wikidata.org/wiki/
https://www.wikidata.org/wiki/Q23235886,https://www.wikidata.org/wiki/Q23548717,https://www.wikidata.org/wiki/,https://www.wikidata.org/wiki/,https://www.wikidata.org/wiki/Q14327652
```
This script uses next, to find information:

- ### find_wiki_page.py

<br /> Script to find linked genetic data in wikidata. Script uses library: requests and pywikibot to find and 
download data on wikidata portal.

API that is used: 'https://www.wikidata.org/w/api.php'

#####The most important methods are:
- *search_entities()*
  <br /> method as input gets an item identifier and returns information about the item (statement)
  

- *get_item_label()*
  <br /> method as input gets an item identifier and returns item label
  

- *get_item_descriptions()*
  <br /> method as input gets an item identifier and returns item description
  

- *get_item_aliases()*
  <br /> method as input gets an item identifier and returns item aliases


- *search_by_property()*
  <br /> method as input gets (a property identifier and value to if there is in property):


- *gene_search()*
  <br /> method as input gets a list of strings with labels/descriptions that have to be found and 
  returns list of id (if some of them were found). Method has few stages:
  
  1)  Using search_entities to search for gene
  2)  Searching for linked protein
  3)  Searching for biological_process ("P682")
      <br /> Searching for molecular_function ("P680")
      <br /> Searching for cell_component ("P681")


- *is_in_text()*
  <br /> Checks if some expression is in the text
  

- *start()*
  <br /> Starts all gene search in different ways

***
  
Advantages of the script: 
- The percentage of found pages is 97%
- Methods can be used to find separate data in wikidata

Disadvantages of the script: 
- code is not readable 
- vulnerable on different changes on input data
- takes to long to find big datasets
- not optimized

***
## Useful information about Wikidata
First: it is important to know the names of varariable (names) of items (features) in wikidata page. So they are here:
![Alt text](https://upload.wikimedia.org/wikipedia/commons/a/ae/Datamodel_in_Wikidata.svg)

#### It's good to know and use Wikidata:SPARQL:
- https://query.wikidata.org/
- https://www.wikidata.org/wiki/Wikidata:SPARQL_tutorial
- https://www.kdnuggets.com/2018/05/brief-introduction-wikidata.html
- https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/queries/examples#Genes
- Text Data Preprocessing: A Walk through in Python: https://www.kdnuggets.com/2018/03/text-data-preprocessing-walkthrough-python.html
- https://developer.ibm.com/articles/use-wikidata-in-ai-and-cognitive-applications-pt1/

#### API
- https://gist.github.com/ettorerizza/7eaebbd731781b6007d9bdd9ddd22713
- https://www.mediawiki.org/wiki/API:Presenting_Wikidata_knowledge

#### Pywikibot
- https://www.wikidata.org/wiki/Wikidata:Pywikibot_-_Python_3_Tutorial/Data_Harvest
