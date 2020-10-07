from flask import render_template

from . import aleph
from app.forms import FalloForm

from back.aleph import salidas, Aleph_main as Aleph


@aleph.route('/simulador', methods=['GET', 'POST'])
def simulador():
    resultados = ['x']
    fallo_form = FalloForm()

    if fallo_form.validate_on_submit():
        if not fallo_form.limpiar.data:
            resultados = Aleph.inicia(
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
    return render_template('aleph_storage.html', **contexto)

    # return render_template('aleph_storage.html', **contexto)




@aleph.route('/main', methods=['GET','POST'])
def main():
    return render_template('main.html')