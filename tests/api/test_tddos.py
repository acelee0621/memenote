import pytest
from fastapi.testclient import TestClient
from app.schemas.schemas import TodoResponse, NoteResponse



# # 测试创建独立的 todo
# def test_create_independent_todo(client: TestClient, mock_user):
#     response = client.post("/todos/", json={"content": "Independent task"})
#     assert response.status_code == 201
#     todo = TodoResponse.model_validate(response.json())
#     assert todo.content == "Independent task"
#     assert todo.note_id is None
#     assert todo.user_id == mock_user.id
#     assert todo.id is not None


# # 测试创建归属于 note 的 todo
# def test_create_todo_under_note(client: TestClient, mock_user):
#     # 创建 note
#     note_resp = client.post("/notes/", json={"title": "Note", "content": "Note content"})
#     assert note_resp.status_code == 201
#     note_id = note_resp.json()["id"]

#     # 创建关联 todo，使用查询参数传递 note_id
#     response = client.post(
#         "/todos/",
#         json={"content": "Task under note"},
#         params={"note_id": note_id}  # note_id 移到查询参数
#     )
#     assert response.status_code == 201
#     todo = TodoResponse.model_validate(response.json())
#     assert todo.content == "Task under note"
#     assert todo.note_id == note_id
#     assert todo.user_id == mock_user.id
#     assert todo.id is not None
    
    
# # 测试创建 todo 时使用不存在的 note_id
# def test_create_todo_with_invalid_note_id(client: TestClient):
#     response = client.post(
#         "/todos/",
#         json={"content": "Task with invalid note"},
#         params={"note_id": 9999}  # 假设 9999 不存在
#     )
#     assert response.status_code == 404
#     assert "Note with id 9999 not found" in response.text


@pytest.mark.parametrize(
    "note_id, expected_status, expected_note_id, content",
    [
        (None, 201, None, "Independent task"),  # 独立 todo
        ("valid", 201, "dynamic", "Task under note"),  # 归属 note 的 todo
        (9999, 404, None, "Task with invalid note"),  # 无效 note_id
    ],
    ids=["independent", "under_note", "invalid_note_id"]  # 为每个用例命名
)
def test_create_todo(client: TestClient, mock_user, note_id, expected_status, expected_note_id, content):
    # 处理 note_id：如果是 "valid"，动态创建 note
    actual_note_id = note_id
    if note_id == "valid":
        note_resp = client.post("/notes/", json={"title": "Note", "content": "Note content"})
        assert note_resp.status_code == 201
        actual_note_id = note_resp.json()["id"]    
    # 发送创建 todo 的请求
    response = client.post(
        "/todos/",
        json={"content": content},
        params={"note_id": actual_note_id} if actual_note_id is not None else {}
    )    
    # 验证状态码
    assert response.status_code == expected_status    
    # 根据状态码验证响应
    if expected_status == 201:
        todo = TodoResponse.model_validate(response.json())
        assert todo.content == content
        assert todo.user_id == mock_user.id
        assert todo.id is not None
        # 动态验证 note_id
        if expected_note_id == "dynamic":
            assert todo.note_id == actual_note_id
        else:
            assert todo.note_id == expected_note_id
    elif expected_status == 404:
        assert "Note with id 9999 not found" in response.text
        
        
# 测试获取某个 note 下的 todos
def test_get_todos_for_note(client: TestClient):
    # 创建 note
    note_response = client.post("/notes/", json={"title": "Test Note", "content": "Note content"})
    assert note_response.status_code == 201
    note = NoteResponse.model_validate(note_response.json())
    note_id = note.id

    # 创建两个关联 todo
    client.post("/todos/", json={"content": "Todo 1"}, params={"note_id": note_id})
    client.post("/todos/", json={"content": "Todo 2"}, params={"note_id": note_id})
    # 创建一个独立 todo
    client.post("/todos/", json={"content": "Independent Todo"})

    # 获取该 note 下的 todos
    response = client.get(f"/todos?note_id={note_id}")
    assert response.status_code == 200
    todos = [TodoResponse.model_validate(todo) for todo in response.json()]
    
    # 验证
    assert len(todos) == 2
    assert all(todo.note_id == note_id for todo in todos)
    assert {todo.content for todo in todos} == {"Todo 1", "Todo 2"}


# 测试获取所有 todos（无过滤）
def test_get_all_todos(client: TestClient):
    client.post("/todos/", json={"content": "Todo 1"})
    client.post("/todos/", json={"content": "Todo 2"})
    response = client.get("/todos/")
    assert response.status_code == 200
    todos = [TodoResponse.model_validate(todo) for todo in response.json()]
    assert len(todos) >= 2
    assert any(todo.content == "Todo 1" for todo in todos)


# 测试获取单个 todo
def test_get_todo_by_id(client: TestClient):
    create_response = client.post("/todos/", json={"content": "Test Todo"})
    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    todo = TodoResponse.model_validate(response.json())
    assert todo.id == todo_id
    assert todo.content == "Test Todo"


# 测试更新 todo
def test_update_todo(client: TestClient):
    create_response = client.post("/todos/", json={"content": "Old Todo"})
    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]
    response = client.patch(f"/todos/{todo_id}", json={"content": "New Todo"})
    assert response.status_code == 200
    updated_todo = TodoResponse.model_validate(response.json())
    assert updated_todo.id == todo_id
    assert updated_todo.content == "New Todo"


# 测试删除 todo
def test_delete_todo(client: TestClient):
    create_response = client.post("/todos/", json={"content": "Todo to delete"})
    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 204
    get_response = client.get(f"/todos/{todo_id}")
    assert get_response.status_code == 404

# 测试无效 note_id
def test_get_todos_with_invalid_note_id(client: TestClient):
    response = client.get("/todos?note_id=9999")
    assert response.status_code == 404

# 测试 search 过滤
def test_get_todos_by_search(client: TestClient):
    client.post("/todos/", json={"content": "Searchable Todo"})
    client.post("/todos/", json={"content": "Other Todo"})
    response = client.get("/todos?search=Searchable")
    assert response.status_code == 200
    todos = [TodoResponse.model_validate(todo) for todo in response.json()]
    assert len(todos) == 1
    assert todos[0].content == "Searchable Todo"
    
    
# 测试 status 过滤
def test_get_todos_by_status(client: TestClient):
    client.post("/todos/", json={"content": "Done Todo"})
    client.post("/todos/", json={"content": "Undone Todo"})
    client.patch("/todos/1", json={"is_completed": True})    
    response = client.get("/todos?status=finished")
    assert response.status_code == 200
    todos = [TodoResponse.model_validate(todo) for todo in response.json()]
    assert len(todos) == 1
    assert todos[0].content == "Done Todo"