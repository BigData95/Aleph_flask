from flask import (
                request,
                make_response,
                render_template,
                session,
                redirect,
                url_for
                )


from flask_bootstrap import Bootstrap

from app import create_app
from app.forms import FalloForm

app = create_app()

@app.route('/')
def index():
    response = make_response(redirect('/auth/aleph'))
    return response

if __name__ == '__main__':
    app.run(debug=True)
