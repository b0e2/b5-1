# Mini Redis

Python으로 구현한 CLI 기반 인메모리 키-값 저장소입니다. 체이닝 해시맵으로 키를 찾고, 이중 연결 리스트로 최근 사용 순서를 관리하며, 동적 배열 기반 최소 힙으로 만료 예약을 처리합니다. 별도 서버 없이 실행되며 종료하면 저장한 데이터는 사라집니다.

## 실행

Python 3.8 이상에서 저장소 루트에서 실행합니다.

```bash
python3 -m mini_redis
```

`exit` 또는 `quit`으로 종료합니다. 입력에 공백이 있는 값은 따옴표로 묶습니다.

```text
mini-redis> SET greeting "hello world"
OK
mini-redis> GET greeting
"hello world"
mini-redis> DEL greeting
(integer) 1
mini-redis> GET greeting
(nil)
```

## 명령

- 데이터: `SET key value`, `GET key`, `DEL key`, `EXISTS key`, `DBSIZE`, `KEYS`
- 메모리: `CONFIG SET maxmemory bytes`, `INFO memory`
- 만료: `EXPIRE key seconds`, `TTL key`
- 메시징: `SUBSCRIBE channel subscriber`, `PUBLISH channel message`, `POLL subscriber`

`maxmemory`의 단위는 바이트이며 0은 무제한입니다. `used_memory`는 키와 값의 UTF-8 바이트 길이 합계입니다. 새 항목 하나가 한도보다 크면 `SET`을 거절하고, 저장 후 전체 한도를 넘으면 가장 오래 사용하지 않은 키부터 제거합니다. 만료된 키는 저장소 명령을 실행할 때 정리합니다. `KEYS`는 패턴 없이 전체 키를 출력합니다.

단일 CLI에서 구독자를 이름으로 구분합니다. `SUBSCRIBE`는 채널의 구독자 수, `PUBLISH`는 전달된 구독자 수를 반환합니다. `POLL`은 해당 구독자에게 먼저 도착한 메시지를 채널·내용 순서로 반환하고 버퍼에서 제거합니다. 메시지 버퍼는 String 키·값의 `used_memory` 및 TTL과 별도로 관리합니다.

```text
SUBSCRIBE news alice
PUBLISH news "hello world"
POLL alice
```

## 트리

이진 트리 순회와 BST는 CLI 명령과 별도로 사용할 수 있습니다.

```python
from mini_redis.binary_tree import BinaryTree, BinaryTreeNode
from mini_redis.bst import BinarySearchTree

tree = BinaryTree(BinaryTreeNode("A", BinaryTreeNode("B"), BinaryTreeNode("C")))
tree.preorder()   # ["A", "B", "C"]
tree.level_order()  # ["A", "B", "C"]

bst = BinarySearchTree()
for value in (3, 1, 4, 2):
    bst.insert(value)
bst.inorder()  # [1, 2, 3, 4]
bst.delete(3)
```

## 테스트

```bash
python3 -m unittest discover -s tests -v
```

스택·큐·덱 문서는 `docs/STACK_QUEUE_DEQUE.md`에 있습니다.
