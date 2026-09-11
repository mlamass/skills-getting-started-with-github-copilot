from src import app as app_module


class TestRoot:
    def test_root_redirects_to_static_index(self, client):
        # Arrange
        expected_location = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_location


class TestActivities:
    def test_get_activities_returns_activity_details(self, client):
        # Arrange
        expected_activity = "Chess Club"

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert expected_activity in response.json()
        assert {"description", "schedule", "max_participants", "participants"} <= set(
            response.json()[expected_activity]
        )


class TestSignup:
    def test_signup_adds_student_to_activity(self, client):
        # Arrange
        activity_name = "Art Club"
        email = "new.student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up {email} for {activity_name}"
        }
        assert email in app_module.activities[activity_name]["participants"]

    def test_signup_rejects_duplicate_student(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = app_module.activities[activity_name]["participants"][0]

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
        assert app_module.activities[activity_name]["participants"].count(email) == 1

    def test_signup_rejects_unknown_activity(self, client):
        # Arrange
        activity_name = "Unknown Club"
        email = "new.student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_requires_email(self, client):
        # Arrange
        activity_name = "Art Club"

        # Act
        response = client.post(f"/activities/{activity_name}/signup")

        # Assert
        assert response.status_code == 422


class TestUnregister:
    def test_unregister_removes_student_from_activity(self, client):
        # Arrange
        activity_name = "Art Club"
        email = "student.to.remove@mergington.edu"
        app_module.activities[activity_name]["participants"].append(email)

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Unregistered {email} from {activity_name}"
        }
        assert email not in app_module.activities[activity_name]["participants"]

    def test_unregister_rejects_unknown_student(self, client):
        # Arrange
        activity_name = "Art Club"
        email = "unknown.student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Student is not signed up for this activity"

    def test_unregister_rejects_unknown_activity(self, client):
        # Arrange
        activity_name = "Unknown Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
