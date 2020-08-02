from flask import (Flask,
                request,
                make_response,
                render_template,
                session,
                redirect,
                url_for
                )

from flask_wtf import FlaskForm
from wtforms.fields import DecimalField, IntegerField, SubmitField
from flask_bootstrap import Bootstrap


from Back import StorageProcessMsg



app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'SUPER SECRETO'



class  FalloForm(FlaskForm):
    """Formularios para el usuario  """
    nodos_fallo = IntegerField("Nodos que quieres que falleno")
    tiempo_fallo = DecimalField("Tiempo a cual falla")
    tiempo_recuperacion =  DecimalField ("Tiempo al que se recupera")
    submit = SubmitField('Enviar')




# @app.route('/')
# def index():
#     return render_template('index.html')


# @app.route('/aleph', methods = ['get', 'post'])
# def my_link():
#     # print('I got clicked!')
#     fallo_form = FalloForm()
#     resultados = ['vacio']
    
#     context = {
#         'prueba': "prueba",
#         'resultados': resultados
#     }
    
#     if fallo_form.validate_on_submit():
#         resultados = StorageProcessMsg.prueba()
#         print(resultados)
#         return redirect(url_for('index')
        
#     return render_template("index.html", **context)

    # return 'Click.'


@app.route('/')
def index():
    user_ip = request.remote_addr

    response = make_response(redirect('/index'))
    'crea una cookie'
    # response.set_cookie('user_ip', user_ip)
    session['user_ip'] = user_ip
    # Redirecciona a /hello
    return response


@app.route('/aleph', methods=['get', 'post'])
def hello():

    # Obtiene la direccion ip de las cookies del navegador
    # user_ip = request.cookies.get('user_ip')
    fallo_form = FalloForm()
    resultados = ['vacio']



    if fallo_form.validate_on_submit():
        resultados = StorageProcessMsg.prueba()
        print(resultados)
        # return redirect(url_for('hello'))
    context = {
                'prueba': "prueba",
                'resultados': resultados,
                'fallo_form': fallo_form
                }

    # metodo es render_template con jinja2 y la variable es user_ip.
    return render_template('index.html', **context)
    # **context es lo mismo que escribir context.user_ip, context.todos, etc.
    # return f'Tu direccion ip es {user_ip}'




# if __name__ == '__main__':
#     app.run()


# app.run(debug=True, port  =5000, host='0.0.0.0')
