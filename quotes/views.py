import random
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum
from .models import Quote, Source
from .forms import QuoteForm
from django.core.exceptions import ValidationError
import json
from django.views.decorators.csrf import csrf_exempt

def get_random_quote(exclude_id=None):
    """Вспомогательная функция для получения случайной цитаты"""
    if not Quote.objects.exists():
        return None

    quotes_query = Quote.objects.all()
    if exclude_id:
        quotes_query = quotes_query.exclude(id=exclude_id)

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

        # Убедимся, что у пользователя есть сессия
        if not request.session.session_key:
            request.session.create()

        # Инициализируем user_votes если их нет
        if 'user_votes' not in request.session:
            request.session['user_votes'] = {}

        # Получаем текущий голос пользователя для этой цитаты
        user_votes = request.session.get('user_votes', {})
        current_vote = user_votes.get(str(quote.id))

        return render(request, 'quotes/random_quote.html', {
            'quote': quote,
            'user_has_liked': current_vote == 'like',
            'user_has_disliked': current_vote == 'dislike'
        })
    else:
        return render(request, 'quotes/random_quote.html', {'quote': None})

@csrf_exempt
def like_quote(request, quote_id):
    if request.method == 'POST':
        quote = get_object_or_404(Quote, id=quote_id)

        # Убедимся, что у пользователя есть сессия
        if not request.session.session_key:
            request.session.create()

        # Инициализируем user_votes если их нет
        if 'user_votes' not in request.session:
            request.session['user_votes'] = {}

        user_votes = request.session['user_votes']

        # Получаем текущий голос для этой цитаты
        current_vote = user_votes.get(str(quote_id))

        if current_vote == 'like':
            # Убираем лайк
            quote.likes -= 1
            del user_votes[str(quote_id)]
            message = 'Лайк убран'
        elif current_vote == 'dislike':
            # Меняем дизлайк на лайк
            quote.dislikes -= 1
            quote.likes += 1
            user_votes[str(quote_id)] = 'like'
            message = 'Дизлайк изменен на лайк'
        else:
            # Новый лайк
            quote.likes += 1
            user_votes[str(quote_id)] = 'like'
            message = 'Лайк добавлен'

        # Сохраняем изменения
        quote.save()
        request.session['user_votes'] = user_votes
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'message': message,
            'likes': quote.likes,
            'dislikes': quote.dislikes,
            'user_has_liked': user_votes.get(str(quote_id)) == 'like',
            'user_has_disliked': user_votes.get(str(quote_id)) == 'dislike'
        })

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def dislike_quote(request, quote_id):
    if request.method == 'POST':
        quote = get_object_or_404(Quote, id=quote_id)

        # Убедимся, что у пользователя есть сессия
        if not request.session.session_key:
            request.session.create()

        # Инициализируем user_votes если их нет
        if 'user_votes' not in request.session:
            request.session['user_votes'] = {}

        user_votes = request.session['user_votes']

        # Получаем текущий голос для этой цитаты
        current_vote = user_votes.get(str(quote_id))

        if current_vote == 'dislike':
            # Убираем дизлайк
            quote.dislikes -= 1
            del user_votes[str(quote_id)]
            message = 'Дизлайк убран'
        elif current_vote == 'like':
            # Меняем лайк на дизлайк
            quote.likes -= 1
            quote.dislikes += 1
            user_votes[str(quote_id)] = 'dislike'
            message = 'Лайк изменен на дизлайк'
        else:
            # Новый дизлайк
            quote.dislikes += 1
            user_votes[str(quote_id)] = 'dislike'
            message = 'Дизлайк добавлен'

        # Сохраняем изменения
        quote.save()
        request.session['user_votes'] = user_votes
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'message': message,
            'likes': quote.likes,
            'dislikes': quote.dislikes,
            'user_has_liked': user_votes.get(str(quote_id)) == 'like',
            'user_has_disliked': user_votes.get(str(quote_id)) == 'dislike'
        })

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def add_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('random_quote')
            except ValidationError as e:
                for error in e:
                    form.add_error(None, error)
            except Exception as e:
                form.add_error(None, f"Ошибка сохранения: {e}")
    else:
        form = QuoteForm()

    return render(request, 'quotes/add_quote.html', {'form': form})

def popular_quotes(request):
    quotes = Quote.objects.order_by('-likes')[:10]
    return render(request, 'quotes/popular_quotes.html', {'quotes': quotes})
