from flask_wtf import FlaskForm
from wtforms.fields import (DecimalField, 
                            IntegerField, 
                            SubmitField, 
                            FileField,
                            BooleanField,
                            StringField
                            
                            )
from wtforms.validators import Optional, DataRequired, ValidationError, Regexp


import re

def listas_enteros(form, field):
        messege = 'Introduce solo numeros enteros'
        decimal_error = 'No se permiten decimales'
        numeros = re.compile('^[1-9]+[0-9]*')

        if numeros.match(field.data):
            if "." in field.data:
                raise ValidationError(decimal_error)
        else:
            raise ValidationError(messege)

def lista_decimales(form, field):
    messege = "Introduce solo numeros decimales"
    decimales = re.compile('^[0-9]*.+[0-9]*')
        
class FalloForm(FlaskForm):
    """Formularios para el usuario  """
    nodos_fallo = StringField("Nodos que quieres que fallen", [
        listas_enteros,
        # Regexp('^[1-9]+[0]*', message="Por favor introduce una lista de numeros"),
        Optional()
        ])

    tiempo_fallo = DecimalField("Tiempo a cual falla", [DataRequired()])
    tiempo_recuperacion = DecimalField("Tiempo al que se recupera", [Optional()])
    # topologia = FileField("Dame la topologia", [Optional()])
    limpiar = BooleanField("Clear", default=True, false_values=(False, 'false', 0, '0'))
    submit = SubmitField('Enviar')
