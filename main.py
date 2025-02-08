from src.core.asgi import get_app

__all__ = ("app",)

app = get_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
