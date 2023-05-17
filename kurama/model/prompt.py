type_inference_prompt = """
Given these columns:
{columns}

And this example of a row:
{row}

Output a JSON where the keys are the names of each column, and the values are the values of the rows, corresponding to each column (infer the type).
"""

pipeline_prompt = """
You are a data scientist writing pipeline queries in MongoDB. You are only capable of communicating with valid JSON, and no other text.

Output a list of JSON objects representing the correct MongoDB pipeline that answers the query.

Columns:
{columns}

Query:
{query}

Example:

Columns:
Order ID,Product,Quantity Ordered,Price Each,Order Date,Purchase Address

Query:
What product is the most ordered?

Output:
[
    {{
        '$group': {{
            '_id': '$Product',
            'totalOrdered': {{ '$sum': '$Quantity Ordered' }}
        }}
    }},
    {{
        '$sort': {{
            'totalOrdered': -1
        }}
    }},
    {{
        '$limit': 1
    }}
]
"""
