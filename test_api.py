import requests
import pytest
import allure

BASE_URL = "https://jsonplaceholder.typicode.com/posts"

new_post = {
    "title": "New Post",
    "body": "This is the body of the new post.",
    "userId": 1
}


@pytest.fixture()
def create_post():
    response = requests.post(BASE_URL, json=new_post)
    yield response
    #requests.delete(f"{BASE_URL}/{response.json()['id']}")  # Удаляет пост после теста


class TestCreatePost:
    @allure.title('Проверяем что код ответа = 201')
    def test_create_post_status_code(self, create_post):
        """Тест на создание нового поста."""
        assert create_post.status_code == 201, f"Expected status code 201, but got {create_post.status_code}"

    @allure.title('Проверяем что в теле ответа присутствует ID поста')
    def test_create_post_id_in_response(self, create_post):
        assert "id" in create_post.json(), "Response does not contain 'id'"

    @allure.title('Проверяем что поля поста соответствуют созданным')
    @pytest.mark.parametrize(
        'check_field_name',
        ["title", "body", "userId"]
    )
    def test_create_post_fields(self, create_post, check_field_name):
        assert create_post.json()[check_field_name] == new_post[check_field_name], \
            f"Expected title '{new_post[check_field_name]}', but got '{create_post.json()[check_field_name]}'"

    @allure.title('Проверяем что можно создать пост без одного из полей')
    @pytest.mark.parametrize(
        'missing_field_name',
        ["title", "body", "userId"]
    )
    def test_create_post_without_one_field(self, missing_field_name):
        del new_post[missing_field_name]
        response = requests.post(BASE_URL, json=new_post)
        assert response.status_code == 201, f"Expected status code 201, but got {response.status_code}"

    @allure.title('Проверяем что можно создать пост без тела запроса')
    def test_create_post_without_request_body(self):
        response = requests.post(BASE_URL)
        assert response.status_code == 201, f"Expected status code 201, but got {response.status_code}"


class TestGetPost:
    @allure.title('Проверяем что при запросе несуществующего поста код ответа = 404')
    def test_get_nonexistent_post_status_code(self):
        response_get_posts = requests.get(f"{BASE_URL}")
        last_post_id = response_get_posts.json()[-1]["id"]
        non_existent_id = last_post_id + 1
        response = requests.get(f"{BASE_URL}/{non_existent_id}")
        assert response.status_code == 404, f"Expected status code 404, but got {response.status_code}"

    @allure.title('Проверяем что код ответа при получении всех постов = 200')
    def test_get_all_posts_status_code(self):
        response = requests.get(f"{BASE_URL}")
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

    @allure.title('Проверяем что код ответа при получении поста по id = 200')
    def test_get_post_by_id_status_code(self):
        response_get_posts = requests.get(f"{BASE_URL}")
        post_id = response_get_posts.json()[0]["id"]
        response = requests.get(f"{BASE_URL}/{post_id}")
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

    @allure.title('Проверяем что при получении поста по ID в ответе присутствуют все поля')
    def test_get_post_by_id_response_body(self):
        response_get_posts = requests.get(f"{BASE_URL}")
        post_by_id = response_get_posts.json()[0]
        response = requests.get(f"{BASE_URL}/{post_by_id["id"]}")
        assert response.json() == post_by_id, f"Response does not match expected post. Got: {response.json()}"


class TestUpdatePost:
    @allure.title('Проверяем что код ответа при полном обновлении данных поста = 200')
    def test_full_data_update_status_code(self):
        response_get_posts = requests.get(f"{BASE_URL}")
        post_by_id = response_get_posts.json()[0]["id"]
        updated_post = {
            "id": post_by_id,
            "title": "Updated Title",
            "body": "Updated body text.",
            "userId": 1
        }
        response = requests.put(f"{BASE_URL}/{post_by_id}", json=updated_post)
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

    @allure.title('Проверяем что в ответе пришел обновленный пост')
    def test_full_data_update_response(self):
        response_get_posts = requests.get(f"{BASE_URL}")
        post_by_id = response_get_posts.json()[0]["id"]
        updated_post = {
            "id": post_by_id,
            "title": "Updated Title",
            "body": "Updated body text.",
            "userId": 1
        }
        response = requests.put(f"{BASE_URL}/{post_by_id}", json=updated_post)
        assert response.json() == updated_post, f"Response does not match expected post. Got: {response.json()}"

    @allure.title('Проверяем что код ответа при попытке полностью обновить несуществующий пост = 404')
    def test_full_data_update_non_existent_post_status_code(self):
        response_get_posts = requests.get(f"{BASE_URL}")
        last_post_id = response_get_posts.json()[-1]["id"]
        non_existent_id = last_post_id + 1
        updated_post = {
            "id": last_post_id,
            "title": "Updated Title",
            "body": "Updated body text.",
            "userId": 1
        }
        response = requests.put(f"{BASE_URL}/{non_existent_id}", json=updated_post)
        assert response.status_code == 404, f"Expected status code 404, but got {response.status_code}"


    @allure.title('Проверяем что код ответа при частичном обновлении данных поста = 200')
    def test_partial_data_update_status_code(self):
        response_get_posts = requests.get(f"{BASE_URL}")
        post_by_id = response_get_posts.json()[0]["id"]
        updated_field = {"title": "Updated Title"}
        response = requests.patch(f"{BASE_URL}/{post_by_id}", json=updated_field)
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

    @pytest.mark.parametrize(
        'field_name, data',
        [("title", "Updated Title"), ("body", "Updated body text."), ("userId", 3)]
    )
    @allure.title('Проверяем что при обновлении поля в ответе пришел обновленный пост')
    def test_partial_data_update_response(self, field_name, data):
        response_get_posts = requests.get(f"{BASE_URL}")
        post_by_id = response_get_posts.json()[0]["id"]
        updated_field = {field_name: data}
        response = requests.patch(f"{BASE_URL}/{post_by_id}", json=updated_field)
        updated_post = response_get_posts.json()[0]
        updated_post[field_name] = data
        assert response.json() == updated_post, f"Response does not match expected post. Got: {response.json()}"

    @allure.title('Проверяем что код ответа при попытке обновить поле в несуществующем посте = 404')
    def test_partial_data_update_non_existent_post_status_code(self):
        response_get_posts = requests.get(f"{BASE_URL}")
        last_post_id = response_get_posts.json()[-1]["id"]
        non_existent_id = last_post_id + 1
        updated_field = {"title": "Updated Title"}
        response = requests.patch(f"{BASE_URL}/{non_existent_id}", json=updated_field)
        assert response.status_code == 404, f"Expected status code 404, but got {response.status_code}"

class TestDeletePost:
    @allure.title('Проверяем что код ответа при удалении поста = 200')
    def test_delete_post_status_code(self, create_post):
        post_id = create_post.json()["id"]
        response = requests.delete(f"{BASE_URL}/{post_id}")
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

    @allure.title('Проверяем что код ответа при удалении несуществующего поста = 404')
    def test_delete_non_existent_post_status_code(self):
        response_get_posts = requests.get(f"{BASE_URL}")
        last_post_id = response_get_posts.json()[-1]["id"]
        non_existent_id = last_post_id + 1
        response = requests.delete(f"{BASE_URL}/{non_existent_id}")
        assert response.status_code == 404, f"Expected status code 404, but got {response.status_code}"
