from flask import render_template, redirect, url_for

from . import auth
from app.forms import FalloForm 


from Back import StorageProcessMsg

@auth.route('/aleph', methods=['get', 'post'])
def inicio():
    resultados = ['vacio']
    fallo_form = FalloForm()
    
    if fallo_form.validate_on_submit():
        # resultados = StorageProcessMsg.prueba()
        resultados = StorageProcessMsg.inicia('topo.txt')

        # return redirect(url_for('index'))
    
    contexto = {
        'fallo_form': fallo_form,
        'resultados': resultados
    }
    return render_template('index.html', **contexto)
