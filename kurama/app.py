from fastapi import FastAPI, UploadFile, File, Request
from kurama.database.utils import (
    upload_csv,
    retrieve_pipeline_for_query,
    retrieve_best_collection_name,
)
from kurama.database.database import NLPDatabase
from kurama.config.environment import HOST, PORT
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import datetime

app = FastAPI()

db = NLPDatabase()

# Add CORS middleware
# TODO: Proxy all requests from Go server and delete this later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload/{user_id}/{collection_id}")
async def upload(user_id: str, collection_id: str, csvFile: UploadFile = File(...)):
    try:
        # TODO: Handle file types other than CSV
        upload_csv(
            csv=csvFile.file,
            collection=db.get_collection(user_id=user_id, collection_id=collection_id),
        )
        return {"message": "CSV file uploaded successfully"}
    except Exception as e:
        print(e)


@app.post("/ask/{user_id}")
async def ask(request: Request, user_id: str):
    body = await request.json()
    # TODO: Add an agentic routing layer
    query = body.get("query")
    print("Query", query)
    # Multi-collection schema retrieval
    schemas = db.get_all_schemas(user_id=user_id)
    collection_id = retrieve_best_collection_name(schemas=schemas, query=query)

    columns = db.get_collection_schema(user_id=user_id, collection_id=collection_id)

    # Retrieve and execute pipeline
    pipeline = retrieve_pipeline_for_query(
        columns=columns,
        query=query,
        date=datetime.datetime.strptime("June 20th 2019", "%B %dth %Y"),
    )
    documents = db.execute_pipeline(
        pipeline=pipeline,
        collection=db.get_collection(user_id=user_id, collection_id=collection_id),
    )
    print("Result", documents)
    doc_json = documents.head().to_dict()
    cols, rows = doc_json.keys(), [d.values() for d in doc_json.values()]
    res = []
    transposed_rows = [list(x) for x in zip(*rows)]
    for row in transposed_rows:
        obj = {}
        for col, val in zip(cols, row):
            obj[col] = val
        res.append(obj)
    return {"message": "success", "data": res}


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=int(PORT))
