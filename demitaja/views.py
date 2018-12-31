from demitaja import app


@app.route('/')
def home():
    return 'Hello world!'
