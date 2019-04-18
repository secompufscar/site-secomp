#!/usr/bin/env python3

import os
from app import create_app

if __name__ == '__main__':
    config = os.getenv('FLASK_CONFIGURATION', 'default')
    app = create_app(config)
    app.run('0.0.0.0')

