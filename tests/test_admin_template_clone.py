import pytest
from uuid import uuid4
from app.models import User, Category, AssessmentTemplate
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

@pytest.mark.asyncio
async def test_clone_assessment_template(test_db, mock_admin):
    # Use admin_id returned by mock_admin fixture
    admin_id = mock_admin
    category_id = str(uuid4())
    template_id = str(uuid4())

    # Create DB records
    admin = User(id=admin_id, name="Admin", email=f"admin+{uuid4().hex[:8]}@example.com", role="admin")
    category = Category(id=category_id, name=f"Fellowship {uuid4().hex[:6]}")
    template = AssessmentTemplate(id=template_id, name="Original Template")
    template.category = category

    test_db.add_all([admin, category, template])
    test_db.commit()

    token = f"Bearer {admin_id}"

    # Perform clone request
    response = client.post(
        f"/admin/templates/{template_id}/clone",
        headers={"Authorization": token}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"].startswith("Original Template")
    assert data["category_id"] == category_id
