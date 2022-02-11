import threading
import time

import pywebio.session
from pywebio.input import input, input_group, file_upload, PASSWORD, TEXT, TIME, FLOAT
from pywebio.output import (
    put_scrollable,
    put_scope,
    put_text,
    put_loading,
    put_buttons,
    put_image,
    put_markdown,
    popup,
    close_popup
)

from bot import Bot, UI_messages


def validate_username(p: str) -> str:
    if '@' in p:
        return 'Please enter without "@" character!'


def file_parser(content: bin, read_proxies: bool = False) -> dict or list:
    content = content.decode('ascii')
    content = content.split("\r\n")
    if not content[-1]:
        content = content[:-1]
    if read_proxies:
        proxies_lst = []
        for line in content:
            proxies_lst.append(line.strip())
        return proxies_lst
    else:
        accounts = {}
        for line in content:
            item = line.split(' ')
            username = item[0].strip()
            passwd = item[1].strip()
            accounts[username] = passwd
        return accounts


def ui_messages():
    while True:
        pywebio.session.get_current_session()
        if UI_messages:
            message = UI_messages.pop()
            put_markdown(message, scope='scrollable')
            if "All done" in message:
                break
        time.sleep(1)


def app(creepy_accounts: dict[str, list], **kwargs) -> None:
    target_account: str = kwargs['target_account']
    start_time: str = kwargs['start_time']
    end_time: str = kwargs['end_time']
    like_time: str = kwargs['like_time']
    api_delay: str = kwargs['api_delay']
    proxies: list = kwargs['proxies']

    with open('bot.png', 'rb') as photo:
        put_image(photo.read(), width='10%', height='10%', position=-1)
    with put_loading(shape='border', color='info'):
        put_text("Hello :) i'm running 🤭")
        put_scrollable(put_scope('scrollable'), height=420, keep_bottom=True)
        put_markdown(f"Time between each like set as `{like_time}` seconds", scope='scrollable')
        # Handles UI messages
        jobs = []  # For threads
        job_thread = threading.Thread(target=ui_messages)
        job_thread.start()
        jobs.append(job_thread)
        # Creating bot instance for each account
        for username, password in creepy_accounts.items():
            print(f'Username: "{username}" - Password: "{password}"')  # To show log to end-user

            bot = Bot(
                start_time=start_time,
                end_time=end_time,
                like_time=like_time,
                api_delay=api_delay,
            )
            put_markdown(
                f"I run `{username}` from **{bot.start_time}** to **{bot.end_time}** o'clock",
                scope='scrollable',
            )
            put_markdown(f"*`{username}` scheduled successfully*", scope='scrollable')
            # Run the creepies [with Smile ;)]
            time.sleep(7)
            job_thread = threading.Thread(
                target=bot.schedule_and_run,
                args=(username, password, target_account, proxies),
            )
            job_thread.start()
            jobs.append(job_thread)
        for job in jobs:
            job.join()
        put_text("bye bye 😴", scope='scrollable')


def main():
    info = input_group("Bot Settings", [
        input("Input your username: ", name="username", type=TEXT, placeholder="Username", validate=validate_username),
        input("Input your password: ", name="password", type=PASSWORD, placeholder="Password"),
        file_upload(
            "Or read the list of accounts from the file[txt] (optional): ",
            name="accounts",
            accept="file/txt",
            required=False,
        ),
        input("Input a proxy (optional): ", name="proxy", type=TEXT, placeholder="Proxy", required=False),
        file_upload(
            "Or select the file[txt] containing the proxies (optional): ",
            name="proxies",
            accept="file/txt",
            required=False,
        ),
        input(
            "Target account: ", name="target", type=TEXT,
            placeholder="Username",
            validate=validate_username,
            required=True,
        ),
    ])
    scheduling = input_group("Scheduling", [
        input("Start time", name="start_t", type=TIME, placeholder="start time"),
        input("End time", name="end_t", type=TIME, placeholder="end time"),
        input(
            "How many seconds to wait for each like?",
            name="like_t",
            type=FLOAT,
            placeholder="time between each like",
            required=True,
        ),
        input(
            "API call delay time (optional; at lest 5 seconds recommended)",
            name="api_delay",
            type=FLOAT,
            placeholder="delays between each API call",
            required=False,
        ),
    ])

    # Creepy accounts
    creepy_username = info['username']
    creepy_password = info['password']
    # Check file exists
    accounts_file = info['accounts']
    proxies_file = info['proxies']
    # Accounts
    accounts = {}
    if accounts_file:
        file_content = info['accounts']['content']
        accounts = file_parser(file_content)
    else:
        accounts[creepy_username] = creepy_password
    # Proxies
    if proxies_file:
        file_content = info['proxies']['content']
        proxies = file_parser(file_content, read_proxies=True)
    elif info['proxy']:
        proxies = [info['proxy']]
    else:
        proxies = []

    # Target account
    target_account = info['target']
    # Timing
    s_t = scheduling['start_t']
    e_t = scheduling['end_t']
    l_t = scheduling['like_t']
    api_delay = scheduling['api_delay']
    if not api_delay:
        api_delay = 7
    # Popup
    with popup('The scheduling was done as follows:') as pop:
        put_text(f"Start time: {s_t}\nEnd time: {e_t}")
        put_buttons([("Ok", pop)], onclick=lambda _: close_popup())
    # Running
    app(
        creepy_accounts=accounts,
        target_account=target_account,
        start_time=s_t,
        end_time=e_t,
        like_time=l_t,
        api_delay=api_delay,
        proxies=proxies,
    )


main()
