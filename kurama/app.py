from fastapi import FastAPI, UploadFile, File, Request
from kurama.database.utils import upload_csv, answer_query, transpose_df, delete_files
from kurama.database.database import PostgresDatabase
from kurama.config.environment import HOST, PORT
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import datetime
import re

app = FastAPI()

pg = PostgresDatabase()

# Add CORS middleware
# TODO: Just proxy all requests to this service from Go server and delete this later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload/{user_id}/{document_id}")
async def upload(user_id: str, document_id: str, csvFile: UploadFile = File(...)):
    try:
        # TODO: Implement ID-based tables/schemas
        # TODO: Handle file types other than CSV
        upload_csv(
            csv=csvFile.file,
            document_id=document_id,
            file_name=csvFile.filename.split(".")[0],
            pg=pg,
            user_id=user_id,
        )
        return {"message": "CSV file uploaded successfully"}
    except Exception as e:
        print(e)
        return {"error": str(e)}


@app.post("/ask/{user_id}")
async def ask(request: Request, user_id: str):
    body = await request.json()
    query = body.get("query")
    print("Query: ", query)

    try:
        result = answer_query(
            query,
            pg=pg,
            user_id=user_id,
            date=datetime.datetime.strptime("June 20th 2019", "%B %dth %Y"),
        )
        # Format results
        return {"message": "success", "data": result}
    except Exception as e:
        print(e)
        return {"error": str(e), "data": "Sorry, something went wrong. Please try again later."}


@app.post("/delete")
async def delete(request: Request):
    body = await request.json()
    user_id = body.get("user_id")
    document_ids = body.get("document_ids")
    try:
        delete_files(user_id=user_id, document_ids=document_ids, pg=pg)
        return {"message": "success"}
    except Exception as e:
        print(e)
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=int(PORT))
