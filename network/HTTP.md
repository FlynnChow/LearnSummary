## HTTP 0.9 - 2

HTTP 0.9 - 2 是基于TCP/IP通信协议的应用层协议

#### HTTP 0.9

```json
GET /index.html
```

* 只有一个命令*GET*

* 协议规定，服务器只能返回HTML格式的字符串

* 服务器发送完就关闭连接

#### HTTP 1.0

```json
HTTP/1.0 200 OK
Content-Type: text/plain
Content-Length: 137582
Expires: Thu, 05 Dec 1997 16:00:00 GMT
Last-Modified: Wed, 5 August 1996 15:55:28 GMT
Server: Apache 0.84


<html>
  <body>Hello World</body>
</html>
```

* 引入了POST和HEAD
* 除可以发送文字，还可以发送图像，视频，二进制文件
* 请求和回应，除了数据部分，还必须包括头信息，用来描述元数据

HTTP 1.0的缺点是建立一次连接只能发送一次数据，要想继续发送数据必须重新建立连接

##### 回应格式

**头信息**

第一行：协议版本+状态码+状态描述

头信息元数据



**数据部分**



**Content-type**

服务端告诉客户端返回的数据类型

```
Content-type: text/html;charset=utf-8
Content-type: text/plain
Content-type: image/png
Content-type: video/mp4
```



**Accept: */ ***

客户端声明自己可以接受的数据类型



**Content-Encoding**

服务端告诉客户端压缩类型



**Accept-Encoding**

客户端声明自己可以接受的压缩类型



#### HTTP1.1

* 引入了持久连接，确保TCP默认不关闭，可以被多个请求复用
  * 不用声明Connect: keep-alive
  * 客户端和服务器发现对方一段时间没有活动，会主动关闭连接
  * 客户端可以发送 Connect: close 要求服务器主动关闭连接
* 管道机制(pipelining) 在同一个TCP连接里，可以发送多个请求
  * 必须要使用Content-Length 声明本次回应的长度，超过长度的部分就是下一个回应
  * 服务器还是会按照顺序处理请求
* 分块发送，用流模式替代缓存模式，适合使用在一些耗时的动态操作来
  * 请求头包括  Transfer-Encoding: chunked 表明使用流模式



虽然能够处理多个回应，但所有回应都是按顺序进行，如果前面的回应特别慢，就会产生队头阻塞，影响整体效率



#### **SPDY协议**

Google为了解决HTTP1.1效率低下而自行研发的，最开始在Chrome上试用



#### **HTTP 2协议**

* 二进制编码
  * HTTP1.1: 头信息使用文本，数据可以使用文本或者二进制
  * HTTP2:必须全部使用二进制，并且统称为frame(帧）：头信息帧，数据帧
  * HTTP 2可以自定义帧
* Multiplexing 多工/多路复用
  * HTTP1.1: 回应通常要按照顺序
  * HTTP2: 可以同时发送多个回应，并且不用一一对应，如果处理一个请求，服务器发现非常耗时，就会发送已经处理好的部分，然后处理其他请求
  * 必须标记某个数据是哪个请求的。HTTP将每个请求或回应的数据包成为stream（流），并且为每个流定义一个唯一编号，规定客户端的编号必须是奇数，服务器必须是偶数
* Http1.0 如果需要取消请求必须关闭tcp连接，2中可以发送rst-stream帧来取消请求，不用关闭TCP连接
* 头信息技术：头信息压缩后在发送，并且客户端和服务器能够共同维护一个头信息表，所有字段都必须存入这个表中并生成一个索引号，以后就不用重新发送发送同样字段，只需发送索引号，提高了速度
* 引入是server push(推送) 机制，可以主动向客户端发送数据