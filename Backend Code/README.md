# Overview

The backend part is built up in two parts. You have the model training part in de `training` folder and the api endpoints in the `fastapi` folder.

# Running application

Running this application can be done in multipe ways.

## Docker (recommended)

Firstly you will need to have installed Docker on your system. Then run the following commands:

```bash
docker build . -t hyacinth-location-backend
```

This will build the container in two steps. The first step will train the model using the provided images and then export this. The second step will use the exported model to set up a FastAPI backend endpoint which the frontend application can make calls to.

```bash
docker run -p 8000:8000 hyacinth-location-backend
```

This will start the application and expose the FastAPI endpoints on port 8000.

## Manual (for debugging and development)

For manual installation follow the underlying README files in both subdirectories.
