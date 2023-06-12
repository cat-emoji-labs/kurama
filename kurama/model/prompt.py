type_inference_prompt = """
Given these columns:
{columns}

And this example of a row:
{row}

Output a JSON where the keys are the names of each column, and the values are the values of the rows, corresponding to each column (infer the type).

For columns that are likely to be date-time objects, list the value as "datetime" instead.
"""

default_system_prompt = """
You are a helpful assistant. Keep your answers brief and concise.
"""

### SQL ###

sql_system_prompt = """
You are a data scientist writing PostgreSQL queries.

Never match literals for string type columns, always use the ILIKE keyword to find similar strings instead. 
Never group by columns previously matched with the ILIKE keyword. Instead, create and define a new, separate column and group by that column instead.
{date}
"""

sql_create_table_system_prompt = """
You are a data scientist writing PostgreSQL queries.

Infer the types for each column from the given row values.
Use snake_case for the column names.
Pay attention to columns that are likely to be date-time objects.
Do not specify precision for floating point values, use the FLOAT value instead.
Remember to include IF NOT EXISTS.
"""

sql_create_table_prompt = """
You are given the name of the table, the columns of the table, and an example row. Your job is to create a PostgreSQL Create Table statement matching the schema of the columns.

Table Name:
{table_name}

Columns:
{columns}

Row:
{row}

Delineate SQL with triple quotes (```).
"""

# QDecomp + InterCOL
# Exploring Chain-of-Thought Style Prompting for Text-to-SQL - https://arxiv.org/abs/2305.14215

sql_query_prompt = """
You are given the columns of the relevant table, your job is to create a SQL query that correctly answers the user question.

Columns:
{columns}

Question:
{query}

Decompose the question. Delineate SQL with triple quotes (```).
"""

retry_sql_query_prompt = """
Running that SQL query didn't work. Can you fix the error?

Error:
{error}
"""

### SQL ###

retrieval_prompt = """
Given a list of file names and descriptions, output the UUID of the file that can most likely be used to answer the query. If you're uncertain, please give your best answer.

The files are given in this format: UUID,name,description

Files:
{files}

Query:
{query}

Think step by step, and output the relevant UUID delineated with triple quotes (```).

Example output:
```UUID('342ac220-7134-4e0c-b452-c0842f19b44e')```
"""

tagging_prompt = """
Given the file name, columns, and first few rows of this CSV file, create up to 5 metadata tags that best describe what this file might be about.

File name:
{file_name}

Columns:
{columns}

Rows:
{rows}

Delimit each metadata tag with the ',' character.

Example output:
`employees,location,salary,hours`
"""
