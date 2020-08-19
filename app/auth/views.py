from flask import render_template

from . import auth
from app.forms import FalloForm  # , ClearForm

from Back import StorageProcessMsg, salidas


@auth.route('/aleph', methods=['GET', 'POST'])
def inicio():
    resultados = ['x']
    fallo_form = FalloForm()

    if fallo_form.validate_on_submit():
        if not fallo_form.limpiar.data:
            resultados = StorageProcessMsg.inicia(
                fallo_form.nodos_fallo.data,
                fallo_form.tiempo_fallo.data,
                fallo_form.tiempo_recuperacion.data
            )
        else:
            resultados = salidas.clear()
            # return  redirect(url_for('auth.inicio'))
        print(fallo_form.limpiar.data)

    contexto = {
        'fallo_form': fallo_form,
        'resultados': resultados,
    }
    return render_template('index.html', **contexto)

    # return render_template('index.html', **contexto)


@auth.route('/clean')
def clean():
    contexto = {
        'resultados': ['vacio']
    }

    return render_template('index.html', **contexto)
