#!/usr/bin/env python3

from app import create_app

server = create_app()

if __name__ == "__main__":
    server.run("0.0.0.0")
