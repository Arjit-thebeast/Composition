FROM python:3.12

# Install dependencies and customize sandbox
RUN apt update \
    && apt install sudo

# Install composio
RUN pip install composio-core==0.3.18rc2 fastapi

# Define entry point
ENTRYPOINT [ "composio",  "serve", "-h", "0.0.0.0" ]
