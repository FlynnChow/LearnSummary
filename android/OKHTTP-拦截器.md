## OKhttp拦截器

RealCall的getResponseWithInterceptorChain发起网络链接

```java
Response getResponseWithInterceptorChain() throws IOException {
    // Build a full stack of interceptors.
    List<Interceptor> interceptors = new ArrayList<>();
    interceptors.addAll(client.interceptors()); //添加用户定义的拦截器
    interceptors.add(retryAndFollowUpInterceptor);//添加网络重试拦截器
    interceptors.add(new BridgeInterceptor(client.cookieJar()));//添加请求头拦截器
    interceptors.add(new CacheInterceptor(client.internalCache()));//添加缓存拦截器
    interceptors.add(new ConnectInterceptor(client));//添加链路拦截器
    if (!forWebSocket) {
      interceptors.addAll(client.networkInterceptors());
    }
    interceptors.add(new CallServerInterceptor(forWebSocket));//服务请求拦截器，发起真正的网络请求

  	//添加拦截器的引用和当前拦截器的索引
    Interceptor.Chain chain = new RealInterceptorChain(interceptors, null, null, null, 0,
        originalRequest, this, eventListener, client.connectTimeoutMillis(),
        client.readTimeoutMillis(), client.writeTimeoutMillis());

  	//执行下一个拦截器，会递归返回网络响应
    return chain.proceed(originalRequest);
  }
```



```java
public Response proceed(Request request, StreamAllocation streamAllocation, HttpCodec httpCodec,RealConnection connection) throws IOException {
    //创建下一个拦截器的chain
    RealInterceptorChain next = new RealInterceptorChain(interceptors, streamAllocation, httpCodec,connection, index + 1, request, call, eventListener, connectTimeout, readTimeout,writeTimeout);
    Interceptor interceptor = interceptors.get(index);
  	//执行当前chain的拦截逻辑，并传入下一个拦截器的chain
    Response response = interceptor.intercept(next);
    return response;
  }
```



```java
@Override public Response intercept(Chain chain) throws IOException {
    RealInterceptorChain realChain = (RealInterceptorChain) chain;
    //..
    //拦截逻辑
    //..
    
    //继续执行下一个拦截器chain的proceed方法，递归执行
    return realChain.proceed(request, streamAllocation, httpCodec, connection);
  }
```

* 在发起请求前对request进行处理

* 在一个拦截器链中实例化下一个拦截器链 #proceed()

* 在拦截器链中执行的拦截器方法 #proceed()->intercept()

* 在拦截器中执行相关的拦截逻辑，然后再使用下一个拦截器的proceed()方法，获得网络请求的response，并且执行下一拦截器的逻辑