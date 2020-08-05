from flask_wtf import FlaskForm
from wtforms.fields import DecimalField, IntegerField, SubmitField, FileField
from wtforms.validators import Optional


class FalloForm(FlaskForm):
    """Formularios para el usuario  """
    nodos_fallo = IntegerField("Nodos que quieres que fallen", [Optional()])
    tiempo_fallo = DecimalField("Tiempo a cual falla")
    tiempo_recuperacion = DecimalField("Tiempo al que se recupera")
    topologia = FileField("Dame la topologia")

    submit = SubmitField('Enviar')
