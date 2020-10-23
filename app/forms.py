# De Flask
from flask_wtf import FlaskForm
from wtforms.fields import (
    SubmitField,
    BooleanField,
    StringField,
    IntegerField
    # FileField,
)
from wtforms.validators import ValidationError, DataRequired, Optional, NumberRange


# De Aleph
from back.aleph.config import Config

# Utilidades
import re


class RequiredIf(DataRequired):
    """
    Validator which makes a field required if another field is set and has a truthy value.
    """
    field_flags = ('requiredif',)

    def __init__(self, other_field_name, message=None):
        DataRequired.__init__(self)
        self.other_field_name = other_field_name
        self.message = message

    def __call__(self, form, field):
        other_field = form[self.other_field_name]
        if other_field is None:
            raise Exception('no field named "%s" in form' %
                            self.other_field_name)
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)


def listas_enteros(form, field):
    messege = 'Introduce solo numeros enteros.'
    decimal_error = 'No se permiten decimales.'
    numeros = re.compile('^([1-9]+[0-9]*-*,* *)*$')

    if numeros.match(field.data):
        if "." in field.data:
            raise ValidationError(decimal_error)
    else:
        raise ValidationError(messege)


def lista_decimales(form, field):
    messege = "Introduce solo numeros decimales."
    error_decimal = "Error en los decimales."
    decimales = re.compile(r'([0-9]*\.?[0-9]+-*,* *)|([1-9]+[0-9]*-*,* *)*')
    bad_decimal = re.compile(r'\d*\.+\d*\.|[a-zA-Z]')
    if decimales.match(field.data):
        if bad_decimal.search(field.data):
            raise ValidationError(error_decimal)
    else:
        raise ValidationError(messege)


class FalloForm(FlaskForm):
    nodos_fallo = StringField("Nodos que quieres que fallen", [
        listas_enteros,
        RequiredIf('tiempo_fallo'),
        RequiredIf('tiempo_recuperacion')
    ])
    tiempo_fallo = StringField("Tiempo a cual falla", [
        lista_decimales,
        RequiredIf('nodos_fallo'),
        RequiredIf('tiempo_recuperacion')
    ])
    tiempo_recuperacion = StringField("Tiempo que pasa despues del fallo para recuperarse.", [
        lista_decimales,
        RequiredIf('nodos_fallo'),
        RequiredIf('tiempo_fallo')
    ])
    nodo_selecionado_1 = IntegerField("Id nodo elegido por oraculo (Copy=0)", [
        RequiredIf('nodo_selecionado_2'),
        RequiredIf('nodo_selecionado_3'),
        NumberRange(Config.NODO_SERVER_LOWER, Config.NODO_SERVER_UPPER,
                    f"Debe estar entre {Config.NODO_SERVER_LOWER} y {Config.NODO_SERVER_UPPER}"),
        Optional()
        ])
    nodo_selecionado_2 = IntegerField("Id nodo elegido por oraculo (Copy=1)", [
        RequiredIf('nodo_selecionado_1'),
        RequiredIf('nodo_selecionado_3'),
        NumberRange(Config.NODO_SERVER_LOWER, Config.NODO_SERVER_UPPER,
                    f"Debe estar entre {Config.NODO_SERVER_LOWER} y {Config.NODO_SERVER_UPPER}"),
        Optional()
        ])
    nodo_selecionado_3 = IntegerField("Id nodo elegido por oraculo (Copy>2)", [
        RequiredIf('nodo_selecionado_1'),
        RequiredIf('nodo_selecionado_2'),
        NumberRange(Config.NODO_SERVER_LOWER, Config.NODO_SERVER_UPPER,
                    f"Debe estar entre {Config.NODO_SERVER_LOWER} y {Config.NODO_SERVER_UPPER}"),
        Optional()
        ])

    # topologia = FileField("Dame la topologia", [Optional()])
    limpiar = BooleanField("Clear", default=True, false_values=(False, 'false', 0, '0'))
    submit = SubmitField('Enviar')
