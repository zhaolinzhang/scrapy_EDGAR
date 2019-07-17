## Web Crawler Project from EDGAR  
1. [Summary.](#summary)
2. [Usage Instructions.](#usage)
3. [Possible Improvement](#improv)

<a name='summary'></a>
#### Summary  
This is a web crawler project, which designed for retrieve mutual fund holding information from SEC website EDGAR by providing CIK or company name.

The crawler can choose the most recent report from the XML page and export to ,tsv file . 

This project is using scrapy platform, more information is here:
`<link>` : <https://scrapy.org/>

<a name='usage'></a>
#### Usage Instruction  
##### Step 1: Install scrapy
##### Step 2: Open a new terminal under the project directory. 
##### Step 3: If CIK is known, run the code in Terminal
```
scrapy crawl EDGARSpiderCIK -a CIK={YOUR_CIK}
```
For example:
```
scrapy crawl EDGARSpiderCIK -a CIK=0001166559
```
##### Step 3(Cont.): If company name is known
```
scrapy crawl EDGARSpiderCompName -a company_name="{YOUR_COMPANY_NAME}"
```
For example:
```
scrapy crawl EDGARSpiderCompName -a company_name="Peak6 Investments LLC"
```

<a name='improv'></a>
#### Possible Improvement
1. How to get previous reports: In EDGARSpiderCIK.parse() and EDGARSpiderCompName.CIK_parse(), I have reserved a condition “if filling_type.startswith("13F-HR")” then “break”. If we need to load more previous reports, set a counter for this, or delete “break” then it can load all reports. All records will be stored into one .tvs file with different “filling_date”. 
2. How to deal with different 13F report formats: In EDGARSpiderCIK.html_file_flattener() and EDGARSpiderCompName.html_file_flattener(), I have reserved a method for parsing html file. If we have more formats besides XML and HTML, clearly we need to implement more flattener to handle.
3. Avoid duplicate methods and code: One of the major obstructs I meet is, I can’t really call EDGARSpiderCIK by EDGARSpiderCompName’s code due to Scrapy platform limit, this cause a large portion of methods and code in EDGARSpiderCompName are copied from EDGARSpiderCIK. A possible solution could be, we make a basic spider, and then both EDGARSpiderCIK and EDGARSpiderCompName can inherit from the basic spider. So they can share some common usage when crawling a same page. It will take time to refactor and test.
  
#### End