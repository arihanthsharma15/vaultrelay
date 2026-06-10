from app.services.sql_guard import validate_sql


def test_valid_select():
    sql = "SELECT * FROM users LIMIT 100"
    assert validate_sql(sql) is True


def test_insert_rejected():
    sql = "INSERT INTO users VALUES (1)"
    assert validate_sql(sql) is False


def test_delete_rejected():
    sql = "DELETE FROM users"
    assert validate_sql(sql) is False


def test_update_rejected():
    sql = "UPDATE users SET name='abc'"
    assert validate_sql(sql) is False
