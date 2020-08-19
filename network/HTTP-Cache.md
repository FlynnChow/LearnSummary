## Http缓存

### Expires

客户端head：告诉客户端在约定时间前，可以直接从缓存中获取资源，时间单位是格林标准时间

### Cache-Control

客户端head：优先级高于Expires，用来控制缓存策略

* max-age可以被缓存多少时间，单位second
* public 缓存可被任何缓存区缓存
* private 私有缓存，不能被代理服务器缓存
* no-cache 强制客户端发起请求，不代表不缓存，会向服务器检查资源是否更新，没有更新会响应304，让客户端继续从缓存读取。
* no-store 不缓存

### **Last-Modified**

服务器head：服务器返回，表示响应资源在服务器最后修改时间

### **If-Modified-Since**

客户端head：上次请求资源返回的Last-Modified，如果值没变服务器返回304，并且内容为空

## **Etag**

服务器head：服务器返回的标签，用来对比资源是否改变

## **If-None-Match**

客户端head：对比资源是否改变，没改变之间返回304