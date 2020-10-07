from flask import (
    make_response,
    redirect,
)

from app import create_app

app = create_app()


@app.route('/')
def index():
    response = make_response(redirect('/aleph/main'))
    return response


if __name__ == '__main__':
    app.run()
