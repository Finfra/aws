# Use the official Ubuntu base image
FROM ubuntu:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip curl && \
    apt-get clean

# Install web.py using pip
RUN pip3 install --break-system-packages web.py

# Create /df directory and copy start.py
WORKDIR /
COPY start.py /start.py

# Make start.py executable
RUN chmod +x /start.py

# Command to run start.py on container start
CMD ["python3", "/start.py"]