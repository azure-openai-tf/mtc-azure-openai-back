from source.api import fastapi


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(fastapi, host="127.0.0.1", port=5000)
