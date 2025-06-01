# telegram_bot/views.py
import hashlib
import hmac
import json

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpRequest
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings

from .models import TelegramUser, TelegramQA
from .services import send_telegram_message, send_telegram_photo, broadcast_telegram_message, start, start_menu, \
    edit_telegram_message
from .forms import BroadcastForm
from contest.models import Contest


user_categories = ['school', 'university', 'teacher', 'company']


def get_telegram_user(chat_id):
    return TelegramUser.objects.get_or_create(chat_id=chat_id)[0]


def get_telegram(user):
    return user.telegram if hasattr(user, 'telegram') else None


@csrf_exempt
@require_POST
def telegram_webhook(request, token):
    if token != settings.TELEGRAM_BOT_TOKEN:
        return HttpResponse({"status": "error", "message": "Invalid token"}, status=403)
    try:
        from telegram_bot.message_cache import message_cache

        data = json.loads(request.body)
        if 'message' in data:
            chat_id = data['message']['chat']['id']
            telegram_user = get_telegram_user(chat_id)

            text = data['message'].get('text', '')
            parts = text.split()
            if text.startswith('/start'):
                # send_telegram_message(chat_id, 'Please integrate your telegram account in auth.cpfed.kz')
                start(chat_id)
            elif message_cache.matches(text, 'CONTESTS'):
                contest_names = Contest.objects.filter(
                    show_on_main_page=True,
                    registration_open=True
                ).values_list('id', 'name')
                keyboard = []
                for i, name in contest_names.iterator():
                    keyboard.append([
                        {
                            'text': name,
                            'callback_data': f"contest_{i}"
                        }
                    ])

                reply_markup = {
                    "inline_keyboard": keyboard
                }

                response = message_cache.get_message(telegram_user.language, 'CONTESTS_LIST')
                send_telegram_message(chat_id, response, reply_markup=reply_markup)
            elif message_cache.matches(text, 'COMMUNITY'):
                response = message_cache.get_message(telegram_user.language, 'COMMUNITY_CHATS')
                send_telegram_message(chat_id, response)
            elif message_cache.matches(text, 'QA'):
                qa = TelegramQA.objects.create(telegram_user=telegram_user, request_write_mode=True)
                response = message_cache.get_message(telegram_user.language, 'QA_REQUEST')
                send_telegram_message(chat_id, response)
            else:
                try:
                    qa = TelegramQA.objects.get(telegram_user=telegram_user, request_write_mode=True)
                    qa.text = text
                    qa.request_write_mode = False
                    qa.save()

                    response = (f"{message_cache.get_message(telegram_user.language, 'QA_NUMBER')} #{qa.id}:\n",
                                f"{message_cache.get_message(telegram_user.language, 'QA_WAIT')}")
                    send_telegram_message(chat_id, response)
                except TelegramQA.DoesNotExist:
                    pass
        elif 'callback_query' in data:
            choice = data['callback_query']['data']
            chat_id = data['callback_query']['message']['chat']['id']
            message_id = data['callback_query']['message']['message_id']
            telegram_user = get_telegram_user(chat_id)

            if choice.startswith('contest'):
                contest_id = int(choice.split('_')[1])
                contest = Contest.objects.get(pk=contest_id)
                contest_date = contest.date.strftime("%d/%m/%Y %H:%M")
                caption = (f'{contest.name}\n'
                           f'{contest.playing_desc}\n'
                           f'{message_cache.get_message(telegram_user.language, "TIME")}: {contest_date}\n\n')
                if contest.link:
                    caption += f'{message_cache.get_message(telegram_user.language, "LINK")}: {contest.link}\n'
                send_telegram_photo(chat_id, photo=contest.image_url, caption=caption)
            elif choice in ['kk', 'ru']:
                edit_telegram_message(chat_id, message_id, '')
                send_telegram_message(chat_id, message_cache.get_message(choice, 'LANG_CHOICE'))

                keyboard = []
                for category in user_categories:
                    keyboard.append([
                        {
                            'text': message_cache.get_message(choice, category),
                            'callback_data': category
                        }
                    ])
                reply_markup = {
                    "inline_keyboard": keyboard
                }

                response = message_cache.get_message(choice, 'CHOOSE_CATEGORY')
                send_telegram_message(chat_id, response, reply_markup=reply_markup)

                telegram_user.language = choice
                telegram_user.save()
            elif choice in user_categories:
                start_menu(chat_id, telegram_user.language)

                telegram_user.user_group = user_categories.index(choice)
                telegram_user.save()
    except Exception as e:
        return HttpResponse({"message": str(e)}, status=400)
    return HttpResponse(status=200)


@require_GET
@csrf_exempt
def telegram_login(request):
    params = request.GET
    user = request.user
    if not user.is_authenticated:
        return HttpResponse(status=403)

    bot_token = settings.TELEGRAM_BOT_TOKEN

    data_check_string = ['{}={}'.format(k, v)
                         for k, v in params.items() if k != 'hash']

    data_check_string = '\n'.join(sorted(data_check_string))

    built_hash = hmac.new(hashlib.sha256(bot_token.encode()).digest(),
                          msg=data_check_string.encode(),
                          digestmod=hashlib.sha256).hexdigest()

    if built_hash != params.get('hash'):
        raise ValidationError("Invalid hash")

    chat_id = params.get('id')

    telegram_user = TelegramUser.objects.get_or_create(chat_id=chat_id)[0]
    telegram_user.user = user
    telegram_user.save()

    send_telegram_message(chat_id, f'Hello {user.first_name}, you successfully singed in your telegram account.')
    start(chat_id)

    return redirect('profile')


def telegram_broadcast(request):
    user = request.user
    if not user.is_authenticated or not (user.is_staff or user.is_superuser):
        return HttpResponse(status=403)

    telegram_users_count = TelegramUser.objects.filter(user__isnull=False).count()

    if request.method == 'POST':
        form = BroadcastForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data.get('message', None)
            if message is None:
                return HttpResponse(status=400)
            broadcast_telegram_message(telegram_users_count, message)
            return HttpResponse(status=200, content={f'Success: {telegram_users_count} users broadcasted successfully'})
        else:
            return HttpResponse(status=400)
    else:
        form = BroadcastForm()

    return render(request, 'telegram_bot/broadcast.html', {
        'form': form,
        'user_count': telegram_users_count
    })


def telegram_requests(request):
    user = request.user
    if not user.is_authenticated or not (user.is_staff or user.is_superuser):
        return HttpResponse(status=403)

    if not request.method == 'GET':
        return HttpResponse(status=404)
    # Get all questions ordered by creation date (newest first)
    questions = TelegramQA.objects.select_related('telegram_user__user').order_by('-created_at')

    # Calculate stats
    stats = {
        'received': TelegramQA.objects.filter(status=0).count(),
        'in_process': TelegramQA.objects.filter(status=1).count(),
        'processed': TelegramQA.objects.filter(status=2).count(),
    }

    context = {
        'questions': questions,
        'stats': stats,
        'current_time': timezone.now(),
    }

    return render(request, 'telegram_bot/requests.html', context)


def telegram_respond(request, qa_id):
    from telegram_bot.message_cache import message_cache

    question = get_object_or_404(TelegramQA, id=qa_id)

    if request.method == 'POST':
        response_text = request.POST.get('response_text', '').strip()
        response_text = (f"{message_cache.get_message(question.telegram_user.language, 'QA_NUMBER_RESPONSE')} #{qa_id}:\n",
                         f"{response_text}")
        action = request.POST.get('action')

        if not response_text:
            return render(request, 'telegram_bot/respond.html', {'question': question})

        if action == 'send':
            # Send response to user via Telegram (you'll need to implement this)
            success = send_telegram_message(question.telegram_user.chat_id, response_text)

            if success:
                # Update question status to processed
                question.status = 2
                question.save()

                return redirect('telegram_requests')
            else:
                pass
                # messages.error(request, 'Failed to send response. Please try again.')

        elif action == 'save_draft':
            question.status = 1
            question.save()

            return redirect('telegram_requests')

    return render(request, 'telegram_bot/respond.html', {'question': question})