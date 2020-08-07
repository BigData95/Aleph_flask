from flask import render_template, redirect, url_for, request

from . import auth
from app.forms import FalloForm, ClearForm 


from Back import StorageProcessMsg

@auth.route('/aleph', methods=['GET', 'POST'])
def inicio():
    resultados = ['vacio']
    fallo_form = FalloForm()    
    clear_form = ClearForm()

    # if request.method == 'POST' and fallo_form.validate():
    #     resultados = StorageProcessMsg.inicia(
    #         fallo_form.nodos_fallo.data,
    #         fallo_form.tiempo_fallo.data,
    #         fallo_form.tiempo_recuperacion.data
    #         )
    #     print(fallo_form.nodos_fallo.data)

    if fallo_form.validate_on_submit():
        if not fallo_form.limpiar.data:
            resultados = StorageProcessMsg.inicia(
                fallo_form.nodos_fallo.data,
                fallo_form.tiempo_fallo.data,
                fallo_form.tiempo_recuperacion.data
                )
        print(fallo_form.limpiar.data)
        # return  redirect(url_for('auth.inicio'))

    contexto = {
        'fallo_form': fallo_form,
        'resultados': resultados,
        'clear_form': clear_form
    }
    return render_template('index.html', **contexto)
    
    
    # return render_template('index.html', **contexto)

@auth.route('/clean')
def clean():
    
    contexto = {
        'resultados': ['vacio']
    }
    
    return render_template('index.html', **contexto)
