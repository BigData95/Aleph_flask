from flask import render_template

from . import aleph
from app.forms import FalloForm

from back.aleph import salidas, Aleph_main as Aleph
from back.aleph.config import Config

@aleph.route('/simulador', methods=['GET', 'POST'])
def simulador():
    resultados = ['x']
    fallo_form = FalloForm()

    if fallo_form.validate_on_submit():
        if not fallo_form.limpiar.data:
            resultados = Aleph.inicia(
                fallo_form.nodos_fallo.data,
                fallo_form.tiempo_fallo.data,
                fallo_form.tiempo_recuperacion.data,
                fallo_form.nodo_selecionado_1.data,
                fallo_form.nodo_selecionado_2.data,
                fallo_form.nodo_selecionado_3.data
            )
        else:
            resultados = salidas.clear()
            # return  redirect(url_for('auth.inicio'))
        print(fallo_form.limpiar.data)
        
    instrucciones = {
        'id_cliente': Config.NODO_CLIENTE,
        'id_proxy_lower': Config.NODO_PROXY_LOWER,
        'id_proxy_upper': Config.NODO_PROXY_UPPER,
        'id_server_lower': Config.NODO_SERVER_LOWER,
        'id_server_upper': Config.NODO_SERVER_UPPER
        }

    contexto = {
        'fallo_form': fallo_form,
        'resultados': resultados,
        'instrucciones': instrucciones
    }
    return render_template('aleph_storage.html', **contexto)

    # return render_template('aleph_storage.html', **contexto)




@aleph.route('/main', methods=['GET','POST'])
def main():
    return render_template('main.html')