# from app import create_app

# app = create_app()

# if __name__ == '__main__':
#     app.run(debug=True)


import logging
from app import create_app
import os

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
logger.debug("Loading WSGI application")

try:
    app = create_app()
    logger.debug("WSGI application created successfully")
except Exception as e:
    logger.error(f"Failed to create WSGI application: {e}")
    raise

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)