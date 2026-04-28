import os
os.environ["SECRET_KEY"] = "test-secret"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"

from app.models.tenant import Tenant


def test_tenant_repr():
    tenant = Tenant(id="123", name="Acme Corp", api_key_hash="hashvalue")
    assert "Acme Corp" in repr(tenant)


def test_tenant_fields():
    tenant = Tenant(
        name="Test Co",
        api_key_hash="hashvalue",
        is_active=True,
    )
    assert tenant.name == "Test Co"
    assert tenant.api_key_hash == "hashvalue"
    assert tenant.is_active is True
