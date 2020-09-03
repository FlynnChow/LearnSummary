### 简单叙述
Android消息机制主要由handler，looper，messagequeue，threadlocal等对象组成。

Android消息机制主要指的就是handler的运行机制，Android不允许在非主线程更新ui，ViewRootImpl有一个checkThread()方法会对线程进行检查，如果线程不是主线程，就会抛出异常。

为什么不允许子线程对UI操作？因为Android的UI是线程不安全的，如果采用锁机制，不仅ui设置变得复杂，效率也会低下，所以采用单线程模型来处ui，handler负责切换。


使用handler需要线程拥有looper，主线程在创建时就会创建looper，非主线程可以通过Looper.prepare创建。

#### 简单叙述运行机制
handler通过post把runnable投递到handler内部，或通过send发送一个消息，post内部会调用send，send最终会通过消息队列的enqueueMessage方法把消息加入队列中，looper就会通过消息队列的next获得消息，looper它会通过消息的target对象来分发消息，而looper是运行在创建handler的线程中的，所以最终就切换到handler所在的线程中了。

### ThreadLocal
ThreadLocal是一个数据存储类，作用域在线程上，不同的线程头不同的ThreadLocal，handler的looper就是存储在ThreadLocal中的。

ThreadLocal.valus是线程中专用来存储ThreadLocal的数据localvalus，不同的线程有不同的localvalus，它内部维护着一个Object类型的数组，就是用来存储数据的。
#### set
它通过调用ThreadLocal的valus方法，传入当前线程，获得当前线程的localvalus对象。

如果线程不存在localvalus就是调用方法新建一个并且初始化，然后再调用localvalus的put方法存储数据。

##### put
它所做的事情就是把数据存储在localvalus的数组中，如果localvalus的reference对象在数组索引是index，存储位置就是index+1.

#### get
它先通过线程获取localvalus，如果valus不为空，就获取ThreadLocal对象reference数组中索引的下一位对象，否则新建一个valus并初始化返回。
### 消息队列的运行机制
尽管它叫队列，但是它内部实现不是队列，而是一个单链表，方便插入删除。
#### enqueueMessage
它所做的操作就是单链表的插入操作，把消息队列插入内部的队列中

#### next
它的内部有一个无限循环的for，for内部有一个do while循环，在do while循环内部就负责遍历链表，如果有消息就退出循环，否则会一直阻塞在这里。

### Looper
looper通过Looper的prepare方法创建，也可以通过prepareMainLooper方法创建主线程looper,通过getMainLooper获得主线程looper, 消息队列在looper的消息队列中创建。

looper结束方法有quit和quitSafely前者直接退出，后者等消息都处理完再安全退出，通常子线程所以都任务都运行完了需要结束looper都循环

调用looper的loop方法开始循环，loop内部有一个无限循环，它会通过消息队列的next获取消息，如果没有消息会一直阻塞在那里，或者当next返回null就会退出循环(如果调用looper的结束方法，就会通知消息队列退出，单消息队列被被标记为退出状态它的next就会返回null)，当next返回消息就会调用handler的dispatchMessage来分发消息。

### Handler
创建handler时，若当前线程没有looper，会抛出异常。

使用handler时发送消息，最终只是在消息队列中插入一条消息，

#### dispatchMessage
它所做的是消息的分发，如果消息的callback不为空，就通过handlecallback方法处理消息，消息队列的handler指的就是post传入的runnable对象，接着就查看handelr的mcallback是否为空，不为空就调用mcallback的handlemessage，最后调用handler的handlemessage，也就是创建handler时的派生子类。

#### 同个activity多个handle发消息最后会谁收
谁发送的就谁收，发送消息的时候，消息会通过target绑定发送的handle，在发送的时候，在loop中通过msg.target来调用dispatchmessage()

#### loop死循环对UI线程不会产生阻塞
因为Android中无论是生命周期的回调，还是事物的分发，都需要通过主线程的handler进行转发，然后再由loop接收并且转发，最后再由的主线程的handler进行处理。

##### 如果一直没有消息阻塞，不会开销过大？
因为linux的一些机制，如果进程在一段时间内空闲，就会进入休眠状态，直到消息或者事物到达再重新唤醒线程。