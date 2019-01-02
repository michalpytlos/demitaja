from flask import Flask


app = Flask(__name__, instance_relative_config=True)

# Configure the app
app.config.from_object('demitaja.default_settings.Config')

import demitaja.views
