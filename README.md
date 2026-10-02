# Mini Redis

Python으로 구현한 CLI 기반 인메모리 키-값 저장소입니다. 체이닝 해시맵, 이중 연결 리스트, 최소 힙을 사용합니다.

## 실행

Python 3.8 이상에서 저장소 루트에서 실행합니다.

```bash
python3 -m mini_redis
```

`exit` 또는 `quit`으로 종료합니다.

## 명령

- 데이터: `SET key value`, `GET key`, `DEL key`, `EXISTS key`, `DBSIZE`, `KEYS`
- 메모리: `CONFIG SET maxmemory bytes`, `INFO memory`
- 만료: `EXPIRE key seconds`, `TTL key`

`maxmemory`의 단위는 바이트이며 0은 무제한입니다. `used_memory`는 키와 값의 UTF-8 바이트 길이 합계입니다. `KEYS`는 패턴 없이 전체 키를 출력합니다.

## 테스트

```bash
python3 -m unittest discover -s tests -v
```

스택·큐·덱 문서는 `docs/STACK_QUEUE_DEQUE.md`에 작성합니다.
