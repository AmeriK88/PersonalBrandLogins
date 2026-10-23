from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        strip=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Your Name"}
        ),
    )
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Your Email"}
        ),
    )
    subject = forms.CharField(
        max_length=200,
        strip=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Subject"}
        ),
    )
    message = forms.CharField(
        max_length=5000,
        strip=True,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Your Message",
                "rows": 5,
            }
        ),
    )
    recaptcha_token = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={"id": "recaptcha-token"}),
    )
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={"autocomplete": "off", "tabindex": "-1"}),
    )
