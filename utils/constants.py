from django.utils.translation import gettext_lazy as _

# T-Shirt sizes
SMALL = "S"
MEDIUM = "M"
LARGE = "L"
EXTRA_LARGE = "XL"
EXTRA_EXTRA_LARGE = "XXL"

T_SHIRT_SIZES = (
    (SMALL, SMALL),
    (MEDIUM, MEDIUM),
    (LARGE, LARGE),
    (EXTRA_LARGE, EXTRA_LARGE),
    (EXTRA_EXTRA_LARGE, EXTRA_EXTRA_LARGE),
)

# # Olympiad Achievements
# GOLD = "GOLD"
# SILVER = "SILVER"
# BRONZE = "BRONZE"
# PARTICIPANT = "PARTICIPANT"
#
# OLYMPIAD_ACHIEVEMENTS = (
#     (GOLD, "Золото"),
#     (SILVER, "Серебро"),
#     (BRONZE, "Бронза"),
#     (PARTICIPANT, "Участник")
# )
#
# # Contest Platforms
# CODEFORCES = "CODEFORCES"
# ATCODER = "ATCODER"
# LEETCODE = "LEETCODE"
#
# CONTEST_HOST_PLATFORMS = (
#     (CODEFORCES, "Codeforces"),
#     (ATCODER, "Atcoder"),
#     (LEETCODE, "Leetcode")
# )

# Genders
MAN = "MAN"
WOMAN = "WOMAN"
NON_BINARY = "NON_BINARY"

GENDER = (
    (MAN, _("Мужской")),
    (WOMAN, _("Женский")),
    (NON_BINARY, _("Небинарный"))
)

# Employment status
WORKING = "WORKING"
STUDYING = "STUDYING"
NOT_WORKING_AND_STUDYING = "NOT_WORKING_AND_STUDYING"

EMPLOYMENT_STATUS = (
    (WORKING, _("Работаю")),
    (STUDYING, _("Учусь")),
    (NOT_WORKING_AND_STUDYING, _("Не учусь и не работаю"))
)
