import psycopg2
from psycopg2 import Error
from psycopg2 import sql

#connection = psycopg2.connect("host=89.208.231.41 dbname=VTB-Hack user=user password=262}ym2C0A79vdFw")

# Самые подходящие новости для этой роли
# мексимально 5 новостей
def main_news(type_person):
    # соединение с БД
    connection = psycopg2.connect(
        user="user",
        password="262}ym2C0A79vdFw",
        host="89.208.231.41",
        database="VTB-Hack"
    )
    try:
        # запрос к БД
        cursor = connection.cursor()


        cursor.execute(sql.SQL("SELECT id FROM {} WHERE (role = 2 or role = " + type_person + ") ORDER BY id DESC LIMIT 100").format(sql.Identifier('RSSTable')))
        news_records = cursor.fetchall()
        print(news_records[-1][0])


        cursor.execute(sql.SQL("SELECT title, link, source_name, publish_date, description, subjects_category FROM {} WHERE (role = 2 or role = " + type_person + ") and id > " + str(news_records[-1][0]) + " ORDER BY score DESC LIMIT 4").format(sql.Identifier('RSSTable')))


        # считываем данные
        news_records = cursor.fetchall()
        print(news_records)

        # хранение результата
        mas_news = []


        for row in news_records:
            mas_news.append(row)
        return mas_news


    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")


def show_trend():
    # соединение с БД
    connection = psycopg2.connect(
        user="user",
        password="262}ym2C0A79vdFw",
        host="89.208.231.41",
        database="VTB-Hack"
    )
    try:
        # запрос к БД
        cursor = connection.cursor()
        cursor.execute(sql.SQL("SELECT trend, insight FROM {} ORDER BY id DESC LIMIT 1").format(sql.Identifier('TrendsInsightsTable')))
        # считываем данные
        news_records = cursor.fetchall()

        return news_records


    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")




def create_trend(trend, inside):
    # соединение с БД
    connection = psycopg2.connect(
        user="user",
        password="262}ym2C0A79vdFw",
        host="89.208.231.41",
        database="VTB-Hack"
    )
    try:
        # запрос к БД
        cursor = connection.cursor()
        cursor.execute(sql.SQL("INSERT INTO \"TrendsInsightsTable\" (trend, insight) VALUES (%s, %s)"), (trend, inside))
        connection.commit()
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")


def get_analis_db():
    # соединение с БД
    connection = psycopg2.connect(
        user="user",
        password="262}ym2C0A79vdFw",
        host="89.208.231.41",
        database="VTB-Hack"
    )
    try:
        # запрос к БД
        cursor = connection.cursor()
        cursor.execute(sql.SQL("SELECT * FROM {} ORDER BY count DESC").format(sql.Identifier('ClusterTable')))
        # считываем данные
        news_records = cursor.fetchall()

        return news_records

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")




print(main_news('1'))