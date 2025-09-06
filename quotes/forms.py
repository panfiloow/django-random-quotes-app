from django import forms
from django.core.exceptions import ValidationError
from .models import Quote, Source

class QuoteForm(forms.Form):
    text = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Текст цитаты', 'rows': 4}),
        label='Текст цитаты'
    )
    source_name = forms.CharField(
        max_length=200, 
        label='Название источника'
    )
    source_type = forms.ChoiceField(
        choices=Source.type_choices, 
        label='Тип источника'
    )
    weight = forms.IntegerField(
        initial=1,
        min_value=1,
        label='Вес цитаты',
        widget=forms.NumberInput(attrs={'min': 1})
    )

    def clean(self):
        cleaned_data = super().clean()
        source_name = cleaned_data.get('source_name')
        source_type = cleaned_data.get('source_type')
        
        if source_name and source_type:
            # Проверяем, не превысит ли новая цитата лимит
            source, created = Source.objects.get_or_create(
                name=source_name,
                defaults={'type': source_type}
            )
            
            # Проверяем ограничение на количество цитат
            if Quote.objects.filter(source=source).count() >= 3:
                raise ValidationError('У одного источника не может быть больше 3 цитат.')
        
        return cleaned_data

    def save(self):
        text = self.cleaned_data['text']
        source_name = self.cleaned_data['source_name']
        source_type = self.cleaned_data['source_type']
        weight = self.cleaned_data['weight']
        
        # Создаем или получаем источник
        source, created = Source.objects.get_or_create(
            name=source_name,
            defaults={'type': source_type}
        )
        
        # Создаем цитату
        quote = Quote.objects.create(
            text=text,
            source=source,
            weight=weight
        )
        
        return quote