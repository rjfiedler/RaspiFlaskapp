from flask_wtf import FlaskForm
from wtforms import IntegerField, DecimalField, StringField, PasswordField, SubmitField, DateTimeField
from wtforms.validators import DataRequired

class WateringForm(FlaskForm):
    wateringfrequency = IntegerField('Frequency', validators=[DataRequired()])
    wateringduration = DecimalField('Duration', places=1, validators=[DataRequired()])
    wateringzone = IntegerField('Zone', validators=[DataRequired()])
    submit = SubmitField('Submit')

class PlotForm(FlaskForm):
	startdatetime = StringField('Start Datetime', validators=[DataRequired()], render_kw={"placeholder": "mm-dd-HH-MM"})
	enddatetime = StringField('End Datetime', validators=[DataRequired()], render_kw={"placeholder": "mm-dd-HH-MM"})
	submit = SubmitField('Submit')
	
class DailyLogForm(FlaskForm):
	PHreading = DecimalField('PH Reading', places=2, validators=[DataRequired()], render_kw={"placeholder": "ex: 753"})
	TDSreading = IntegerField('TDS Reading', validators=[DataRequired()], render_kw={"placeholder": "ex: 6.09"})
	submit = SubmitField('Submit')
