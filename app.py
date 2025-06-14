from flask import Flask
from limiter.helpers import ratelimit

app = Flask(__name__)


@app.route('/')
@ratelimit(key='ip', rate='3/m', mode='fixed')
def home():
    return "Welcome to the homepage."


@app.route('/api')
@ratelimit(key='ip', rate='10/m', mode='token')
def api_data():
    return "API response"


if __name__ == '__main__':
    app.run(debug=True)
