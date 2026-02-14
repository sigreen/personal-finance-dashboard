Create me step-by-step plan to build a personal finance dashboard.
The user will download their banking/brokerage/credit card statements 
in CSV format and place them in a directory.  From the web browser,
the user can initiate an import of the financial data, which will
initiate an ETL process to import the data into a postgres database.  
The database and applications will run on kubernetes, running locally on minikube.  
Once the data is imported and normalized, the application will expose an MCP
server that can be queried by Claude or any other model. Output the plan to spec.model
in this folder.