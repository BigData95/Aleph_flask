from flask_wtf import FlaskForm
from wtforms.fields import (DecimalField, 
                            IntegerField, 
                            SubmitField, FileField, 
                            BooleanField
                            )
from wtforms.validators import Optional, DataRequired


class FalloForm(FlaskForm):
    """Formularios para el usuario  """
    nodos_fallo = IntegerField("Nodos que quieres que fallen", [Optional()] )#, default=-1)
    tiempo_fallo = DecimalField("Tiempo a cual falla",[ Optional() ] )
    tiempo_recuperacion = DecimalField("Tiempo al que se recupera", [Optional()])
    # topologia = FileField("Dame la topologia", [Optional()])
    limpiar = BooleanField("Clear",default=True, false_values=(False, 'false', 0, '0'))
    submit = SubmitField('Enviar')



# class ClearForm(FlaskForm):
#     clear = SubmitField('Limpiar')