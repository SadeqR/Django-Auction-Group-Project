from django import forms
from django.contrib.auth.models import  User
from django.contrib.auth.forms import UserCreationForm
from .models import Auction, Bid
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
import datetime


class AddBidForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
       super(AddBidForm, self).__init__(*args, **kwargs)
       self.fields['price'].widget.attrs['readonly'] = True

    class Meta:
        model = Bid
        fields = ['price', 'auction', 'user']
        exclude = ('auction', 'user')
        widgets = {
            'auction': forms.HiddenInput(),
            'user': forms.HiddenInput()
        }
        
class AddAuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['title', 'condition', 'description', 'image', 'price', 'date_expired']
        labels = {
            "price": "Starting Price"
        }

class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)