import sqlite3
import datetime


class DatabaseHandler:

    def __init__(self, file):
        self.connection = sqlite3.connect(file, check_same_thread=False)

    def sql_operation_processing(self, operation, tup):
        cursor = self.connection.cursor()
        cursor.execute(operation, tup)
        self.connection.commit()
        cursor.close()

    def get_class_name(self, telegram_id):
        cursor = self.connection.cursor()
        result = cursor.execute(f"SELECT class_name FROM teachers WHERE telega_id='{telegram_id}'").fetchone()
        cursor.close()

        return result

    def get_kids_list(self, class_name):
        cursor = self.connection.cursor()
        result = cursor.execute(
            f"SELECT child_id, child_name FROM childrens WHERE class_name='{class_name}'").fetchall()
        cursor.close()

        return result

    def get_absence_reasons_list(self):
        cursor = self.connection.cursor()
        result = cursor.execute("SELECT * from reasons").fetchall()
        cursor.close()

        return result

    def is_child_in_report(self, child_id):
        day = datetime.datetime.now().strftime("%Y-%m-%d")

        cursor = self.connection.cursor()
        result = cursor.execute(f"SELECT*FROM kuramshin_otchet WHERE child_id='{child_id}' AND date='{day}'").fetchall()
        cursor.close()

        return bool(result)

    def get_data(self, req, tup=()):
        cursor = self.connection.cursor()
        result = cursor.execute(req, tup).fetchall()
        cursor.close()

        return result

    def get_all_teachers(self):
        cursor = self.connection.cursor()
        result = cursor.execute("SELECT * from teachers")
        cursor.close()

        return result

    def get_teachers_id(self):
        cursor = self.connection.cursor()
        result = cursor.execute("SELECT telega_id FROM teachers").fetchall()
        cursor.close()

        return result

    def get_reports(self, date):
        cursor = self.connection.cursor()
        result = cursor.execute(
            f"SELECT telega_id, class_name, class_total_len, present_len, reason, date, time\
              FROM kuramshin_otchet INNER JOIN teachers USING(telega_id) WHERE date='{date}'").fetchall()
        cursor.close()

        return result

    def is_reports_from_teacher(self, teacher_id, date) -> bool:
        cursor = self.connection.cursor()
        result = cursor.execute(f"SELECT date FROM otchet WHERE telega_id ='{teacher_id}' AND date='{date}'").fetchall()
        cursor.close()

        return bool(result)

    def is_user_in_table(self, telegram_id, table) -> bool:
        cursor = self.connection.cursor()
        result = cursor.execute(f"SELECT * FROM {table} WHERE telega_id='{telegram_id}'").fetchall()
        cursor.close()

        return bool(result)

    def total_len_bool(self, message_id, size) -> bool:
        cursor = self.connection.cursor()
        result = cursor.execute(f"SELECT class_total_len FROM teachers WHERE telega_id ='{message_id}'").fetchone()
        cursor.close()

        return int(result[0]) >= int(size)
