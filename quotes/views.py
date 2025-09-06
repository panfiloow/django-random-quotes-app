# quotes/views.py
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum
from .models import Quote, Source
from .forms import QuoteForm

def get_random_quote(exclude_id=None):
    """Вспомогательная функция для получения случайной цитаты"""
    if not Quote.objects.exists():
        return None
    
    # Фильтруем цитаты, исключая текущую
    quotes_query = Quote.objects.all()
    if exclude_id:
        quotes_query = quotes_query.exclude(id=exclude_id)
    
    # Если после исключения не осталось цитат, возвращаем None
    if not quotes_query.exists():
        return None
    
    total_weight = quotes_query.aggregate(total=Sum('weight'))['total'] or 0
    
    if total_weight == 0:
        quotes = list(quotes_query)
        return random.choice(quotes) if quotes else None
    
    random_index = random.randint(0, total_weight - 1)
    
    current = 0
    for quote in quotes_query:
        current += quote.weight
        if current > random_index:
            return quote
    
    return None

def random_quote(request):
    # Получаем случайную цитату
    quote = get_random_quote()
    
    if quote:
        # Увеличиваем счетчик просмотров
        quote.views += 1
        quote.save()
        
        # Сохраняем ID текущей цитаты в сессии
        request.session['current_quote_id'] = quote.id
        request.session.modified = True
        
        # Проверяем, лайкал ли пользователь эту цитату через сессию
        liked_quotes = request.session.get('liked_quotes', [])
        disliked_quotes = request.session.get('disliked_quotes', [])
        
        user_has_liked = quote.id in liked_quotes
        user_has_disliked = quote.id in disliked_quotes
        
        return render(request, 'quotes/random_quote.html', {
            'quote': quote,
            'user_has_liked': user_has_liked,
            'user_has_disliked': user_has_disliked
        })
    else:
        return render(request, 'quotes/random_quote.html', {'quote': None})

def next_quote(request):
    """Представление для следующей цитаты (для AJAX)"""
    # Получаем ID текущей цитаты из сессии
    current_quote_id = request.session.get('current_quote_id')
    
    # Получаем новую цитату, исключая текущую
    quote = get_random_quote(exclude_id=current_quote_id)
    
    # Если после исключения текущей цитаты не осталось других,
    # показываем любую случайную цитату
    if not quote:
        quote = get_random_quote()
    
    if quote:
        # Увеличиваем счетчик просмотров
        quote.views += 1
        quote.save()
        
        # Обновляем ID текущей цитаты в сессии
        request.session['current_quote_id'] = quote.id
        request.session.modified = True
        
        # Проверяем, лайкал ли пользователь эту цитату через сессию
        liked_quotes = request.session.get('liked_quotes', [])
        disliked_quotes = request.session.get('disliked_quotes', [])
        
        user_has_liked = quote.id in liked_quotes
        user_has_disliked = quote.id in disliked_quotes
        
        # Возвращаем данные в JSON формате
        return JsonResponse({
            'success': True,
            'quote_id': quote.id,
            'quote_text': quote.text,
            'quote_source': str(quote.source),
            'views': quote.views,
            'likes': quote.likes,
            'dislikes': quote.dislikes,
            'user_has_liked': user_has_liked,
            'user_has_disliked': user_has_disliked
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Цитаты не найдены'
        })

def like_quote(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    
    # Получаем списки лайкнутых и дизлайкнутых цитат из сессии
    liked_quotes = request.session.get('liked_quotes', [])
    disliked_quotes = request.session.get('disliked_quotes', [])
    
    # Проверяем, не лайкал ли уже пользователь
    if quote_id in liked_quotes:
        return JsonResponse({
            'success': False,
            'message': 'Вы уже лайкали эту цитату',
            'likes': quote.likes,
            'dislikes': quote.dislikes
        })
    
    # Убираем дизлайк, если был
    if quote_id in disliked_quotes:
        disliked_quotes.remove(quote_id)
        quote.dislikes -= 1
        request.session['disliked_quotes'] = disliked_quotes
    
    # Добавляем лайк
    liked_quotes.append(quote_id)
    quote.likes += 1
    quote.save()
    
    # Сохраняем в сессии
    request.session['liked_quotes'] = liked_quotes
    request.session.modified = True
    
    return JsonResponse({
        'success': True,
        'likes': quote.likes,
        'dislikes': quote.dislikes
    })

def dislike_quote(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    
    # Получаем списки лайкнутых и дизлайкнутых цитат из сессии
    liked_quotes = request.session.get('liked_quotes', [])
    disliked_quotes = request.session.get('disliked_quotes', [])
    
    # Проверяем, не дизлайкал ли уже пользователь
    if quote_id in disliked_quotes:
        return JsonResponse({
            'success': False,
            'message': 'Вы уже дизлайкали эту цитату',
            'likes': quote.likes,
            'dislikes': quote.dislikes
        })
    
    # Убираем лайк, если был
    if quote_id in liked_quotes:
        liked_quotes.remove(quote_id)
        quote.likes -= 1
        request.session['liked_quotes'] = liked_quotes
    
    # Добавляем дизлайк
    disliked_quotes.append(quote_id)
    quote.dislikes += 1
    quote.save()
    
    # Сохраняем в сессии
    request.session['disliked_quotes'] = disliked_quotes
    request.session.modified = True
    
    return JsonResponse({
        'success': True,
        'likes': quote.likes,
        'dislikes': quote.dislikes
    })

def add_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('random_quote')
            except ValidationError as e:
                # Добавляем ошибку валидации в форму
                for error in e:
                    form.add_error(None, error)
        # Если форма не валидна, ошибки уже будут в form.errors
    else:
        form = QuoteForm()
    
    return render(request, 'quotes/add_quote.html', {'form': form})

def popular_quotes(request):
    quotes = Quote.objects.order_by('-likes')[:10]
    return render(request, 'quotes/popular_quotes.html', {'quotes': quotes})