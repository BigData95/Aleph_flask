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


@app.route('/aleph', methods=['get', 'post'])
def hello():

    # fallo_form = FalloForm()
    resultados = ['vacio']
    # input_fallo = None

    # if fallo_form.validate_on_submit():
    #     # resultados = StorageProcessMsg.prueba()
    #     resultados = StorageProcessMsg.prueba()
        
    #     #! Con el atributo .data podemos acceder a los datos en las fomr
    #     input_fallo = fallo_form.nodos_fallo.data
    #     print(input_fallo)
    #     print(resultados)
    #     # return redirect(url_for('hello'))
    context = {
                'prueba': "prueba",
                'resultados': resultados,
                # 'fallo_form': fallo_form
                }
    return render_template('index.html', **context)



if __name__ == '__main__':
    app.run(debug=True)
