from fastapi import FastAPI
import uvicorn

app = FastAPI(title="CICD Test API")


@app.get("/")
async def root():
    return {"message": "Hello from cicd-test!", "status": "ok"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
