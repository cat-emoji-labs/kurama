from fastapi import FastAPI, UploadFile, File, Request
from kurama.database.utils import upload_csv, retrieve_pipeline_for_query
from kurama.database.database import NLPDatabase
import uvicorn

# Create an instance of the FastAPI application
app = FastAPI()
# Create db connection
db = NLPDatabase()


# Define a simple route
@app.get("/")
def read_root():
    return {"Hello": "World"}


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


@app.post("/ask")
async def ask(request: Request):
    body = await request.json()
    user_id, collection_id, query = body.get("userID"), body.get("collectionID"), body.get("query")
    pipeline = retrieve_pipeline_for_query(query=query)
    pass


# Run the application with uvicorn server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)

# time.sleep(2)
# pipeline = retrieve_pipeline_for_query(
#     "Order ID,Product,Quantity Ordered,Price Each,Order Date,Purchase Address",
#     "What is the highest price product?",
# )

# print(pipeline)

# for document in collection.aggregate(pipeline):
#     print(document)
