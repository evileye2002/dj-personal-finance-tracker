from django import forms
from django.forms import widgets
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Record, Wallet, Category, CategoryGroup
from django.db import models


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        min_length=6,
        max_length=150,
        required=True,
        widget=widgets.TextInput(
            attrs={"id": "username", "placeholder": "Tên đăng nhập"}
        ),
    )

    email = forms.EmailField(
        max_length=100,
        required=True,
        widget=widgets.EmailInput(attrs={"id": "email", "placeholder": "Email"}),
    )

    password1 = forms.CharField(
        min_length=8,
        required=True,
        widget=widgets.PasswordInput(
            attrs={"id": "password1", "placeholder": "Mật khẩu"}
        ),
    )

    password2 = forms.CharField(
        min_length=8,
        required=True,
        widget=widgets.PasswordInput(
            attrs={"id": "password2", "placeholder": "Nhập lại mật khẩu"}
        ),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

        username = self.__getitem__("username")
        email = self.__getitem__("email")
        # password1 = self.__getitem__('password1')
        password2 = self.__getitem__("password2")

        errors = ""
        if username.errors:
            errors += "username;"
        if email.errors:
            errors += "email;"
        if password2.errors:
            errors += "password1;password2;"

        for visible in self.visible_fields():
            if visible.field.widget.attrs["id"] in errors:
                visible.field.widget.attrs["class"] = "form-control is-invalid"
            else:
                visible.field.widget.attrs["class"] = "form-control"


class SignInForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=widgets.TextInput(
            attrs={
                "id": "username",
                "class": "form-control",
                "placeholder": "Tên đăng nhập",
            }
        ),
    )

    password = forms.CharField(
        required=True,
        widget=widgets.PasswordInput(
            attrs={
                "id": "password",
                "class": "form-control",
                "placeholder": "Mật khẩu",
            }
        ),
    )

    remember = forms.BooleanField(
        required=False,
        widget=widgets.CheckboxInput(
            attrs={"id": "remember", "class": "form-check-input"}
        ),
    )

    def __init__(self, *args, **kwargs):
        super(SignInForm, self).__init__(*args, **kwargs)

        if self.errors:
            for visible in self.visible_fields():
                if visible.field.widget.attrs["id"] != "remember":
                    visible.field.widget.attrs["class"] = "form-control is-invalid"


class RecordForm(forms.ModelForm):
    # datetime_format = "%d/%m/%Y - %H:%M:%S"
    # initial_datetime = timezone.now().strftime(datetime_format)
    timestamp = forms.DateTimeField(
        widget=forms.DateInput(attrs={"type": "datetime-local"}),
        label="Tại thời điểm",
        # initial=initial_datetime,
        # input_formats=[datetime_format],
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={"style": "height: 100px;"}),
        label="Mô tả",
        required=False,
    )

    class Meta:
        model = Record
        fields = ["name", "wallet", "category", "money", "timestamp", "description"]
        labels = {
            "wallet": "Ví của bạn",
            "money": "Số tiền",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        type = kwargs.pop("type", None)
        super(RecordForm, self).__init__(*args, **kwargs)

        if user:
            self.fields["wallet"].queryset = Wallet.objects.filter(author=user)

            if type == "income":
                self.fields["name"].label = "Tên khoản thu"
                self.fields["category"].label = "Hạng mục thu"
                self.fields["category"].queryset = Category.objects.filter(
                    models.Q(is_default=True) | models.Q(author=user),
                    category_group__name="Thu tiền",
                )

            if type == "spending":
                self.fields["name"].label = "Tên khoản chi"
                self.fields["category"].label = "Hạng mục chi"
                self.fields["category"].queryset = Category.objects.filter(
                    models.Q(is_default=True) | models.Q(author=user),
                    category_group__name="Chi tiền",
                )

            if type == "loan":
                self.fields["name"].label = "Tên khoản vay"
                self.fields["category"].label = "Hạng mục vay"
                self.fields["category"].queryset = Category.objects.filter(
                    models.Q(is_default=True) | models.Q(author=user),
                    category_group__name="Vay nợ",
                )


class WalletForm(forms.ModelForm):
    name = forms.CharField(label="Tên ví")
    is_calculate = forms.BooleanField(
        label="Tính vào báo cáo", required=False, initial=True
    )

    class Meta:
        model = Wallet
        fields = ["name", "is_calculate"]
