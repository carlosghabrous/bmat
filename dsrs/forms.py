from django import forms

class SelectDsrsFileForm(forms.Form):
    '''This class represents a form to upload the DSR files'''
    dsr_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))