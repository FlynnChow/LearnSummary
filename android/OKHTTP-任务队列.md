## OKhttp任务队列

```java
public final class Dispatcher {

  //最大并发线程数
  private int maxRequests = 64;
  //统一域名下最大并发线程数
  private int maxRequestsPerHost = 5;
  private Runnable idleCallback;

  //调度器内部的线程池
  private ExecutorService executorService;

  //异步就绪队列
  private final Deque<AsyncCall> readyAsyncCalls = new ArrayDeque<>();

  //异步正在运行队列
  private final Deque<AsyncCall> runningAsyncCalls = new ArrayDeque<>();

  //同步正在运行队列
  private final Deque<RealCall> runningSyncCalls = new ArrayDeque<>();

  public Dispatcher(ExecutorService executorService) {
    this.executorService = executorService;
  }

  public Dispatcher() {
  }

  //第一个参数是最小并发线程数
  //这里设置0: 如果一直空闲线程池内线程会全部被销毁
  //空闲线程最大存活60s
  public synchronized ExecutorService executorService() {
    if (executorService == null) {
      executorService = new ThreadPoolExecutor(0, Integer.MAX_VALUE, 60, TimeUnit.SECONDS,
          new SynchronousQueue<Runnable>(), Util.threadFactory("OkHttp Dispatcher", false));
    }
    return executorService;
  }
  
  ...
}
```

### 同步请求：

* 将请求加入任务队列

* 执行任务

* 将任务移除任务队列

```java
synchronized void enqueue(AsyncCall call) {
    //正在运行的异步任务小于64，同一域名下小于5
  if (runningAsyncCalls.size() < maxRequests && runningCallsForHost(call) < maxRequestsPerHost) {
    //加入同步运行的队列
    runningAsyncCalls.add(call);
    //线程池执行线程逻辑
    executorService().execute(call);
  } else {
    //加入到同步就绪队列
    readyAsyncCalls.add(call);
  }
}
```



### 异步请求

```java
synchronized void enqueue(AsyncCall call) {
    //正在运行的异步任务小于64，同一域名下小于5
  if (runningAsyncCalls.size() < maxRequests && runningCallsForHost(call) < maxRequestsPerHost) {
    //加入异步运行的队列
    runningAsyncCalls.add(call);
    //线程池执行线程逻辑
    executorService().execute(call);
  } else {
    //加入到就绪队列
    readyAsyncCalls.add(call);
  }
}
```



 ```java
#AsyncCall#execute()

@Override protected void execute() {
  boolean signalledCallback = false;
  try {
      //执行网络请求。。
    Response response = getResponseWithInterceptorChain(forWebSocket);
    if (canceled) {
      signalledCallback = true;
      //在线程池中回调
      responseCallback.onFailure(RealCall.this, new IOException("Canceled"));
    } else {
      signalledCallback = true;
      responseCallback.onResponse(RealCall.this, response);
    }
  } catch (IOException e) {
    if (signalledCallback) {
      logger.log(Level.INFO, "Callback failure for " + toLoggableString(), e);
    } else {
      responseCallback.onFailure(RealCall.this, e);
    }
  } finally {
    //任务完成，移除队列 
    client.dispatcher().finished(this);
  }
}
 ```



```java
@Override protected void execute() {
  boolean signalledCallback = false;
  try {
      //执行网络请求。。
    Response response = getResponseWithInterceptorChain(forWebSocket);
    if (canceled) {
      signalledCallback = true;
      //在线程池中回调
      responseCallback.onFailure(RealCall.this, new IOException("Canceled"));
    } else {
      signalledCallback = true;
      responseCallback.onResponse(RealCall.this, response);
    }
  } catch (IOException e) {
    if (signalledCallback) {
      logger.log(Level.INFO, "Callback failure for " + toLoggableString(), e);
    } else {
      responseCallback.onFailure(RealCall.this, e);
    }
  } finally {
    //任务完成，移除队列 
    client.dispatcher().finished(this);
  }
}
```



如果有空闲的线程，那么会把调用promoteCalls()方法

```java
private <T> void finished(Deque<T> calls, T call, boolean promoteCalls) {
    int runningCallsCount;
    Runnable idleCallback;
    synchronized (this) {
      if (!calls.remove(call)) throw new AssertionError("Call wasn't in-flight!");
      if (promoteCalls) promoteCalls();
      runningCallsCount = runningCallsCount();
      idleCallback = this.idleCallback;
    }

    if (runningCallsCount == 0 && idleCallback != null) {
      idleCallback.run();
    }
  }
```



```
private void promoteCalls() {
    //需要满足当前任务数小于64，切就绪队列有任务
    if (runningAsyncCalls.size() >= maxRequests) return;
    if (readyAsyncCalls.isEmpty()) return;calls to promote.

    //遍历就绪队列，把满足的任务加入到异步队列中执行任务，当任务数大于64时return
    for (Iterator<AsyncCall> i = readyAsyncCalls.iterator(); i.hasNext(); ) {
      AsyncCall call = i.next();

      if (runningCallsForHost(call) < maxRequestsPerHost) {
        i.remove();
        runningAsyncCalls.add(call);
        executorService().execute(call);
      }

      if (runningAsyncCalls.size() >= maxRequests) return; // Reached max capacity.
    }
  }
```

