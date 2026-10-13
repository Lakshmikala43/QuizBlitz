from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.repositories.user_repo import UserRepository

user_repo = UserRepository()


class LoginForm(FlaskForm):
    """User login form."""

    username_or_email = StringField(
        "Username or Email",
        validators=[DataRequired(message="Please provide your username or email address.")],
        render_kw={"placeholder": "Enter your username or email", "autocomplete": "username"},
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(message="Password is required.")],
        render_kw={"placeholder": "••••••••", "autocomplete": "current-password"},
    )
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In to Battle")


class RegisterForm(FlaskForm):
    """Player registration form."""

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=30, message="Username must be between 3 and 30 characters."),
        ],
        render_kw={"placeholder": "Choose a warrior callsign", "autocomplete": "username"},
    )
    email = StringField(
        "Email Address",
        validators=[DataRequired(), Email(message="Please enter a valid email address.")],
        render_kw={"placeholder": "you@example.com", "autocomplete": "email"},
    )
    display_name = StringField(
        "Display Name (Optional)",
        validators=[Length(max=30)],
        render_kw={"placeholder": "In-game display name"},
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6, max=100, message="Password must be at least 6 characters."),
        ],
        render_kw={"placeholder": "••••••••", "autocomplete": "new-password"},
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
        render_kw={"placeholder": "••••••••", "autocomplete": "new-password"},
    )
    submit = SubmitField("Create Account & Join Arena")

    def validate_username(self, username):
        if user_repo.get_by_username(username.data.strip()):
            raise ValidationError("This callsign is already taken. Please choose another.")

    def validate_email(self, email):
        if user_repo.get_by_email(email.data.strip()):
            raise ValidationError("An account with this email address already exists.")


class ForgotPasswordForm(FlaskForm):
    """Password recovery request form."""

    email = StringField(
        "Registered Email Address",
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Enter your registered email"},
    )
    submit = SubmitField("Generate Recovery Link")


class ResetPasswordForm(FlaskForm):
    """Password reset form using token."""

    password = PasswordField(
        "New Password",
        validators=[DataRequired(), Length(min=6, max=100)],
        render_kw={"placeholder": "New password (min 6 characters)"},
    )
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
        render_kw={"placeholder": "Confirm new password"},
    )
    submit = SubmitField("Update Password")


class ChangePasswordForm(FlaskForm):
    """In-app password change form for authenticated players."""

    current_password = PasswordField(
        "Current Password",
        validators=[DataRequired()],
        render_kw={"placeholder": "Current password"},
    )
    new_password = PasswordField(
        "New Password",
        validators=[DataRequired(), Length(min=6, max=100)],
        render_kw={"placeholder": "New password (min 6 characters)"},
    )
    confirm_new_password = PasswordField(
        "Confirm New Password",
        validators=[DataRequired(), EqualTo("new_password", message="Passwords must match.")],
        render_kw={"placeholder": "Confirm new password"},
    )
    submit = SubmitField("Save New Password")
