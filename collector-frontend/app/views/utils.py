from sqlalchemy.exc import IntegrityError
from app.models import db
from app.exceptions.Error import Error

# support mappings
tag_mappings = {
    27: "女の子",
    48486: "獣娘",
    31: "泣カセテミロ",
    419: "MIKUMIKUDANCE",
    6859: "アナログ",
    30: "落書キ",
    459529: "イクシオンサーガコンテスト",
    2458: "擬人化",
    443608: "ソードアートアバター&武器コンテスト",
    459530: "ハイペリオン",
}

reverse_tag_mappings = {
    '女の子': 27,
    '獣娘': 48486,
    '泣カセテミロ': 31,
    'MIKUMIKUDANCE': 419,
    'アナログ': 6859,
    '落書キ': 30,
    'イクシオンサーガコンテスト': 459529,
    '擬人化': 2458,
    'ソードアートアバター&武器コンテスト': 443608,
    'ハイペリオン': 459530
 }

# Helper Functions
def insert_db(item):
    try:
        db.session.add(item)
        db.session.commit()
    except IntegrityError as e:
        status_code = e.orig.args[0]
        message = e.orig.args[1]
        raise Error(
            "Database_Error",
            message,
            status_code
        )
