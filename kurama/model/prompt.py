type_inference_prompt = """
Given these columns:
{columns}

And this example of a row:
{row}

Output a JSON where the keys are the names of each column, and the values are the values of the rows, corresponding to each column (infer the type).

For columns that are likely to be date-time objects, list the value as "datetime" instead.
"""

pipeline_prompt = """
You are a data scientist writing pipeline queries in MongoDB. You are only capable of communicating with a list of valid JSON, and no other text.

Today's date is {date}. Output a list of Python-compatible JSON objects representing the correct MongoDB pipeline that answers the query. 

Never match literals for string type columns, always use Regex to find similar strings instead.
Always represent dates and times as Python datetime objects (datetime.datetime)

Columns:
{columns}

Query:
{query}
"""
