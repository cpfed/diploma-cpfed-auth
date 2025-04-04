# telegram_bot/views.py
import hashlib
import hmac
import json

from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpRequest
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings

from authentication.models import TelegramUser, MainUser
from django.contrib.auth import get_user_model
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from asgiref.sync import sync_to_async
from .services import send_telegram_message, send_telegram_photo, broadcast_telegram_message, start, start_menu, edit_telegram_message
from .forms import BroadcastForm
from contest.models import Contest
from .utils import LANG_DICT

from datetime import datetime


async def get_telegram_user(chat_id):
    get_user = sync_to_async(lambda: TelegramUser.objects.get_or_create(chat_id=chat_id)[0])
    return await get_user()


def get_telegram(user):
    return user.telegram if hasattr(user, 'telegram') else None


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
            if text == '/start':
                pass
                # await start(chat_id)
            elif text.startswith('/register') and len(parts) == 3:
                # Format: is /register username token
                username = parts[1]
                token = parts[2]
                user = await sync_to_async(MainUser.objects.get)(handle=username)
                if token != user.telegram_token:
                    await send_telegram_message(chat_id, 'Incorrect token')
                else:
                    telegram = await sync_to_async(get_telegram)(user)
                    if not telegram:
                        telegram_user = await get_telegram_user(chat_id)
                        user.telegram = telegram_user
                        await sync_to_async(user.save)()

                    await send_telegram_message(chat_id, LANG_DICT[user.telegram.language]['HELLO'] + user.first_name + LANG_DICT[user.telegram.language]['TELEGRAM_INTEGRATION_SUCCESS'])
            elif text.startswith('💻 Предстоящие контесты') or text.startswith('💻 Келесі сайыстар'):
                get_names = sync_to_async(lambda: list(Contest.objects.filter(
                    show_on_main_page=True,
                    registration_open=True
                ).values_list('id', 'name')))

                # Execute the async operation
                contest_names = await get_names()
                keyboard = []
                for i, name in contest_names:
                    keyboard.append([InlineKeyboardButton(name, callback_data=f"contest_{i}")])

                telegram_user = await get_telegram_user(chat_id)
                reply_markup = InlineKeyboardMarkup(keyboard)
                await send_telegram_message(chat_id, LANG_DICT[telegram_user.language]['CONTESTS_LIST'] + ':', reply_markup=reply_markup)
            elif text.startswith('👥 Присоединяйтесь к сообществу') or text.startswith('👥 Қауымдастыққа қосылыңыз'):
                url = 't.me/'
                telegram_user = await get_telegram_user(chat_id)
                await send_telegram_message(chat_id, LANG_DICT[telegram_user.language]['COMMUNITY_CHATS'] + f': {url}\n')
        elif 'callback_query' in data:
            choice = data['callback_query']['data']
            chat_id = data['callback_query']['message']['chat']['id']
            message_id = data['callback_query']['message']['message_id']
            if choice.startswith('contest'):
                contest_id = int(choice.split('_')[1])
                get_contest = sync_to_async(lambda: Contest.objects.get(pk=contest_id))
                contest = await get_contest()
                contest_date = contest.date.strftime("%d/%m/%Y %H:%M")

                telegram_user = await get_telegram_user(chat_id)
                caption = (f'{contest.name}\n'
                           f'{contest.playing_desc}\n'
                           f'{LANG_DICT[telegram_user.language]['TIME']}: {contest_date}\n\n')
                if contest.link:
                    caption += f'{LANG_DICT[telegram_user.language]['LINK']}: {contest.link}\n'
                await send_telegram_photo(chat_id, photo=contest.image_url, caption=caption)
            elif choice in ['KAZ', 'RUS']:
                language = ['KAZ', 'RUS'].index(choice)
                await start_menu(chat_id, language)
                # await send_telegram_message(chat_id, TelegramUser.LANGUAGE[language][1])

                telegram_user = await get_telegram_user(chat_id)
                telegram_user.language = language
                await sync_to_async(telegram_user.save)()
    except Exception as e:
        print(e)
        #return HttpResponse({"status": "error", "message": str(e)}, status=500)
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

    telegram_user = await get_telegram_user(telegram_id)
    if not telegram_user.user:
        telegram_user.user = user
        await sync_to_async(telegram_user.save)()

    await send_telegram_message(telegram_id, f'Hello {user.first_name}, you successfully singed in your telegram account.')
    await start(telegram_id)

    return redirect('profile')


async def telegram_broadcast(request):
    async_user = sync_to_async(lambda: request.user)()
    user = await async_user
    is_authenticated = await sync_to_async(lambda u: u.is_authenticated)(user)
    if not is_authenticated or not (user.is_staff or user.is_superuser):
        return HttpResponse(status=403)

    get_telegram_users = sync_to_async(lambda: MainUser.objects.filter(telegram_id__isnull=False).count())
    telegram_users_count = await get_telegram_users()

    if request.method == 'POST':
        form = BroadcastForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data.get('message', None)
            if message is None:
                return HttpResponse(status=400)
            await broadcast_telegram_message(telegram_users_count, message)
            return HttpResponse(status=200, content={f'Success: {telegram_users_count} users broadcasted successfully'})
        else:
            return HttpResponse(status=400)
    else:
        form = BroadcastForm()

    return render(request, 'telegram_bot/broadcast.html', {
        'form': form,
        'user_count': telegram_users_count
    })
