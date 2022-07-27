import uvicorn
from fastapi import FastAPI
from notecoin.coins.server.download import DownloadServer

app = FastAPI()

app.include_router(DownloadServer())


uvicorn.run(app, host='0.0.0.0', port=8451)
