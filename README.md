# Mini Redis

Python으로 구현하는 CLI 기반 인메모리 키-값 저장소입니다. 현재 REPL 진입점과 종료, 알 수 없는 명령 출력이 동작합니다.

## 실행

Python 3.8 이상에서 저장소 루트에서 실행합니다.

```bash
python3 -m mini_redis
```

`exit` 또는 `quit`으로 종료합니다.

## 테스트

```bash
python3 -m unittest discover -s tests -v
```

이중 연결 리스트, 체이닝 해시맵, 최소 힙 모듈을 포함합니다. CLI 저장소 명령은 이후 추가합니다. 스택·큐·덱 문서는 `docs/STACK_QUEUE_DEQUE.md`에 작성합니다.
