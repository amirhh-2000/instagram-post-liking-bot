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


def file_content_parsing(content: bin) -> dict:
    accounts = {}
    content = content.decode('ascii')
    content = content.split("\r\n")
    if not content[-1]:
        content = content[:-1]
    for item in content:
        item = item.split(' ')
        if len(item) == 2:
            item.append(False)
        username = item[0]
        pass_and_proxy = item[1:]
        accounts[username] = pass_and_proxy
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


def app(creepy_accounts: dict[str, list], target_account: str, start_time: str, end_time: str, like_time: str) -> None:
    with open('bot.png', 'rb') as photo:
        put_image(photo.read(), width='10%', height='10%', position=-1)
    with put_loading(shape='border', color='info'):
        put_text("Hello :) i'm running 🤭")
        put_scrollable(put_scope('scrollable'), height=420, keep_bottom=True)
        put_markdown(f"Time between each like set as `{like_time}` seconds", scope='scrollable')
        jobs = []
        # Handle UI messages
        job_thread = threading.Thread(target=ui_messages)
        job_thread.start()
        jobs.append(job_thread)
        # Creating bot instance for each account
        for username, passwd_and_proxy in creepy_accounts.items():
            print(username, passwd_and_proxy)  # TODO: TEST
            password = passwd_and_proxy[0]
            proxy = passwd_and_proxy[1]

            bot = Bot(start_time=start_time, end_time=end_time, like_time=like_time)
            put_markdown(f"I run `{username}` from **{bot.start_time}** to **{bot.end_time}** o'clock", scope='scrollable')
            put_markdown(f"*`{username}` scheduled successfully*", scope='scrollable')
            # Run the creepies [with Smile ;)]
            time.sleep(7)
            job_thread = threading.Thread(target=bot.schedule_and_run, args=(username, password, target_account, proxy))
            job_thread.start()
            jobs.append(job_thread)
        for job in jobs:
            job.join()
        put_text("bye bye 😴", scope='scrollable')


def main():
    info = input_group("Accounts", [
        input("Input your username: ", name="username", type=TEXT, placeholder="Username", validate=validate_username),
        input("Input your password: ", name="password", type=PASSWORD, placeholder="Password"),
        input("Input a proxy (optional): ", name="proxy", type=TEXT, placeholder="Proxy", required=False),
        file_upload(
            "Or select a txt file for accounts and proxies: ",
            name="accounts",
            accept="file/*",
            required=False
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
        input("How many seconds to wait for each like?", name="like_t", type=FLOAT,
              placeholder="time between each like"),
    ])

    # Creepy accounts
    creepy_username = info['username']
    creepy_password = info['password']
    # Check file exists
    accounts_file = info['accounts']
    accounts = {}
    if accounts_file:
        file_content = info['accounts']['content']
        accounts = file_content_parsing(file_content)
    else:
        accounts[creepy_username] = [creepy_password, None]
        if info['proxy']:
            accounts[creepy_username][1] = info['proxy']

    # Target account
    target_account = info['target']
    # Timing
    s_t = scheduling['start_t']
    e_t = scheduling['end_t']
    l_t = scheduling['like_t']
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
    )


main()
