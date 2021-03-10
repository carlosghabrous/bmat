from django import forms

class SelectDsrsFileForm(forms.Form):
    '''FROM CARLOS: This class represents a form to upload the DSR files'''
    dsr_files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))