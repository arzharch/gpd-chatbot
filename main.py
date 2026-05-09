from fastapi import FastAPI


app = FastAPI()


@app.post("/chat")
async def chat_reply():


    return {"dummy"}