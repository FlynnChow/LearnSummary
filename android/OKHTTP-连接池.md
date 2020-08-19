## Http连接池

### 链路复用

connection实现类realConnection,代表的是一个真实的socket链路，一个realConnection代表着与服务端有一个真实的链路

```java
public final class ConnectInterceptor implements Interceptor {
  @Override public Response intercept(Chain chain) throws IOException {
    RealInterceptorChain realChain = (RealInterceptorChain) chain;
    Request request = realChain.request();
    StreamAllocation streamAllocation = realChain.streamAllocation();

    boolean doExtensiveHealthChecks = !request.method().equals("GET");
    //如果链接是http2会返回http2codec,否则返回http1codec
    //同时在方法中会调用findConnection复用链路或者新建一个real链接
    HttpCodec httpCodec = streamAllocation.newStream(client, chain, doExtensiveHealthChecks);
    RealConnection connection = streamAllocation.connection();

    return realChain.proceed(request, streamAllocation, httpCodec, connection);
  }
}
```

streamAllocation.findConnection()

从连接池中获取链接

 ```java
  private RealConnection findConnection(int connectTimeout, int readTimeout, int writeTimeout,
      int pingIntervalMillis, boolean connectionRetryEnabled) throws IOException {
    boolean foundPooledConnection = false;
    RealConnection result = null;
    Route selectedRoute = null;
    Connection releasedConnection;
    Socket toClose;
    synchronized (connectionPool) {
      if (released) throw new IllegalStateException("released");
      if (codec != null) throw new IllegalStateException("codec != null");
      if (canceled) throw new IOException("Canceled");
      releasedConnection = this.connection;
      toClose = releaseIfNoNewStreams();
      //先判断streamAllocation的realconnection是否为空，不为空则直接返回复用
      if (this.connection != null) {
        result = this.connection;
        releasedConnection = null;
      }
      if (!reportedAcquired) {
        releasedConnection = null;
      }

      if (result == null) {
        //尝试从连接池中获取链接
        Internal.instance.get(connectionPool, address, this, null);
        //如果获取到了链接，返回
        if (connection != null) {
          foundPooledConnection = true;
          result = connection;
          //否则选择获取路由
        } else {
          selectedRoute = route;
        }
      }
    }
    closeQuietly(toClose);

    if (releasedConnection != null) {
      eventListener.connectionReleased(call, releasedConnection);
    }
    if (foundPooledConnection) {
      eventListener.connectionAcquired(call, result);
    }
    //之前获取到链接就直接返回
    if (result != null) {
      return result;
    }

    boolean newRouteSelection = false;
    if (selectedRoute == null && (routeSelection == null || !routeSelection.hasNext())) {
      newRouteSelection = true;
      //获取路由配置
      routeSelection = routeSelector.next();
    }

    synchronized (connectionPool) {
      if (canceled) throw new IOException("Canceled");

      if (newRouteSelection) {
       	//配置了路由配置再从链接池中获取链接，如果获取到就取消遍历
        List<Route> routes = routeSelection.getAll();
        for (int i = 0, size = routes.size(); i < size; i++) {
          Route route = routes.get(i);
          Internal.instance.get(connectionPool, address, this, route);
          if (connection != null) {
            foundPooledConnection = true;
            result = connection;
            this.route = route;
            break;
          }
        }
      }
      
      //如果没有获取到链接，那么新建一个新链接
      if (!foundPooledConnection) {
        if (selectedRoute == null) {
          selectedRoute = routeSelection.next();
        }
        route = selectedRoute;
        refusedStreamCount = 0;
        result = new RealConnection(connectionPool, selectedRoute);
        acquire(result, false);
      }
    }

    //通过路由获取到链接就返回
    if (foundPooledConnection) {
      eventListener.connectionAcquired(call, result);
      return result;
    }


    //对新建的链接进行tcp和tls握手
    result.connect(connectTimeout, readTimeout, writeTimeout, pingIntervalMillis,
            connectionRetryEnabled, call, eventListener);
    routeDatabase().connected(result.route());

    Socket socket = null;
    synchronized (connectionPool) {
      reportedAcquired = true;
      //将新链接添加进链接池中
      Internal.instance.put(connectionPool, result);
      if (result.isMultiplexed()) {
        socket = Internal.instance.deduplicate(connectionPool, address, this);
        result = connection;
      }
    }
    //关闭socket
    closeQuietly(socket);

    eventListener.connectionAcquired(call, result);
    return result;
  }
 ```



尝试获取链路

对所有的链路进行遍历，如果有链路可以服用，直接返回，否则返回null

```
@Nullable RealConnection get(Address address, StreamAllocation streamAllocation, Route route) {
    assert (Thread.holdsLock(this));
    for (RealConnection connection : connections) {
      if (connection.isEligible(address, route)) {
        streamAllocation.acquire(connection, true);
        return connection;
      }
    }
    return null;
  }
```



isEligible

* 链接未达到负载上限
* 非host域必须相同
* 非http2hust域也要相同



### 链接清理

```java
private final Runnable cleanupRunnable = new Runnable() {
    @Override public void run() {
      while (true) {
        //清楚链路并返回下次清理时间，返回-1不清理并退出，返回0立即清理
        long waitNanos = cleanup(System.nanoTime());
        if (waitNanos == -1) return;
        if (waitNanos > 0) {
          long waitMillis = waitNanos / 1000000L;
          waitNanos -= (waitMillis * 1000000L);
          synchronized (ConnectionPool.this) {
            try {
              ConnectionPool.this.wait(waitMillis, (int) waitNanos);
            } catch (InterruptedException ignored) {
            }
          }
        }
      }
    }
  };
```



调用put方法时会把清理线程加入到线程池

```java
void put(RealConnection connection) {
    assert (Thread.holdsLock(this));
    if (!cleanupRunning) {
      cleanupRunning = true;
      executor.execute(cleanupRunnable);
    }
    connections.add(connection);
  }
```



#### cleanup

* 空闲链路数量大于5或者空闲超过5分钟，清楚链路，返回0
* 空闲链路小于5，返回链路剩余最小时间
* 没有空闲链路，但有工作链路，返回5分钟
* 没有任何链路返回-1

