from decimal import Decimal

import pytest

from src.part2 import cart, crud, storage, utils


def test_normalize_price_examples():
    assert utils.normalize_price(Decimal("12.999")) == Decimal("13.00")
    assert utils.normalize_price(Decimal("2.3451")) == Decimal("2.35")
    assert utils.normalize_price(Decimal("2.3449")) == Decimal("2.34")
    assert utils.normalize_price(Decimal("5")) == Decimal("5.00")


def test_generate_product_id():
    assert crud.generate_product_id([]) == storage.PRODUCT_ID_MIN

    st = [
        (1, "A", Decimal("1.00"), 1),
        (7, "B", Decimal("2.00"), 2),
    ]
    assert crud.generate_product_id(st) == 8


def test_create_product():
    st = []
    pid = crud.create_product(st, ("Apple", Decimal("2.345"), 10))

    assert pid == 1
    assert st == [(1, "Apple", Decimal("2.35"), 10)]


def test_create_product_duplicate_name(capsys):
    st = [(1, "Apple", Decimal("1.00"), 1)]

    assert crud.create_product(st, ("Apple", Decimal("2.00"), 2)) is None
    assert st == [(1, "Apple", Decimal("1.00"), 1)]

    out = capsys.readouterr().out
    assert "Apple" in out


def test_read_product(capsys):
    st = [(1, "Apple", Decimal("1.00"), 1)]

    assert crud.read_product(st, 1) == (1, "Apple", Decimal("1.00"), 1)
    assert crud.read_product(st, 99) is None

    out = capsys.readouterr().out
    assert "99" in out


def test_update_product_same_name_and_normalize():
    st = [
        (1, "Apple", Decimal("1.00"), 1),
        (2, "Banana", Decimal("2.00"), 2),
    ]

    res = crud.update_product(st, 1, ("Apple", Decimal("3.456"), 5))

    assert res == (1, "Apple", Decimal("3.46"), 5)
    assert st[0] == (1, "Apple", Decimal("3.46"), 5)


def test_update_product_allows_duplicate_name():
    st = [
        (1, "Apple", Decimal("1.00"), 1),
        (2, "Banana", Decimal("2.00"), 2),
    ]

    res = crud.update_product(st, 1, ("Banana", Decimal("3.00"), 3))

    assert res == (1, "Banana", Decimal("3.00"), 3)


def test_update_product_missing(capsys):
    st = [(1, "Apple", Decimal("1.00"), 1)]

    assert crud.update_product(st, 99, ("X", Decimal("1.00"), 1)) is None
    assert "99" in capsys.readouterr().out


def test_delete_product_returns_id():
    st = [
        (1, "Apple", Decimal("1.00"), 1),
        (2, "Banana", Decimal("2.00"), 2),
    ]

    assert crud.delete_product(st, 2) == 2
    assert st == [(1, "Apple", Decimal("1.00"), 1)]


def test_delete_product_missing(capsys):
    st = []

    assert crud.delete_product(st, 99) is None
    assert "99" in capsys.readouterr().out


def make_storage():
    return [
        (1, "Apple", Decimal("1.00"), 10),
        (2, "Banana", Decimal("2.00"), 5),
    ]


def test_add_to_cart_new_line():
    st = make_storage()
    c = []

    assert cart.add_to_cart(st, c, 1, 3) == (1, 3)
    assert c == [(1, 3)]
    assert st[0][3] == 7


def test_add_to_cart_existing_line():
    st = make_storage()
    c = [(1, 2)]

    assert cart.add_to_cart(st, c, 1, 3) == (1, 5)
    assert c == [(1, 5)]
    assert st[0][3] == 7


def test_add_to_cart_not_enough(capsys):
    st = make_storage()
    c = []

    assert cart.add_to_cart(st, c, 1, 11) is None
    assert c == []
    assert st[0][3] == 10

    out = capsys.readouterr().out
    assert "1" in out
    assert "10" in out
    assert "11" in out


def test_add_to_cart_unknown(capsys):
    st = make_storage()
    c = []

    assert cart.add_to_cart(st, c, 99, 1) is None
    assert c == []
    assert "99" in capsys.readouterr().out


def test_remove_from_cart_partial():
    st = make_storage()
    c = [(1, 5)]

    assert cart.remove_from_cart(st, c, 1, 2) == (1, 3)
    assert c == [(1, 3)]
    assert st[0][3] == 12


def test_remove_from_cart_full():
    st = make_storage()
    c = [(1, 3)]

    assert cart.remove_from_cart(st, c, 1, 3) == (1, 0)
    assert c == []
    assert st[0][3] == 13


def test_remove_from_cart_not_in_cart(capsys):
    st = make_storage()
    c = []

    assert cart.remove_from_cart(st, c, 1, 1) is None
    assert c == []
    assert "1" in capsys.readouterr().out


def test_remove_from_cart_too_many(capsys):
    st = make_storage()
    c = [(1, 2)]

    assert cart.remove_from_cart(st, c, 1, 3) is None
    assert c == [(1, 2)]
    assert st[0][3] == 10

    out = capsys.readouterr().out
    assert "1" in out
    assert "2" in out
    assert "3" in out


def test_remove_from_cart_product_missing_from_storage(capsys):
    st = []
    c = [(1, 2)]

    assert cart.remove_from_cart(st, c, 1, 1) is None
    assert c == [(1, 2)]
    assert "1" in capsys.readouterr().out


def test_cart_storage_balance_invariant():
    st = make_storage()
    c = []

    total = st[0][3]

    cart.add_to_cart(st, c, 1, 4)
    assert st[0][3] + c[0][1] == total

    cart.remove_from_cart(st, c, 1, 2)
    assert st[0][3] + c[0][1] == total