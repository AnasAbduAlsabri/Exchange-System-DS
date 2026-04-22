# app/routes.py
import os
from flask import jsonify, render_template, redirect, url_for, flash, request, session
import zeep
from . import db, app, socketio, openai_client
from .socket_routes import user_sids
from .forms import (
    RegistrationForm,
    LoginForm,
    TransferForm,
    ConfirmTransferForm,
    DepositForm,
    ConvertCurrencyForm,
)
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Transfer, Transactions


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/google_map", methods=["GET"])
def google_map():
    return render_template("google_map.html", google_api_key=os.getenv("GOOGLE_API_KEY"))


@app.route("/balance")
def balance():
    return render_template("balance.html")


@app.route("/register", methods=["GET"])
def goToregister():
    form = RegistrationForm()
    return render_template("register.html", form=form)


@app.route("/register", methods=["POST"])
def register():
    form = RegistrationForm()

    if current_user.is_authenticated:
        # Redirect to the home page or handle the case where a logged-in user tries to register
        return redirect(url_for("index"))

    if form.validate_on_submit():
        user_found = User.query.filter_by(username=form.username.data).first()
        if not user_found:
            new_user = User(
                username=form.username.data,
                email=form.email.data,
            )
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()

            flash("Account created successfully!", "success")
            return redirect(url_for("login"))
        flash("Username alredy exist!", "error")
        return render_template("register.html", form=form)
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET"])
def goTologin():
    form = LoginForm()
    return render_template("login.html", form=form)


@app.route("/login", methods=["POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("index"))

    flash("Invalid username or password. Please try again.", "danger")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required  # يجعل هذا الطريقة محمية ويتطلب تسجيل الدخول
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for("index"))


@app.route("/deposit", methods=["GET"])
@login_required
def goTodeposit():
    form = DepositForm()
    return render_template("deposit.html", form=form)


@app.route("/deposit", methods=["POST"])
@login_required
def deposit():
    form = DepositForm()
    if form.validate_on_submit():
        # تحويل قيمة amount إلى float قبل إجراء العمليات الرياضية
        amount = form.amount.data
        current_user.balance += float(amount)
        db.session.commit()
        flash(f"Deposit of ${amount} successful!", "success")
        return redirect(url_for("balance"))

    return render_template("deposit.html", form=form)


@app.route("/transfer", methods=["GET"])
def goToTransfer():
    form = TransferForm()
    return render_template("transfer.html", form=form)


@app.route("/transfer", methods=["POST"])
@login_required
def transfer():
    form = TransferForm()
    if form.validate_on_submit():
        # التحقق من توفر الرصيد

        if current_user.balance < form.amount.data:
            flash("Insufficient funds! Please check your balance.", "danger")

            return redirect(url_for("transfer"))

        # التحقق من صحة حساب الوجهة
        destination_user = User.query.filter_by(username=form.receiver.data).first()
        if not destination_user:
            flash(
                "Destination account not found! Please double-check the username.",
                "danger",
            )
            return redirect(url_for("transfer"))
        # حفظ البيانات في الجلسة
        session["transfer_data"] = {
            "sender": current_user.username,
            "receiver": destination_user.username,
            "recipient_sid": user_sids.get(destination_user.username),
            "amount": float(form.amount.data),
        }

        print("//////////////////////////////////Recipient SID:", session.get("recipient_sid"))
        return redirect(url_for("confirm_transfer"))
    return render_template("transfer.html", form=form)


@app.route("/confirm_transfer", methods=["GET"])
def goToconfirm_transfer():
    transfer_data = session.get("transfer_data")
    if not transfer_data:
        flash("No transfer data available", "danger")
        return redirect(url_for("transfer"))
    form = ConfirmTransferForm(data=transfer_data)
    return render_template("confirm_transfer.html", transfer=transfer_data, form=form)


@app.route("/confirm_transfer", methods=["POST"])
def confirm_transfer():
    print("---------------------", request.method)
    # استرجاع البيانات من الجلسة أو flash
    transfer_data = session.get("transfer_data")
    destination_user = User.query.filter_by(username=transfer_data["receiver"]).first()
    # إجراء عملية التحويل
    amount = transfer_data["amount"]
    current_user.balance -= amount
    destination_user.balance += amount
    transfer = Transfer(
        sender=transfer_data["sender"],
        receiver=transfer_data["receiver"],
        amount=transfer_data["amount"],
    )
    db.session.add(transfer)
    db.session.commit()
    # إرسال إشعار إلى العميل الذي تم تحويل الأموال إليه
    recipient_sid = transfer_data.get("recipient_sid")
    if recipient_sid:
        socketio.emit(
            "transfer_notification",
            {"message": f"You received ${amount} from {transfer_data['sender']}!"},
            room=recipient_sid
        )
    else:
        # Fallback or general notification
        socketio.emit(
            "transfer_notification",
            {"message": "A transfer was completed."},
        )

    # إزالة بيانات التحويل من الجلسة بمجرد تحميلها
    session.pop("transfer_data", None)
    flash("Transfer confirmed!", "success")
    return render_template("index.html")



@app.route("/complete_transfer", methods=["POST"])
def complete_transfer():
    form = ConfirmTransferForm(request.form)
    if form.validate():
        # استخدام بيانات النموذج
        new_transaction = Transactions(
            sender=form.sender.data,
            receiver=form.receiver.data,
            amount=form.amount.data,
            currency=form.currency.data,
        )
        db.session.add(new_transaction)
        db.session.commit()
        flash("Transfer completed successfully!", "success")
        return redirect(url_for("index"))

    return redirect(url_for("confirm_transfer"))


@app.route("/transactions")
@login_required
def transactions():
    # from mpi4py import app
    # app.app_command_line("mpiexec -n 3 py ../getTransfers_mpi.py")
    transfers = Transfer.query.filter_by(sender=current_user.username).all()
    return render_template("transactions.html", transfers=transfers)


@app.route("/convert_currency", methods=["GET", "POST"])
def convert_currency():
    form = ConvertCurrencyForm()

    if form.validate_on_submit():
        # طباعة جميع البيانات المستقبلة من الفورم

        original_amount = form.original_amount.data
        currency_from = form.currency_from.data
        currency_to = form.currency_to.data
        date = "2022/1/1"
        user = ""
        password = ""

        try:
            # تحديد عنوان WSDL
            wsdl_path = os.path.join(os.path.dirname(__file__), "..", "FxtopServices.wsdl")

            # إنشاء عميل Zeep
            client = zeep.Client(wsdl=wsdl_path)
            # إرسال طلب تحويل العملات
            result = client.service.Convert(
                OriginalAmount=original_amount,
                C1=currency_from,
                C2=currency_to,
                Date=date,
                User=user,
                Password=password,
            )

            flash(
                f"{result['OriginalAmount']} {result['C1']} = {float(result['ResultAmount']):.2f} {result['C2']}  ",
                "success",
            )

        except zeep.exceptions.Fault as e:
            flash(f"Conversion Error: {e.message}", "danger")

    return render_template("convert_currency.html", form=form)


@app.route("/get_chat", methods=["GET"])
def get_chat():
    return render_template("openAi.html")


@app.route("/get_chat_response", methods=["POST"])
def get_chat_response():
    user_message = request.form["user_message"]

    try:
        # Send user message to OpenAI for chat completion
        stream = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
            stream=True,
        )

        response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response += chunk.choices[0].delta.content

        return jsonify({"response": response})
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return jsonify({"response": f"Error: {str(e)}"}), 500


@app.route("/show_banks", methods=["GET"])
def goToShow_banks():
    return render_template("banks.html")


@app.route("/show_banks", methods=["POST"])
def show_banks():
    import requests

    bank_no = request.form.get('BanksNo')

    url = "http://localhost:8000/get_banks"
    data = [
        {
            "BanksNo":int(bank_no),
            "id": "3aab299b047b4e0ebcacc6fc2606af63",
            "title": "Get Banks Names",
        }
    ]

    response = requests.request("POST", url=url, json=data)
    Bank= response.json()
    return render_template("banks.html", Bank=Bank)
