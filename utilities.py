import psycopg2

def insert_row(conn,
                schema="public",
                table="",
                columns=[],
                data=()):
    """ Insert multiple rows into the specified table  """
    # print("Inserting to DB ")
    cols = ", ".join(columns)
    vals = ",".join(len(columns)*["%s"])
    sql = f"INSERT INTO {schema}.{table}({cols}) VALUES("+ vals +");"
    try:
        with  conn.cursor() as cur:
            # execute the INSERT statement
            cur.execute(sql, data)
        # commit the changes to the database
        conn.commit()
        # print("Inserted to DB ")
    except (Exception, psycopg2.DatabaseError) as error:
        print("DB save failed with error: ", error)


def prepare_met_array(met_sample):
        new = [
            float(m) if isinstance(m, (int, float)) else
            1.0 if m is True else
            0.0 if m is False else
            0.0 # for None
            for m in met_sample
        ]
        print("new ", new)
        return new