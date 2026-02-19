def test_workflow_start_and_thumbnail_finalize(client):
    start_response = client.post(
        "/api/v1/workflows/start",
        json={
            "topic": "Testing",
            "platforms": ["youtube"],
            "user_id": "test_user",
            "brand_voice": "educational",
        },
    )

    assert start_response.status_code == 200
    start_data = start_response.json()

    assert start_data["status"] == "awaiting_approval"
    assert start_data["current_step"] == "awaiting_approval"
    assert start_data["requires_action"] == "script_approval"
    assert len(start_data["scripts"]) == 3

    workflow_id = start_data["workflow_id"]

    status_response = client.get(f"/api/v1/workflows/{workflow_id}/status")
    assert status_response.status_code == 200

    selected_script_id = start_data["scripts"][0]["id"]
    approve_response = client.post(
        f"/api/v1/workflows/{workflow_id}/approve",
        json={
            "action": "approve",
            "selected_script_id": selected_script_id,
        },
    )

    assert approve_response.status_code == 200
    approve_data = approve_response.json()

    assert approve_data["status"] == "awaiting_thumbnail_selection"
    assert approve_data["current_step"] == "awaiting_thumbnail_selection"
    assert approve_data["requires_action"] == "thumbnail_selection"
    assert approve_data["selected_script_id"] == selected_script_id
    assert len(approve_data["thumbnails"]) == 3

    selected_thumbnail_id = approve_data["thumbnails"][0]["id"]
    select_thumbnail_response = client.post(
        f"/api/v1/workflows/{workflow_id}/select-thumbnail",
        json={
            "selected_thumbnail_id": selected_thumbnail_id,
        },
    )

    assert select_thumbnail_response.status_code == 200
    ab_testing_data = select_thumbnail_response.json()

    # After thumbnail selection, workflow enters A/B testing phase
    assert ab_testing_data["status"] == "ab_testing"
    assert ab_testing_data["current_step"] in ["ab_testing", "ab_test_complete"]
    assert ab_testing_data["requires_action"] == "ab_test_monitoring"

    # Check AB test status
    ab_status_response = client.get(f"/api/v1/workflows/{workflow_id}/ab-status")
    assert ab_status_response.status_code == 200
    ab_status = ab_status_response.json()
    assert ab_status["is_running"] is True
    assert len(ab_status["variants"]) == 3

    # Manually declare winner to complete the workflow
    declare_winner_response = client.post(
        f"/api/v1/workflows/{workflow_id}/declare-winner",
        json={
            "thumbnail_id": selected_thumbnail_id,
        },
    )

    assert declare_winner_response.status_code == 200
    complete_data = declare_winner_response.json()

    assert complete_data["status"] == "completed"
    assert complete_data["current_step"] == "completed"
    assert complete_data["selected_thumbnail_id"] == selected_thumbnail_id

    # Check final results
    results_response = client.get(f"/api/v1/workflows/{workflow_id}/results")
    assert results_response.status_code == 200
    results = results_response.json()
    assert results["status"] == "completed"
    assert results["export_ready"] is True
    assert results["winning_content"]["script"] is not None
    assert results["winning_content"]["thumbnail"] is not None
    assert results["ab_test_summary"]["was_manual_override"] is True
