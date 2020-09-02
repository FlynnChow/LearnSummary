## LinkedHashMap

#### 构造方法

initialCapacity：初始大小

loadFactor：扩充系数，初始0.75f

accessOrder：和LRU有有光，设置为true后，调用get方法，会讲entry移动到链表尾部

```java
public LinkedHashMap(int initialCapacity,
                         float loadFactor,
                         boolean accessOrder) {
        super(initialCapacity, loadFactor);
        this.accessOrder = accessOrder;
    }
```



#### Put

```java
final V putVal(int hash, K key, V value, boolean onlyIfAbsent,
               boolean evict) {
    Node<K,V>[] tab; Node<K,V> p; int n, i;
    if ((tab = table) == null || (n = tab.length) == 0)
      	//tab == null 或 tab长度为0，首次扩容
        n = (tab = resize()).length;
  
  	// n是2的n次方时，(n - 1) & hash = hash % 2，位运算效率较高，用于确定下标值
  	// 如果该下标为null，则可以直接存入
    if ((p = tab[i = (n - 1) & hash]) == null)
        tab[i] = newNode(hash, key, value, null);
    else {
        Node<K,V> e; K k;
      	//hash冲突解决，判断是否是要put的key：
      	//1.key的hash相等
      	//2.key == 相等
      	//3.key equlas 相等
        if (p.hash == hash &&
            ((k = p.key) == key || (key != null && key.equals(k))))
            e = p;
      	//发生hash冲突，如果是红黑树，[插入]
        else if (p instanceof TreeNode)
            e = ((TreeNode<K,V>)p).putTreeVal(this, tab, hash, key, value);
        else {//否则是链表[插入]
          	//[插入] 查询树或链表是否存在满足的key，如果不存在，进行插入
            for (int binCount = 0; ; ++binCount) {
                if ((e = p.next) == null) {
                    p.next = newNode(hash, key, value, null);
                    if (binCount >= TREEIFY_THRESHOLD - 1) // -1 for 1st
                        treeifyBin(tab, hash);
                    break;
                }
                if (e.hash == hash &&
                    ((k = e.key) == key || (key != null && key.equals(k))))
                    break;
                p = e;
            }
        }
      	//[key]否则在这里更新目标key对象的value值
        if (e != null) { // existing mapping for key
            V oldValue = e.value;
            if (!onlyIfAbsent || oldValue == null)
                e.value = value;
          	//LinkedHashMap重写：accessOrder = true，将节点放到链表尾部
            afterNodeAccess(e);
            return oldValue;
        }
    }
    ++modCount;
    if (++size > threshold)
        resize();
  	//LinkedHashMap重写了这个方法：LRU算法，删除最老的节点
    afterNodeInsertion(evict);
    return null;
}
```



LinkedHashMap 重写了newNode来新建节点

换成了LinkedHashMapEntry，主要加了before和after接口(双链表结构)

```
Node<K,V> newNode(int hash, K key, V value, Node<K,V> e) {
        LinkedHashMapEntry<K,V> p =
            new LinkedHashMapEntry<K,V>(hash, key, value, e);
        linkNodeLast(p);
        return p;
    }
```



linkNodeLast用于进行链表的插入操作，采用尾插法

```
 private void linkNodeLast(LinkedHashMapEntry<K,V> p) {
        LinkedHashMapEntry<K,V> last = tail;
        tail = p;
        if (last == null)
            head = p;
        else {
            p.before = last;
            last.after = p;
        }
    }
```



由linedHashMap实现afterNodeAccess，将节点放到链表尾部

```
public V get(Object key) {
        Node<K,V> e;
        if ((e = getNode(hash(key), key)) == null)
            return null;
        if (accessOrder)
            afterNodeAccess(e);
        return e.value;
    }
```



#### LRU算法的实现在于afterNodeInsertion

改方法再put最后调用，linkedhashmap重写了改方法

```
void afterNodeInsertion(boolean evict) { // possibly remove eldest
        LinkedHashMapEntry<K,V> first;
        if (evict && (first = head) != null && removeEldestEntry(first)) {
            K key = first.key; // first 指向的是头结点，即删除链表头的结点
            removeNode(hash(key), key, null, false, true);
        }
    }
```



removeEldestEntry确定map的size到达多少就删除最老的节点

```
 @Override
 protected boolean removeEldestEntry(Map.Entry<String, String> entry) {
      //当map的size 大于3的时候就删除表头结点
      return map.size() > 3;
 }
```

