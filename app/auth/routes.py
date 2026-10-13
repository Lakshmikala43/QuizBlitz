from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.auth.forms import (
    LoginForm,
    RegisterForm,
    ForgotPasswordForm,
    ResetPasswordForm,
)
from app.auth.services import AuthService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """User authentication view."""
    if current_user.is_authenticated:
        return redirect(url_for("players.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        success, message, user = AuthService.authenticate_user(
            form.username_or_email.data,
            form.password.data,
        )
        if success and user:
            login_user(user, remember=form.remember_me.data)
            flash(f"Welcome back, {user.effective_display_name}! Ready for battle.", "success")
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            return redirect(url_for("players.dashboard"))
        else:
            flash(message, "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """New player registration view."""
    if current_user.is_authenticated:
        return redirect(url_for("players.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        success, message, user = AuthService.register_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            display_name=form.display_name.data,
        )
        if success and user:
            login_user(user)
            flash(message, "success")
            return redirect(url_for("players.dashboard"))
        else:
            flash(message, "danger")

    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """User logout view."""
    logout_user()
    flash("You have been signed out. Until next time!", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Password recovery request view."""
    if current_user.is_authenticated:
        return redirect(url_for("players.dashboard"))

    form = ForgotPasswordForm()
    recovery_link = None

    if form.validate_on_submit():
        success, message, token = AuthService.request_password_reset(form.email.data)
        if token:
            recovery_link = url_for("auth.reset_password", token=token, _external=True)
            flash(
                "Password recovery token generated for local development. Use the link below.",
                "success",
            )
        else:
            flash(message, "info")

    return render_template(
        "auth/forgot_password.html",
        form=form,
        recovery_link=recovery_link,
    )


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Password reset with token."""
    if current_user.is_authenticated:
        return redirect(url_for("players.dashboard"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        success, message = AuthService.reset_password(token, form.password.data)
        if success:
            flash(message, "success")
            return redirect(url_for("auth.login"))
        else:
            flash(message, "danger")

    return render_template("auth/reset_password.html", form=form, token=token)
