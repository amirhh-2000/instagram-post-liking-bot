import time
from datetime import datetime
import logging

from instagram_private_api import Client

logging.basicConfig(
    filename='report.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(filename)s - %(message)s'
)

UI_messages = set()  # Forwards program logs to UI
time_frame = dict()  # For scheduling


class InstaBot:
    def __init__(self, username: str, password: str, target_account: str, api_call_delay: float, proxy=False):
        self.username = username
        self.password = password
        self.target_account = target_account
        self.api_call_delay = api_call_delay
        if proxy:
            self.api = Client(username, password, proxy=proxy)
        else:
            self.api = Client(username, password)
        self.like_counter = 0
        logging.info(f'"{username}" bot is logged in and started.')
        # --- UI MSG ---
        UI_messages.add(f"I'm logged in as `{username}`")

    def job(self, like_time: float) -> bool:
        # --- UI MSG ---
        UI_messages.add(f"`{self.username}` is liking...")
        user_id = self._get_user_id(self.target_account)
        for media_id in self._tagged_post_ids(user_id):
            if media_id:
                self.api.post_like(media_id)
                print(f"'{self.username}' liked a post")  # To show log to end-user
                self.like_counter += 1
                logging.info(f'"{self.username}" liked a post; media_id: {media_id} - Count: {self.like_counter}')
                time.sleep(like_time)
            if self.like_counter % 15 == 0:
                # --- UI MSG ---
                UI_messages.add(f"`{self.username}` have liked `{self.like_counter}` posts and more so far")
        return True

    def _get_user_id(self, username: str) -> str:
        info = self.api.username_info(username)
        user_id = info['user']['pk']
        return user_id

    def _tagged_post_ids(self, user_id: str) -> str:
        """
        Get tagged posts and return post_id to like it
        :param user_id: The specific user_id
        :return: post_id
        """
        next_max_id = ''
        while True:
            if datetime.now() >= time_frame['et']:
                UI_messages.add("Time ended, I stopped 🥲")
                return None
            response = self.api.usertag_feed(user_id, **{'max_id': next_max_id})
            time.sleep(self.api_call_delay)
            for i in range(int(response['num_results'])):
                post_id = response['items'][i]['id']
                has_liked = response['items'][i]['has_liked']
                if not has_liked:
                    yield post_id
            if 'next_max_id' in response.keys():
                next_max_id = response['next_max_id']
            else:
                break


class Bot:
    def __init__(self, **kwargs):
        self.start_time: str = kwargs['start_time']
        self.end_time: str = kwargs['end_time']
        self.like_time: float = float(kwargs['like_time'])
        self.api_delay: float = float(kwargs['api_delay'])
        logging.info(f'Bot is scheduling...')

    def schedule_and_run(self, username, password, target_account, proxy):
        current_time = datetime.now()
        # Start time
        s_hour, s_minute = self.start_time[:2], self.start_time[3:]
        # End time
        e_hour, e_minute = self.end_time[:2], self.end_time[3:]
        # Set time object
        start_time = current_time.replace(hour=int(s_hour), minute=int(s_minute), second=0, microsecond=0)
        end_time = current_time.replace(hour=int(e_hour), minute=int(e_minute), second=0, microsecond=0)
        # Check time conflict
        if start_time >= end_time:
            tomorrow = current_time.day + 1
            end_time = end_time.replace(day=tomorrow)
        # Scheduling dictionary
        time_frame['st'] = start_time
        time_frame['et'] = end_time
        # Run
        while True:
            current_time = datetime.now()
            if start_time <= current_time:
                insta_bot_instance = InstaBot(
                    username=username,
                    password=password,
                    target_account=target_account,
                    api_call_delay=self.api_delay,
                    proxy=proxy,
                )
                result = insta_bot_instance.job(self.like_time)
                time.sleep(3)
                if result:
                    UI_messages.add("**All done or time ended**")
                    break
            if end_time <= current_time:
                # --- UI MSG ---
                UI_messages.add(f"*Time frame has passed!*")
                break
            time.sleep(1)


if __name__ == '__main__':
    pass
