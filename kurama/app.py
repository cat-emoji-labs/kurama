from fastapi import FastAPI, UploadFile, File, Request
from kurama.database.utils import (
    upload_csv,
    retrieve_df_for_query,
    transpose_df,
    get_schema_name_from_user_id,
)
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


@app.post("/upload/{user_id}/{collection_id}")
async def upload(user_id: str, collection_id: str, csvFile: UploadFile = File(...)):
    try:
        # TODO: Implement ID-based tables/schemas
        # TODO: Handle file types other than CSV
        upload_csv(
            csv=csvFile.file,
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
        df = retrieve_df_for_query(
            query,
            pg=pg,
            user_id=user_id,
            date=datetime.datetime.strptime("June 20th 2019", "%B %dth %Y"),
        )
        # Format results
        transposed_df = transpose_df(df=df)
        return {"message": "success", "data": transposed_df}
    except Exception as e:
        print(e)
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=int(PORT))
