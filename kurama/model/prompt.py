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

Never match literals for string type columns, always use the LIKE keyword to find similar strings instead.
Never group by the original column if it was matched with the LIKE keyword. Instead, create and define a new one.
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

Delineate each SQL query with triple quotes (```).
"""

# QDecomp + InterCOL
# Exploring Chain-of-Thought Style Prompting for Text-to-SQL - https://arxiv.org/abs/2305.14215

sql_query_prompt = """
You are given the columns of the relevant table, your job is to create a SQL query that correctly answers the user question.

Columns:
{columns}

Question:
{query}

Decompose the question. Delineate each SQL query with triple quotes (```).
"""

retry_sql_query_prompt = """
Running that SQL query didn't work. Can you fix the error?

Error:
{error}
"""

### SQL ###

pipeline_prompt = """
You are a data scientist writing pipeline queries in MongoDB. You are only capable of communicating with a list of valid JSON, and no other text.

Today's date is {date}.
Never match literals for string type columns, always use Regex to find similar strings instead.
Always represent dates and times as Python objects (datetime.datetime). Never use ISODate objects.

Think step by step. Output a list of Python-compatible JSON objects representing the correct MongoDB pipeline that answers the query. 

Columns:
{columns}

Query:
{query}
"""

match_step_prompt = """
You are a data scientist writing pipeline queries in MongoDB. You are only capable of communicating with a valid JSON, and no other text.

Today's date is {date}. Think step by step and output a Python-compatible JSON object representing the correct $match MongoDB pipeline that answers the query.

Always use Regex to find similar strings instead of matching string literals.
Always represent dates and times as Python datetime objects (datetime.datetime). Never use ISODate objects.
Pay extra attention for queries where you're asked for a comparison, and use the OR conditional wherever appropriate.

Columns:
{columns}

Query:
{query}
"""

group_step_prompt = """
You are a data scientist writing pipeline queries in MongoDB. You are only capable of communicating with a valid JSON, and no other text.

Today's date is {date}. You are given the previous $match step. Think step by step and output a Python-compatible JSON object representing the correct $group MongoDB pipeline that answers the user query.

Do not repeat any work that has already been done for you in the previous $match step.
Always use None instead of null when grouping by the _id column.

$match step:
{match_step}

Columns:
{columns}

Query:
{query}
"""

etc_step_prompt = """
You are a data scientist writing pipeline queries in MongoDB. You are only capable of communicating with valid JSON, and no other text.

Today's date is {date}. You are given the previous $match and $group steps. Think step by step and output a Python-compatible JSON object representing the remaining $project MongoDB pipeline step that answers the user query.

Do not add unnecessary or additional columns to the $project step which directly answer the query, only output the relevant columns and allow the user to decide for themselves.

$match step:
{match_step}

$group step:
{group_step}

Columns:
{columns}

Query:
{query}
"""

schema_prompt = """
You are a helpful assistant. You are only capable of communicating with a collection name, and no other text.

Given MongoDB collection names and their corresponding schemas (represented as JSON key value pairs), output as a string which collection name is best suited to answer the user query.
Output only the collection name and no other text. If you're not sure, just output the first collection name.

Schemas:
{schemas}

User Query:
{query}
"""
