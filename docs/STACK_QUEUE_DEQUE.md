# 스택·큐·덱

세 구조는 데이터를 담는 방식보다 **어느 위치에서 넣고 꺼낼 수 있는지**로 구분한다. 아래 시간 복잡도는 원소 수를 `n`이라 할 때의 값이다.

## 스택 (Stack)

마지막에 넣은 원소를 먼저 꺼내는 LIFO(Last In, First Out) 구조다. `A`, `B`, `C`를 차례로 넣으면 꺼내는 순서는 `C`, `B`, `A`다.

- `push(x)`: 맨 위에 삽입, O(1). 동적 배열을 늘려야 하는 경우에는 O(n)이지만, 용량을 2배씩 늘리면 여러 번의 삽입에 대한 분할 상환 비용은 O(1)이다.
- `pop()`: 맨 위 원소를 꺼냄, O(1).
- `peek()`: 맨 위 원소를 제거하지 않고 확인, O(1).

동적 배열의 끝이나 연결 리스트의 머리를 스택의 맨 위로 삼을 수 있다. 깊이 우선 순회에서 나중에 방문할 노드를 보관하는 데 적합하다.

## 큐 (Queue)

먼저 넣은 원소를 먼저 꺼내는 FIFO(First In, First Out) 구조다. `A`, `B`, `C`를 차례로 넣으면 꺼내는 순서도 `A`, `B`, `C`다.

- `enqueue(x)`: 뒤에 삽입, O(1).
- `dequeue()`: 앞의 원소를 꺼냄, O(1).
- `front()`: 앞의 원소를 제거하지 않고 확인, O(1).

앞·뒤 노드를 관리하는 연결 리스트라면 위 비용을 달성할 수 있다. 현재 `DynamicArray`의 첫 원소를 `remove(0)`으로 꺼내면 나머지를 왼쪽으로 이동해야 하므로 O(n)이다. 배열로 O(1) 수준의 앞쪽 삭제를 구현하려면 시작 위치를 이동하는 원형 버퍼가 필요하다. 너비 우선 또는 트리 레벨 순회에서 같은 깊이의 노드를 순서대로 처리할 때 쓴다.

## 덱 (Deque)

앞과 뒤 양쪽에서 삽입·삭제할 수 있는 double-ended queue다. 한쪽에서만 넣고 꺼내면 스택처럼, 뒤에 넣고 앞에서 꺼내면 큐처럼 사용할 수 있다.

- `add_front(x)`, `add_back(x)`: 각 끝에 삽입, O(1).
- `remove_front()`, `remove_back()`: 각 끝에서 꺼냄, O(1).
- `peek_front()`, `peek_back()`: 각 끝의 원소 확인, O(1).

이 비용은 양끝 노드를 가진 이중 연결 리스트를 기준으로 한다. 현재 `DynamicArray`에서 앞쪽 삽입·삭제는 원소 이동 때문에 O(n)이다. 덱의 검색은 별도 색인 없이 O(n)이며, 노드를 이미 알고 있을 때만 연결 리스트의 중간 삭제·이동이 O(1)이다.

## Mini Redis에서의 사용

현재 `LinkedList`는 양끝 삽입·삭제와 알려진 노드의 이동을 지원한다. `MiniRedis`는 최근 접근한 키를 앞쪽으로 옮기고 메모리가 부족할 때 뒤쪽의 가장 오래 사용하지 않은 키를 제거한다. 이는 큐의 FIFO 삭제가 아니라 **접근 순서가 갱신되는 LRU**다.

이진 트리의 레벨 순회를 구현할 때는 큐가, 반복적인 깊이 우선 순회를 선택할 때는 스택이 자연스럽다. 향후 단일 CLI에서 구독자별로 아직 표시하지 않은 메시지를 모아 보여주기로 한다면 큐를 임시 전달 버퍼로 쓸 수 있다. 다만 이 문서는 Pub/Sub의 저장·전달 방식을 확정하거나 해당 기능을 구현하지 않는다.

## 참고 자료

- NIST, [stack](https://xlinux.nist.gov/dads/HTML/stack.html), [queue](https://xlinux.nist.gov/dads/HTML/queue.html), [deque](https://xlinux.nist.gov/dads/HTML/deque.html)
- Princeton COS 226, [Stacks and Queues Study Guide](https://www.cs.princeton.edu/courses/archive/spring23/cos226/lectures/study/13StacksAndQueues.html)
- Oregon State University, [Queues and Deques](https://web.engr.oregonstate.edu/~sinisa/courses/OSU/CS261/CS261_Textbook/Chapter07.pdf)
