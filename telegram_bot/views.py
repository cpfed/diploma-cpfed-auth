# telegram_bot/views.py
import hashlib
import hmac
import json

from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpRequest
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings

from authentication.models import MainUser
from django.contrib.auth import get_user_model
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from .bot import application
from asgiref.sync import sync_to_async
from .services import send_telegram_message, send_telegram_photo
from contest.models import Contest


@csrf_exempt
@require_POST
async def telegram_webhook(request, token):
    print('received', token)
    if token != settings.TELEGRAM_BOT_TOKEN:
        return HttpResponse({"status": "error", "message": "Invalid token"}, status=403)
    try:
        data = json.loads(request.body)
        print('data =', data)
        if 'message' in data:
            chat_id = data['message']['chat']['id']

            text = data['message'].get('text', '')
            parts = text.split()

            if text.startswith('/register') and len(parts) == 3:
                # Format: is /register username token
                username = parts[1]
                token = parts[2]
                user = await sync_to_async(MainUser.objects.get)(handle=username)
                if token != user.telegram_token:
                    await send_telegram_message(chat_id, 'Incorrect token')
                else:
                    user.telegram_id = chat_id
                    await sync_to_async(user.save)()

                    await send_telegram_message(chat_id, f'Hello {user.first_name}, you successfully singed in your telegram account.')
            elif text.startswith('💻 Предстоящие контесты'):
                get_names = sync_to_async(lambda: list(Contest.objects.filter(
                    show_on_main_page=True,
                    registration_open=True
                ).values_list('id', 'name')))

                # Execute the async operation
                contest_names = await get_names()
                keyboard = []
                for i, name in contest_names:
                    keyboard.append([InlineKeyboardButton(name, callback_data=f"contest_{i}")])

                reply_markup = InlineKeyboardMarkup(keyboard)
                await send_telegram_message(chat_id, 'List of contests:', reply_markup=reply_markup)
        elif 'callback_query' in data:
            choice = data['callback_query']['data']
            chat_id = data['callback_query']['message']['chat']['id']
            if choice.startswith('contest'):
                contest_id = int(choice.split('_')[1])
                print('choice_id =', contest_id)
                get_contest = sync_to_async(lambda: Contest.objects.get(pk=contest_id))
                contest = await get_contest()
                await send_telegram_photo(chat_id, photo=contest.image_url, caption=f'{contest.name}\n{contest.playing_desc}\n\nLink: {contest.link}\n')
    except Exception as e:
        print(e)
        #return HttpResponse({"status": "error", "message": str(e)}, status=500)
    print('token is same')
    return HttpResponse(status=200)


@require_GET
@csrf_exempt
async def telegram_login(request):
    params = request.GET
    async_user = sync_to_async(lambda: request.user)()
    user = await async_user
    is_authenticated = await sync_to_async(lambda u: u.is_authenticated)(user)
    if not is_authenticated:
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

    telegram_id = params.get('id')
    user.telegram_id = telegram_id
    await sync_to_async(user.save)()
    await send_telegram_message(telegram_id, f'Hello {user.first_name}, you successfully singed in your telegram account.')

    return HttpResponse(status=200)
