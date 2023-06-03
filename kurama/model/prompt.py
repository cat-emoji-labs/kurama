type_inference_prompt = """
Given these columns:
{columns}

And this example of a row:
{row}

Output a JSON where the keys are the names of each column, and the values are the values of the rows, corresponding to each column (infer the type).

For columns that are likely to be date-time objects, list the value as "datetime" instead.
"""

### SQL ###

sql_system_prompt = """
You are a data scientist writing PostgreSQL queries.

Never match literals for string type columns, always use the ILIKE keyword to find similar strings instead. 
Never group by columns previously matched with the ILIKE keyword. Instead, create and define a new, separate column and group by that column instead.
If you need the date to answer the question, today's date is {date}.
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

Columns:
{columns}

Row:
{row}

Table Name:
{name}

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
