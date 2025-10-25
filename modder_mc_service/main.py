import uvicorn
import os


def serve():
    """
    main function to run the FastAPI app inside uvicorn server.
    """
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("modder_mc_service.api.api:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    # for debugging purposes this is an entry point
    # When serving use the poetry script command 'serve'
    serve()