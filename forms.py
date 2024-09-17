from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, RadioField, IntegerRangeField, SelectField, IntegerField, FileField
from wtforms.validators import InputRequired, EqualTo, NumberRange, Length

class RegistrationForm(FlaskForm):
    fname = StringField("FIRST NAME", validators=[InputRequired("Please enter your first name!")])
    lname = StringField("LAST NAME", validators=[InputRequired("Please enter your last name")])
    email = StringField("EMAIL", validators=[InputRequired("Please enter your email!")])
    password = PasswordField("PASSWORD", validators=[InputRequired("Please enter your password!")])
    confirm_password = PasswordField("CONFIRM PASSWORD", validators=[InputRequired(message="Please confirm your password!"), EqualTo("password", "Passwords do not match!")])
    submit = SubmitField("REGISTER")

class LoginForm(FlaskForm):
    email = StringField("EMAIL", validators=[InputRequired("Please enter your email!")])
    password = PasswordField("PASSWORD", validators=[InputRequired("Please enter your password!")])
    submit = SubmitField("LOG IN")

class VehicleFilter(FlaskForm):
    brand = RadioField("Brands", choices=["All"], default="All")
    price_range = IntegerRangeField(default=0)
    sort_by = SelectField("Sort By", choices = [
                                                "Alphabetical: A -> Z",
                                                "Alphabetical: Z -> A",
                                                "Price: High -> Low",
                                                "Price: Low -> High"
                                                ], default="Alphabetical: A -> Z")
    submit = SubmitField("Filter")

class InsertCar(FlaskForm):
    brand = StringField("Brand", validators=[InputRequired("Please enter the brand!")])
    model = StringField("Model", validators=[InputRequired("Please enter the model!")])
    price = IntegerField("Price", validators=[InputRequired("Please enter the price!"), NumberRange(0)])
    description = StringField("Description (Max Length: 400)", validators=[InputRequired("Please enter the description!"), Length(0,400)])
    image = FileField("File (optional)")
    submit = SubmitField("INSERT")

class DeleteCar(FlaskForm):
    brand = StringField("Brand", validators=[InputRequired("Please enter the brand!")])
    model = StringField("Model", validators=[InputRequired("Please enter the model!")])
    submit = SubmitField("DELETE")

class DetailsForm(FlaskForm):
    days = IntegerField("Days", validators=[NumberRange(0)])
    submit = SubmitField("Book Now")

class ReviewForm(FlaskForm):
    content = StringField("REVIEW", validators=[InputRequired("Please enter a message!"), Length(max=1000)])
    submit = SubmitField("LEAVE REVIEW")

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("OLD PASSWORD", validators=[InputRequired("The old password must be entered!")])
    new_password = PasswordField("NEW PASSWORD", validators=[InputRequired("Please enter the new password!")])
    confirm_password = PasswordField("CONFIRM NEW PASSWORD", validators=[InputRequired("Please confirm the new password!"), EqualTo('new_password', 'Passwords do not match!')])
    submit = SubmitField("CHANGE PASSWORD")

class UpdateCarForm(FlaskForm):
    brand = StringField("Brand", validators=[InputRequired("Please enter the brand!")])
    model = StringField("Model", validators=[InputRequired("Please enter the model!")])
    price = IntegerField("Price", validators=[InputRequired("Please enter the old price!"), NumberRange(0)])
    new_price = IntegerField("New Price", validators=[InputRequired("Please enter the new price!"), NumberRange(0)])
    new_image = FileField("New Profile Picture")
    submit = SubmitField("UPDATE CAR")

class ChangePFPForm(FlaskForm):
    pfp = FileField("Change Profile Picture", validators=[InputRequired("You must choose a file!")])
    submit = SubmitField("Change")