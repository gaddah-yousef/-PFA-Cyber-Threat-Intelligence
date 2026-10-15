def test_admin_can_update_user_role_and_activation(client, auth_headers):
    created = client.post(
        "/api/auth/users",
        headers=auth_headers,
        json={"email": "viewer@test.local", "password": "SuperSecret1", "role": "viewer"},
    ).json()

    response = client.patch(
        f"/api/auth/users/{created['id']}",
        headers=auth_headers,
        json={"role": "analyst", "is_active": False},
    )

    assert response.status_code == 200
    assert response.json()["role"] == "analyst"
    assert response.json()["is_active"] is False
    logs = client.get("/api/audit-logs", headers=auth_headers).json()
    assert any(
        item["action"] == "auth.update_user" and item["target_id"] == created["id"]
        for item in logs
    )


def test_admin_cannot_deactivate_own_account(client, auth_headers):
    current = client.get("/api/auth/me", headers=auth_headers).json()

    response = client.patch(
        f"/api/auth/users/{current['id']}",
        headers=auth_headers,
        json={"is_active": False},
    )

    assert response.status_code == 400

    demotion = client.patch(
        f"/api/auth/users/{current['id']}",
        headers=auth_headers,
        json={"role": "viewer"},
    )
    assert demotion.status_code == 400
