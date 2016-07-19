# -*- coding: utf-8 -*-
from django import forms


class CSVForm(forms.Form):
    csvfile = forms.FileField(
        label='Select a file',
        help_text='CSV format, max. XX megabytes'
    )
