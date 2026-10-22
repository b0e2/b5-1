# Mini Redis

Python 표준 라이브러리로 만든 CLI 기반 인메모리 키-값 저장소입니다. String 명령과 메모리 한도, LRU 퇴출, TTL 만료, Pub/Sub 메시징을 지원합니다. 해시맵과 연결 리스트, 동적 배열, 최소 힙은 직접 구현했습니다.

- Python 3.8 이상
- 외부 패키지 설치 불필요
- 별도 서버나 데이터 파일 없이 현재 프로세스의 메모리에서 실행

## 실행

저장소 루트에서 실행합니다.

```bash
python3 -m mini_redis
```

공백이 있는 값은 따옴표로 묶습니다. `exit` 또는 `quit`으로 종료하며, 종료 후 데이터는 유지되지 않습니다.

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

- String: `SET key value`, `GET key`, `DEL key`, `EXISTS key`, `DBSIZE`, `KEYS`
- 메모리: `CONFIG SET maxmemory bytes`, `INFO memory`
- 만료: `EXPIRE key seconds`, `TTL key`
- 메시징: `SUBSCRIBE channel subscriber`, `PUBLISH channel message`, `POLL subscriber`

`KEYS`는 패턴 검색 없이 전체 키를 반환하며 출력 순서는 보장하지 않습니다. 이 CLI는 Redis 서버에 접속하는 클라이언트가 아니라 한 프로세스에서 동작하는 프로그램입니다.

## 저장과 만료

키는 체이닝 해시맵에서 찾고, 최근 사용 순서는 이중 연결 리스트로 관리합니다. `GET`과 성공한 `SET`은 해당 키를 최근 사용 위치로 옮깁니다.

`INFO memory`의 `used_memory`는 살아 있는 String 키와 값의 UTF-8 바이트 길이 합계입니다. `maxmemory`의 단위는 바이트이며 0은 무제한입니다. 새 항목 하나가 한도보다 크면 `SET`을 거절합니다. 저장 후 전체 한도를 넘으면 가장 오래 사용하지 않은 키부터 제거하고 `evicted_keys`를 올립니다. 한도를 낮추는 명령만으로는 제거하지 않고, 다음 `SET`에서 한도를 적용합니다.

TTL 예약은 최소 힙에 만료 시각 순으로 저장합니다. 별도 타이머가 아니라 String 저장소 명령이 들어올 때 기한이 지난 키를 정리합니다. `TTL`은 키가 없으면 `-2`, 만료 설정이 없으면 `-1`, 그 외에는 남은 초를 반환합니다.

```text
mini-redis> CONFIG SET maxmemory 12
OK
mini-redis> SET a one
OK
mini-redis> SET b two
OK
mini-redis> GET a
"one"
mini-redis> SET c three
OK
mini-redis> GET b
(nil)
mini-redis> INFO memory
used_memory:10
maxmemory:12
evicted_keys:1
```

## 메시징

`SUBSCRIBE`는 채널에 구독자 이름을 등록합니다. `PUBLISH`는 발행 시점의 구독자마다 메시지를 전달하고, `POLL`은 해당 구독자에게 가장 먼저 도착한 메시지 한 건을 꺼냅니다. 여러 채널의 메시지는 구독자별 우편함에 도착 순서대로 쌓입니다.

```text
mini-redis> SUBSCRIBE news alice
(integer) 1
mini-redis> PUBLISH news "hello world"
(integer) 1
mini-redis> POLL alice
1. "news"
2. "hello world"
```

메시지 우편함은 String 키의 `used_memory`, LRU, TTL과 별도로 관리합니다.

## 코드 구조

```text
.
├── mini_redis/
│   ├── __init__.py
│   ├── __main__.py           REPL 입력과 출력
│   ├── cli.py                명령 검증, 실행, 결과 형식
│   ├── store.py              String 저장, 메모리, LRU, TTL
│   ├── pubsub.py             채널 구독과 구독자별 우편함
│   └── structures/
│       ├── __init__.py
│       ├── linked_list.py    이중 연결 리스트
│       ├── hash_map.py       체이닝 해시맵
│       ├── dynamic_array.py  동적 배열
│       ├── min_heap.py       최소 힙
│       ├── binary_tree.py    이진 트리 순회
│       └── bst.py            이진 탐색 트리
├── tests/                   unittest 테스트
├── docs/
│   └── STACK_QUEUE_DEQUE.md 스택·큐·덱 설명
└── README.md
```

입력은 `__main__`에서 해석하고, `cli.execute()`가 명령을 처리해 `MiniRedis`에 전달합니다. `store.py`는 `structures/`의 자료구조를 사용하며, 트리 모듈은 CLI 명령과 별도로 사용할 수 있습니다.

```python
from mini_redis.structures.binary_tree import BinaryTree, BinaryTreeNode
from mini_redis.structures.bst import BinarySearchTree

tree = BinaryTree(BinaryTreeNode("A", BinaryTreeNode("B"), BinaryTreeNode("C")))
print(tree.preorder())  # ['A', 'B', 'C']

bst = BinarySearchTree()
for value in (3, 1, 4, 2):
    bst.insert(value)
print(bst.inorder())  # [1, 2, 3, 4]
```

## 테스트

```bash
python3 -m unittest discover -s tests -v
```
