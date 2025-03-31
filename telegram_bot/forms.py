from django import forms


class BroadcastForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, label="Message to broadcast")
