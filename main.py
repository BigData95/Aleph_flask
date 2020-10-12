from flask import (
    make_response,
    redirect,
    render_template
)

from app import create_app

app = create_app()


@app.route('/')
def index():
    response = make_response(redirect('/aleph/main'))
    return response


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', error=error)


@app.errorhandler(500)
def internal_error(error):
    return  render_template('500.html',error=error)


if __name__ == '__main__':
    app.run()
