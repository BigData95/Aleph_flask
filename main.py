from flask import (Flask,
                request,
                make_response,
                render_template,
                session,
                redirect,
                url_for
                )

from flask_wtf import FlaskForm
from wtforms.fields import DecimalField, IntegerField, SubmitField, FileField
from wtforms.validators import Optional

from flask_bootstrap import Bootstrap


from Back import StorageProcessMsg



app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'SUPER SECRETO'



class  FalloForm(FlaskForm):
    """Formularios para el usuario  """
    nodos_fallo = IntegerField("Nodos que quieres que fallen", [Optional()])
    tiempo_fallo = DecimalField("Tiempo a cual falla")
    tiempo_recuperacion =  DecimalField ("Tiempo al que se recupera")
    topologia = FileField("Dame la topologia")
    
    
    submit = SubmitField('Enviar')



@app.route('/')
def index():
    response = make_response(redirect('/aleph'))
    return response


@app.route('/aleph', methods=['get', 'post'])
def hello():

    fallo_form = FalloForm()
    resultados = ['vacio']
    input_fallo = None

    if fallo_form.validate_on_submit():
        # resultados = StorageProcessMsg.prueba()
        resultados = StorageProcessMsg.prueba()
        
        #! Con el atributo .data podemos acceder a los datos en las fomr
        input_fallo = fallo_form.nodos_fallo.data
        print(input_fallo)
        print(resultados)
        # return redirect(url_for('hello'))
    context = {
                'prueba': "prueba",
                'resultados': resultados,
                'fallo_form': fallo_form
                }
    return render_template('index.html', **context)




if __name__ == '__main__':
    app.run(debug=True)


# app.run(debug=True, port  =5000, host='0.0.0.0')






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
