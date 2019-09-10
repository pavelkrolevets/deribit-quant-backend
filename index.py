from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import BaseConfig
from flask_bcrypt import Bcrypt
# from flask_uploads import UploadSet, IMAGES, configure_uploads

UPLOAD_FOLDER = '/Users/pavelkrolevets/WebStormProjects/tokenizer-backend/static'

app = Flask(__name__, static_folder="./static/dist", template_folder="./static")
app.config.from_object(BaseConfig)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# # Configure the image uploading via Flask-Uploads
# images = UploadSet('images', IMAGES)
# configure_uploads(app, images)
