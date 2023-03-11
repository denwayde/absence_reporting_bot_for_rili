import asyncio

from datetime import datetime
from aiogram import Bot

from database import DatabaseHandler


class UsersNotifier:

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.db_handler = DatabaseHandler("mydatabase.db")

    async def start_notifies(self) -> None:
        """
        Sending notifies to every user.
        The function works every day.
        The function goes sleep for 15 minutes after check finished.
        """

        while True:
            current_time = self._get_current_time()
            rounded_time = self._get_rounded_time(current_time)
            rounded_time = self._convert_to_utc_0(rounded_time, "UTC+00:00")
            print(rounded_time)

            if rounded_time == "11:00":
                # teachers_ids = self.db_handler.get_data("SELECT telega_id FROM teachers")

                # for teacher_id in teachers_ids:
                #     await self.bot.send_message(teacher_id[0], "Доброго времени суток, отправьте пожалуйста отчет посещаемости")
                ids = self.db_handler.get_data("SELECT telega_id FROM teachers")
                d = datetime.now().strftime("%Y-%m-%d")
                for x in ids:
                    for v in self.db_handler.get_data("SELECT DISTINCT telega_id FROM kuramshin_otchet WHERE date = ?", (d,)):
                        if x == v:
                            ids.remove(v)
                for z in ids:
                    await self.bot.send_message(z[0], "Доброго времени суток, отправьте пожалуйста отчет посещаймости")
            await asyncio.sleep(900)

    def _get_current_time(self) -> str:
        moment = datetime.now()
        current_hour = str(moment.hour).rjust(2, "0")
        current_minute = str(moment.minute).rjust(2, "0")
        current_time = f"{current_hour}:{current_minute}"

        return current_time

    def _convert_to_utc_0(self, entered_time: str, from_utc: str):
        """
        Converting entered time to UTC+00:00
        """
        entered_time_hour, entered_time_minute = map(int, entered_time.split(":"))

        operand = from_utc[3]
        from_utc_dif = from_utc.split(operand)[-1]
        from_utc_hour_dif, from_utc_minute_dif = map(int, from_utc_dif.split(":"))

        if operand == "-":
            entered_time_hour = (entered_time_hour + from_utc_hour_dif) % 24
            entered_time_minute += from_utc_minute_dif
            entered_time_hour += entered_time_minute // 60
            entered_time_minute %= 24
            entered_time_minute %= 60

        else:
            entered_time_hour = (entered_time_hour - from_utc_hour_dif) % 24

            if entered_time_hour < 0:
                entered_time_hour = 24 + entered_time_hour

            entered_time_minute -= from_utc_minute_dif

            if entered_time_minute < 0:
                entered_time_hour -= 1
                entered_time_minute = 60 + entered_time_minute

            entered_time_hour %= 24
            entered_time_minute %= 60

        entered_time_hour = str(entered_time_hour).rjust(2, "0")
        entered_time_minute = str(entered_time_minute).rjust(2, "0")

        return f"{entered_time_hour}:{entered_time_minute}"

    def _get_rounded_time(self, time: str) -> str:
        """
        Rounding time to whole hours or half hours.
        """
        hour, minute = map(int, time.split(":"))
        new_time = ""

        if minute < 15:
            new_hour = str(hour).rjust(2, "0")
            new_time = f"{new_hour}:00"

        elif minute < 30:
            new_hour = str(hour).rjust(2, "0")
            new_time = f"{new_hour}:15"

        elif minute < 45:
            new_hour = str(hour).rjust(2, "0")
            new_time = f"{new_hour}:30"

        elif minute >= 45:
            new_hour = str((hour + 1) % 24)
            new_hour = new_hour.rjust(2, "0")
            new_time = f"{new_hour}:00"

        return new_time