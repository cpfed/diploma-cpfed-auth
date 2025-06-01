from django.http import HttpResponse
from django.db import connection


def get_kcpc_res():
    contest_ids = [1, 4, 8]
    subq = '''COALESCE((SELECT U0."points"
                                  FROM "contest_contestresult" U0
                                           INNER JOIN "contest_usercontest" U1 ON (U0."user_reg_id" = U1."id")
                                  WHERE (U1."contest_id" = {id} AND U1."user_id" = ("authentication_mainuser"."id"))
                                  LIMIT 1), 0.0
                        )'''
    q = f'''WITH first_cte as (SELECT authentication_mainuser.id,
                          authentication_mainuser.first_name || ' ' || authentication_mainuser.last_name as "full_name",
                          authentication_mainuser.region_id,
                          array [{", ".join(subq.format(id=id) for id in contest_ids)}] AS "result_array"
                   FROM "authentication_mainuser"
                            INNER JOIN "contest_usercontest"
                                       ON ("authentication_mainuser"."id" = "contest_usercontest"."user_id" and "contest_id"={contest_ids[-1]})
                   group by "authentication_mainuser"."id"),
    second_cte as (select id,
                       full_name,
                       region_id,
                       result_array,
                       (SELECT sum(x) - min(x) FROM unnest(result_array) AS x) AS total_points
                from first_cte)
    select id,
           full_name,
           region_id,
           result_array,
           total_points,
           rank() over (order by total_points desc) as rank
    from second_cte
    '''
    with connection.cursor() as cursor:
        cursor.execute(q)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return results
