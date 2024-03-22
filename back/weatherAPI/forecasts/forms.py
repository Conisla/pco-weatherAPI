from django import forms

class TrainModelForm(forms.Form):
    csv_file = forms.FileField()
    features = forms.CharField()
    target = forms.CharField()
    model_type = forms.CharField()
    model_name = forms.CharField()
    train_test_size = forms.FloatField()
    batch_size = forms.IntegerField()
    epochs = forms.IntegerField()