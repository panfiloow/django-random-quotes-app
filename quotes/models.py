from django.db import models
from django.core.exceptions import ValidationError

class Source(models.Model):
    name = models.CharField(max_length=200, unique=True)
    type_choices = [
        ('MOV', 'Фильм'),
        ('BOOK', 'Книга'),
        ('SONG', 'Песня'),
        ('OTHER', 'Другое'),
    ]
    type = models.CharField(max_length=5, choices=type_choices)

    def __str__(self):
        return f"{self.get_type_display()}: {self.name}"

class Quote(models.Model):
    text = models.TextField(unique=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    weight = models.IntegerField(default=1)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.source_id:
            raise ValidationError('Источник обязателен для цитаты')
        
        if Quote.objects.filter(source=self.source).exclude(id=self.id).count() >= 3:
            raise ValidationError('У одного источника не может быть больше 3 цитат')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'"{self.text[:50]}..." from {self.source}'